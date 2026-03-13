#!/usr/bin/env python3
"""
Add a floating contact FAB (bottom-left) with call, text, email options.
Animated pulse, expands on click.
"""

import os
import glob

BLOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'blog')

CONTACT_CSS = """
        /* ============================================
           FLOATING CONTACT FAB
           ============================================ */
        .contact-fab {
            position: fixed;
            bottom: 2rem;
            left: 2rem;
            z-index: 998;
        }

        .contact-fab-toggle {
            width: 54px;
            height: 54px;
            border-radius: 50%;
            border: none;
            background: linear-gradient(135deg, #006992, #005577);
            color: #fff;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 20px rgba(0, 105, 146, 0.4);
            position: relative;
            z-index: 2;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .contact-fab-toggle::after {
            content: '';
            position: absolute;
            inset: -4px;
            border-radius: 50%;
            background: rgba(0, 105, 146, 0.25);
            animation: fabPulse 2s ease-in-out infinite;
            z-index: -1;
        }

        @keyframes fabPulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.25); opacity: 0; }
        }

        .contact-fab-toggle:hover {
            transform: scale(1.08);
            box-shadow: 0 6px 28px rgba(0, 105, 146, 0.5);
        }

        .contact-fab-toggle svg {
            width: 24px;
            height: 24px;
            fill: none;
            stroke: #fff;
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
            transition: transform 0.3s;
        }

        .contact-fab.open .contact-fab-toggle svg {
            transform: rotate(45deg);
        }

        .contact-fab.open .contact-fab-toggle {
            background: linear-gradient(135deg, #001D4A, #0a2a5c);
        }

        .contact-fab.open .contact-fab-toggle::after {
            animation: none;
            opacity: 0;
        }

        .contact-fab-menu {
            position: absolute;
            bottom: 68px;
            left: 0;
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
            opacity: 0;
            visibility: hidden;
            transform: translateY(12px) scale(0.9);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .contact-fab.open .contact-fab-menu {
            opacity: 1;
            visibility: visible;
            transform: translateY(0) scale(1);
        }

        .contact-fab-item {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            padding: 0.6rem 1rem 0.6rem 0.6rem;
            background: #fff;
            border-radius: 28px;
            text-decoration: none !important;
            box-shadow: 0 3px 16px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(0, 0, 0, 0.04);
            white-space: nowrap;
            transform: translateY(8px);
            opacity: 0;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .contact-fab.open .contact-fab-item {
            transform: translateY(0);
            opacity: 1;
        }

        .contact-fab.open .contact-fab-item:nth-child(1) { transition-delay: 0.05s; }
        .contact-fab.open .contact-fab-item:nth-child(2) { transition-delay: 0.1s; }
        .contact-fab.open .contact-fab-item:nth-child(3) { transition-delay: 0.15s; }

        .contact-fab-item:hover {
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 105, 146, 0.15);
            transform: translateX(4px);
        }

        .fab-icon {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }

        .fab-icon svg {
            width: 18px;
            height: 18px;
            fill: none;
            stroke: #fff;
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        .fab-icon-call { background: linear-gradient(135deg, #22c55e, #16a34a); }
        .fab-icon-text { background: linear-gradient(135deg, #006992, #005577); }
        .fab-icon-email { background: linear-gradient(135deg, #ECA400, #d4940a); }
        .fab-icon-email svg { stroke: #001D4A; }

        .fab-label {
            font-size: 0.82rem;
            font-weight: 600;
            color: #001D4A !important;
            line-height: 1.2;
        }

        .fab-label span {
            display: block;
            font-size: 0.7rem;
            font-weight: 400;
            color: #6b7280 !important;
            margin-top: 1px;
        }

        @media (max-width: 768px) {
            .contact-fab {
                bottom: 4.5rem;
                left: 1.25rem;
            }
            .contact-fab-toggle {
                width: 48px;
                height: 48px;
            }
            .contact-fab-toggle svg {
                width: 22px;
                height: 22px;
            }
            .contact-fab-menu {
                bottom: 60px;
            }
        }"""

CONTACT_HTML = """
    <!-- Floating Contact FAB -->
    <div class="contact-fab" id="contactFab">
        <div class="contact-fab-menu">
            <a href="tel:+17813305604" class="contact-fab-item">
                <div class="fab-icon fab-icon-call">
                    <svg viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                </div>
                <div class="fab-label">Call Now<span>(781) 330-5604</span></div>
            </a>
            <a href="sms:+17813305604" class="contact-fab-item">
                <div class="fab-icon fab-icon-text">
                    <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                </div>
                <div class="fab-label">Text Now<span>(781) 330-5604</span></div>
            </a>
            <a href="mailto:bluebrickmass@gmail.com" class="contact-fab-item">
                <div class="fab-icon fab-icon-email">
                    <svg viewBox="0 0 24 24"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                </div>
                <div class="fab-label">Email Us<span>bluebrickmass@gmail.com</span></div>
            </a>
        </div>
        <button class="contact-fab-toggle" aria-label="Contact us">
            <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        </button>
    </div>
"""

CONTACT_JS = """
        // -- Contact FAB toggle --
        const contactFab = document.getElementById('contactFab');
        if (contactFab) {
            const fabToggle = contactFab.querySelector('.contact-fab-toggle');
            fabToggle.addEventListener('click', () => {
                contactFab.classList.toggle('open');
            });
            document.addEventListener('click', (e) => {
                if (!contactFab.contains(e.target)) {
                    contactFab.classList.remove('open');
                }
            });
        }"""


def add_css(content):
    """Insert contact FAB CSS before FLOATING SIDE CTA section."""
    if 'FLOATING CONTACT FAB' in content:
        return content

    marker = '/* ============================================\n           FLOATING SIDE CTA'
    idx = content.find(marker)
    if idx != -1:
        content = content[:idx] + CONTACT_CSS + '\n\n        ' + content[idx:]
    return content


def add_html(content):
    """Insert contact FAB HTML before floating side CTA."""
    if 'contactFab' in content and '<div class="contact-fab"' in content:
        return content

    marker = '    <!-- Floating Side CTA -->'
    idx = content.find(marker)
    if idx != -1:
        content = content[:idx] + CONTACT_HTML + content[idx:]
    return content


def add_js(content):
    """Insert contact FAB JS after floating side CTA JS."""
    if 'Contact FAB toggle' in content:
        return content

    # Insert after the floating CTA block
    marker = """        // -- Floating side CTA --
        const floatingCta = document.getElementById('floatingCta');
        if (floatingCta) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 400) {
                    floatingCta.classList.add('visible');
                } else {
                    floatingCta.classList.remove('visible');
                }
            });
        }"""

    idx = content.find(marker)
    if idx != -1:
        end = idx + len(marker)
        content = content[:end] + CONTACT_JS + content[end:]
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
        content = add_css(content)
        content = add_html(content)
        content = add_js(content)

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
