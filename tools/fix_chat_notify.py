#!/usr/bin/env python3
"""Add /api/chat notification to chat widget across all pages.
Inserts a fetch() call in chatHandleSend so every user message
gets forwarded to email + Telegram, without changing the UX."""

import os
import glob

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

# The current chatHandleSend function (exact match)
OLD_SEND = """            function chatHandleSend() {
                var text = chatInput2.value.trim();
                if (!text) return;
                chatAddMsg(text, true);
                chatInput2.value = '';
                chatAddLoading();
                setTimeout(function() {
                    var loader = document.getElementById('chatLoader');
                    if (loader) loader.remove();
                    chatAddMsg(chatGetResponse(text), false);
                }, 800 + Math.random() * 600);
            }"""

# New version: same UX + background POST to /api/chat
NEW_SEND = """            function chatHandleSend() {
                var text = chatInput2.value.trim();
                if (!text) return;
                chatAddMsg(text, true);
                chatInput2.value = '';
                chatAddLoading();

                // Notify via email + Telegram (fire & forget)
                try {
                    fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: text,
                            page: window.location.pathname,
                            timestamp: new Date().toLocaleString('en-US', { timeZone: 'America/New_York' })
                        })
                    }).catch(function() {});
                } catch(e) {}

                setTimeout(function() {
                    var loader = document.getElementById('chatLoader');
                    if (loader) loader.remove();
                    chatAddMsg(chatGetResponse(text), false);
                }, 800 + Math.random() * 600);
            }"""


def main():
    # All blog posts
    files = sorted(glob.glob(os.path.join(BASE_DIR, 'blog', '*.html')))
    # Plus main pages
    files += [
        os.path.join(BASE_DIR, 'index.html'),
        os.path.join(BASE_DIR, 'cities.html'),
        os.path.join(BASE_DIR, 'tools', 'quote-calculator.html'),
    ]

    updated = 0
    for filepath in files:
        if not os.path.exists(filepath):
            continue
        basename = os.path.basename(filepath)

        with open(filepath, 'r') as f:
            content = f.read()

        if OLD_SEND not in content:
            # Check if already updated
            if '/api/chat' in content:
                print(f'  SKIP (already has /api/chat): {basename}')
            else:
                print(f'  SKIP (no match): {basename}')
            continue

        content = content.replace(OLD_SEND, NEW_SEND, 1)

        with open(filepath, 'w') as f:
            f.write(content)

        print(f'  OK: {basename}')
        updated += 1

    print(f'\nUpdated {updated} files')


if __name__ == '__main__':
    main()
