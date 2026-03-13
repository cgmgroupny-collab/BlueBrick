#!/usr/bin/env python3
"""
Fix: 1) Remove floating CTA JS remnants, 2) Add chat widget JS.
"""

import os
import re
import glob

BLOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'blog')

CHAT_JS = """
        // -- Expandable Chat Widget --
        const chatWidget = document.getElementById('chatWidget');
        const chatToggle = document.getElementById('chatToggle');
        const chatInput = document.getElementById('chatInput');
        const chatSendBtn = document.getElementById('chatSendBtn');
        const chatBody = document.getElementById('chatBody');

        if (chatToggle) {
            chatToggle.addEventListener('click', () => {
                chatWidget.classList.toggle('open');
                if (chatWidget.classList.contains('open')) {
                    setTimeout(() => chatInput.focus(), 300);
                }
            });

            const responses = {
                'quote': "Great! For a quick estimate, try our <a href='/tools/quote-calculator.html' target='_blank' style='color:#ECA400;font-weight:600'>Quote Calculator</a> or text us at <a href='sms:+17813305604' style='color:#ECA400;font-weight:600'>(781) 330-5604</a> with your address and sqft!",
                'services': "We offer: Deep Cleaning, Post-Construction Cleanup, Move-In/Move-Out, Luxury Residential, Commercial Cleaning, and Spring Cleaning. Which interests you?",
                'areas': "We serve 15 cities: Boston, Cambridge, Newton, Waltham, Brookline, Somerville, Brighton, Watertown, Allston, East Boston, South Boston, Lexington, Needham, Wellesley, and Weston!",
                'price': "Pricing depends on square footage and service type. Use our <a href='/tools/quote-calculator.html' target='_blank' style='color:#ECA400;font-weight:600'>Quote Calculator</a> for an instant estimate!",
                'book': "To book, text us at <a href='sms:+17813305604' style='color:#ECA400;font-weight:600'>(781) 330-5604</a> or email <a href='mailto:bluebrickmass@gmail.com' style='color:#ECA400;font-weight:600'>bluebrickmass@gmail.com</a>. We respond within 2 hours!",
                'default': "Thanks for your message! For the fastest response, text us at <a href='sms:+17813305604' style='color:#ECA400;font-weight:600'>(781) 330-5604</a> or email <a href='mailto:bluebrickmass@gmail.com' style='color:#ECA400;font-weight:600'>bluebrickmass@gmail.com</a>."
            };

            function addMessage(text, isSent) {
                const msg = document.createElement('div');
                msg.className = 'chat-msg' + (isSent ? ' sent' : '');
                msg.innerHTML = '<div class="chat-msg-avatar">' + (isSent ? 'You' : 'BB') + '</div><div class="chat-msg-bubble">' + text + '</div>';
                chatBody.appendChild(msg);
                chatBody.scrollTop = chatBody.scrollHeight;
            }

            function addLoading() {
                const loader = document.createElement('div');
                loader.className = 'chat-msg';
                loader.id = 'chatLoader';
                loader.innerHTML = '<div class="chat-msg-avatar">BB</div><div class="chat-loading"><span></span><span></span><span></span></div>';
                chatBody.appendChild(loader);
                chatBody.scrollTop = chatBody.scrollHeight;
            }

            function removeLoading() {
                const loader = document.getElementById('chatLoader');
                if (loader) loader.remove();
            }

            function getResponse(text) {
                const t = text.toLowerCase();
                if (t.includes('quote') || t.includes('estimate') || t.includes('cost') || t.includes('pricing')) return responses.quote;
                if (t.includes('service') || t.includes('offer') || t.includes('clean')) return responses.services;
                if (t.includes('area') || t.includes('city') || t.includes('cities') || t.includes('where') || t.includes('cover') || t.includes('location')) return responses.areas;
                if (t.includes('price') || t.includes('how much') || t.includes('rate')) return responses.price;
                if (t.includes('book') || t.includes('schedule') || t.includes('appointment')) return responses.book;
                return responses.default;
            }

            function handleSend() {
                const text = chatInput.value.trim();
                if (!text) return;
                addMessage(text, true);
                chatInput.value = '';
                addLoading();
                setTimeout(() => {
                    removeLoading();
                    addMessage(getResponse(text), false);
                }, 800 + Math.random() * 600);
            }

            chatSendBtn.addEventListener('click', handleSend);
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') { e.preventDefault(); handleSend(); }
            });

            document.querySelectorAll('.chat-quick-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const msg = btn.getAttribute('data-msg');
                    chatInput.value = msg;
                    handleSend();
                });
            });

            document.addEventListener('click', (e) => {
                if (!chatWidget.contains(e.target) && chatWidget.classList.contains('open')) {
                    chatWidget.classList.remove('open');
                }
            });
        }"""


def fix_file(content):
    """Clean up floating CTA remnants and add chat JS."""

    # Remove floating CTA JS remnants - various patterns
    # Pattern: "} else {\n.*floatingCta.*\n.*\n.*\n.*}"
    content = re.sub(
        r'\} else \{\s*\n\s*floatingCta\.classList\.remove\(\'visible\'\);\s*\n\s*\}\);\s*\n\s*\}',
        '}',
        content
    )

    # Also clean any standalone floatingCta references
    content = re.sub(
        r'\s*// -- Floating side CTA --.*?(?=\s*// -- )',
        '\n',
        content,
        flags=re.DOTALL
    )

    # Remove any leftover floatingCta variable declarations
    content = re.sub(
        r"\s*const floatingCta = document\.getElementById\('floatingCta'\);.*?(?=\s*// -- )",
        '\n        ',
        content,
        flags=re.DOTALL
    )

    # Add chat JS if not present
    if 'Expandable Chat Widget --' not in content:
        # Insert after Contact FAB JS block
        marker = """            document.addEventListener('click', (e) => {
                if (!contactFab.contains(e.target)) {
                    contactFab.classList.remove('open');
                }
            });
        }"""
        idx = content.find(marker)
        if idx != -1:
            end = idx + len(marker)
            content = content[:end] + CHAT_JS + content[end:]

    return content


def main():
    blog_dir = os.path.abspath(BLOG_DIR)
    files = sorted(glob.glob(os.path.join(blog_dir, '*.html')))

    updated = 0
    for f in files:
        basename = os.path.basename(f)
        if basename == 'index.html':
            continue

        with open(f, 'r') as fh:
            content = fh.read()

        original = content
        content = fix_file(content)

        if content != original:
            with open(f, 'w') as fh:
                fh.write(content)
            print(f'  OK: {basename}')
            updated += 1
        else:
            print(f'  SKIP: {basename}')

    print(f'\nUpdated {updated} files')


if __name__ == '__main__':
    main()
