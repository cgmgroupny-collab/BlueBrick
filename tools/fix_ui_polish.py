#!/usr/bin/env python3
"""
UI polish:
1. Replace navbar logo <img> with SVG house icon
2. Remove contact FAB (duplicate chat-like button)
3. Add glow + rotating phrases to chat widget
"""

import os
import glob
import re

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

# SVG house icon matching Blue Brick logo shape
HOUSE_SVG = '''<svg width="28" height="28" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 4L4 18H9V34H31V18H36L20 4Z" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                    <rect x="12" y="22" width="16" height="12" rx="1" stroke="currentColor" stroke-width="2.5" fill="none"/>
                </svg>'''

# Old logo HTML patterns to replace
OLD_LOGO_PATTERNS = [
    # Blog posts: ../assets/images/
    r'<a href="/" class="tube-nav-logo" aria-label="Blue Brick Home">\s*<img src="\.\./assets/images/IMG_9670\.png" alt="Blue Brick">\s*</a>',
    # Root pages: assets/images/
    r'<a href="/" class="tube-nav-logo" aria-label="Blue Brick Home">\s*<img src="assets/images/IMG_9670\.png" alt="Blue Brick">\s*</a>',
]

NEW_LOGO_HTML = f'''<a href="/" class="tube-nav-logo" aria-label="Blue Brick Home">
                {HOUSE_SVG}
            </a>'''

# CSS to replace for the logo (remove img filter rules, add SVG color)
OLD_LOGO_CSS = """        .tube-nav-logo img {
            height: 36px;
            width: auto;
            filter: brightness(0) invert(1);
            transition: filter 0.3s;
        }

        .tube-nav.scrolled .tube-nav-logo img {
            filter: none;
        }"""

NEW_LOGO_CSS = """        .tube-nav-logo svg {
            width: 28px;
            height: 28px;
            color: rgba(255, 255, 255, 0.9);
            transition: color 0.3s;
        }

        .tube-nav.scrolled .tube-nav-logo svg {
            color: #001D4A;
        }"""

# Chat widget enhancements - glow + rotating phrases
CHAT_GLOW_CSS = """
        /* ============================================
           CHAT WIDGET ENHANCEMENTS
           ============================================ */
        .chat-toggle {
            animation: chatGlow 3s ease-in-out infinite;
        }

        @keyframes chatGlow {
            0%, 100% { box-shadow: 0 4px 20px rgba(0, 105, 146, 0.4), 0 0 0 0 rgba(0, 105, 146, 0); }
            50% { box-shadow: 0 4px 20px rgba(0, 105, 146, 0.4), 0 0 20px 8px rgba(236, 164, 0, 0.3); }
        }

        .chat-widget.open .chat-toggle {
            animation: none;
        }

        .chat-prompt {
            position: absolute;
            bottom: calc(100% + 8px);
            right: 0;
            background: #fff;
            color: #001D4A;
            font-size: 0.78rem;
            font-weight: 600;
            padding: 0.5rem 1rem;
            border-radius: 12px 12px 4px 12px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
            white-space: nowrap;
            pointer-events: none;
            opacity: 0;
            transform: translateY(4px);
            animation: promptFade 12s ease-in-out infinite;
            font-family: 'Manrope', system-ui, sans-serif;
        }

        .chat-prompt::after {
            content: '';
            position: absolute;
            bottom: -6px;
            right: 16px;
            width: 12px;
            height: 6px;
            background: #fff;
            clip-path: polygon(0 0, 100% 0, 100% 100%);
        }

        .chat-widget.open .chat-prompt {
            display: none;
        }

        @keyframes promptFade {
            0%, 8% { opacity: 0; transform: translateY(4px); }
            12%, 22% { opacity: 1; transform: translateY(0); }
            26%, 100% { opacity: 0; transform: translateY(4px); }
        }

        @media (max-width: 480px) {
            .chat-prompt { display: none; }
        }
"""

# Rotating phrases HTML - added after the chat toggle button
CHAT_PROMPT_HTML = '''<div class="chat-prompt" id="chatPrompt"></div>'''

# JS for rotating phrases
CHAT_PROMPT_JS = """
        // -- Rotating chat prompts --
        var chatPromptEl = document.getElementById('chatPrompt');
        if (chatPromptEl) {
            var chatPrompts = [
                'Need a cleaning quote? \\u2728',
                'Get an instant estimate!',
                'Ask us anything \\u{1F44B}',
                'What can we clean for you?',
                'Text or chat with us!'
            ];
            var promptIdx = 0;
            function rotateChatPrompt() {
                chatPromptEl.textContent = chatPrompts[promptIdx];
                promptIdx = (promptIdx + 1) % chatPrompts.length;
            }
            rotateChatPrompt();
            setInterval(rotateChatPrompt, 12000);
        }
"""


def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    original = content
    changes = []

    # 1. Replace navbar logo img with SVG house icon
    for pattern in OLD_LOGO_PATTERNS:
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, NEW_LOGO_HTML, content, flags=re.DOTALL)
            changes.append('logo→SVG')
            break

    # 1b. Replace logo CSS
    if OLD_LOGO_CSS in content:
        content = content.replace(OLD_LOGO_CSS, NEW_LOGO_CSS)
        changes.append('logo-css')

    # 2. Remove contact FAB HTML
    fab_pattern = r'\s*<!-- Floating Contact FAB -->.*?</div>\s*</div>\s*'
    # More specific pattern
    fab_html = re.search(
        r'\s*<!-- Floating Contact FAB -->\s*<div class="contact-fab".*?</button>\s*</div>',
        content,
        re.DOTALL
    )
    if fab_html:
        content = content[:fab_html.start()] + content[fab_html.end():]
        changes.append('remove-fab-html')

    # 2b. Remove contact FAB CSS
    fab_css = re.search(
        r'\s*/\* ={3,}\s*\n\s*FLOATING CONTACT FAB\s*\n\s*={3,} \*/.*?(?=\s*/\* ={3,}|\s*@media \(max-width: 640px\))',
        content,
        re.DOTALL
    )
    if fab_css:
        content = content[:fab_css.start()] + content[fab_css.end():]
        changes.append('remove-fab-css')

    # 2c. Remove contact FAB JS
    fab_js = re.search(
        r'\s*// -- Contact FAB toggle --.*?(?=\s*// -- Expandable Chat|\s*</script>)',
        content,
        re.DOTALL
    )
    if fab_js:
        content = content[:fab_js.start()] + '\n' + content[fab_js.end():]
        changes.append('remove-fab-js')

    # 2d. Remove FAB mobile adjustment CSS
    content = content.replace("            .contact-fab { bottom: 5rem !important; }\n", "")
    content = content.replace("            .contact-fab { bottom: 4.5rem !important; }\n", "")

    # 3. Add chat glow CSS (before the closing </style> or before BACK TO TOP section)
    if 'chatGlow' not in content:
        # Insert before BACK TO TOP or before </style>
        back_to_top_marker = '        /* ============================================\n           BACK TO TOP'
        if back_to_top_marker in content:
            idx = content.find(back_to_top_marker)
            content = content[:idx] + CHAT_GLOW_CSS + '\n' + content[idx:]
            changes.append('glow-css')
        else:
            style_close = content.rfind('</style>')
            if style_close != -1:
                content = content[:style_close] + CHAT_GLOW_CSS + '\n    </style>' + content[style_close + len('</style>'):]
                changes.append('glow-css')

    # 4. Add chat prompt HTML (after the chat toggle button)
    if 'chatPrompt' not in content:
        toggle_end = '</button>\n    </div>\n\n    <!-- Floating Contact FAB'
        if toggle_end not in content:
            # Try finding the chat widget closing
            toggle_marker = '''</button>
    </div>'''
            # Find the chat widget's closing button + div
            chat_end_pattern = r'(</button>\s*</div>)\s*\n\s*(?:<!-- Floating Contact FAB|<!-- Back to Top|<footer|\s*<div class="footer)'
            chat_end = re.search(chat_end_pattern, content)
            if chat_end:
                insert_pos = chat_end.start(1) + len(chat_end.group(1))
                # Actually insert the prompt div inside the chat-widget div, after the toggle
                pass

        # Simpler approach: find 'aria-label="Open chat">' and insert after the closing </button>
        toggle_close = 'aria-label="Open chat">'
        idx = content.find(toggle_close)
        if idx != -1:
            # Find the </button> after this
            btn_close_idx = content.find('</button>', idx)
            if btn_close_idx != -1:
                insert_at = btn_close_idx + len('</button>')
                content = content[:insert_at] + '\n        ' + CHAT_PROMPT_HTML + content[insert_at:]
                changes.append('prompt-html')

    # 5. Add rotating prompt JS before </script> of the widget script
    if 'rotateChatPrompt' not in content:
        # Find the last </script> before </body>
        body_close = content.rfind('</body>')
        if body_close != -1:
            last_script_close = content.rfind('</script>', 0, body_close)
            if last_script_close != -1:
                content = content[:last_script_close] + CHAT_PROMPT_JS + '\n    </script>' + content[last_script_close + len('</script>'):]
                changes.append('prompt-js')

    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f'  OK [{", ".join(changes)}]: {os.path.basename(filepath)}')
        return True
    else:
        print(f'  SKIP: {os.path.basename(filepath)}')
        return False


def main():
    # All blog posts
    files = sorted(glob.glob(os.path.join(BASE_DIR, 'blog', '*.html')))
    # Plus the 4 main pages
    files += [
        os.path.join(BASE_DIR, 'index.html'),
        os.path.join(BASE_DIR, 'cities.html'),
        os.path.join(BASE_DIR, 'tools', 'quote-calculator.html'),
    ]

    updated = 0
    for f in files:
        basename = os.path.basename(f)
        if basename == 'index.html' and 'blog' in f:
            # blog/index.html is included via glob
            pass
        if not os.path.exists(f):
            continue
        if process_file(f):
            updated += 1

    print(f'\nUpdated {updated} files')


if __name__ == '__main__':
    main()
