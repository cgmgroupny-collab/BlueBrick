#!/usr/bin/env python3
"""Add back-to-top JS to all blog posts."""

import os
import glob

BLOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'blog')

JS_BLOCK = """
        // -- Back to Top button --
        const backToTop = document.getElementById('backToTop');
        if (backToTop) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 600) {
                    backToTop.classList.add('visible');
                } else {
                    backToTop.classList.remove('visible');
                }
            });
            backToTop.addEventListener('click', () => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }
    """

MARKER = """        });
    </script>


    <script>
    document.querySelectorAll('.faq-question')"""

REPLACEMENT = """        });

        // -- Back to Top button --
        const backToTop = document.getElementById('backToTop');
        if (backToTop) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 600) {
                    backToTop.classList.add('visible');
                } else {
                    backToTop.classList.remove('visible');
                }
            });
            backToTop.addEventListener('click', () => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }
    </script>


    <script>
    document.querySelectorAll('.faq-question')"""

# For posts without FAQ
MARKER_NO_FAQ = """        });
    </script>

</body>"""

REPLACEMENT_NO_FAQ = """        });

        // -- Back to Top button --
        const backToTop = document.getElementById('backToTop');
        if (backToTop) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 600) {
                    backToTop.classList.add('visible');
                } else {
                    backToTop.classList.remove('visible');
                }
            });
            backToTop.addEventListener('click', () => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }
    </script>

</body>"""


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

        if 'Back to Top button' in content:
            print(f'  SKIP: {basename} (already has it)')
            continue

        original = content

        if MARKER in content:
            content = content.replace(MARKER, REPLACEMENT, 1)
        elif MARKER_NO_FAQ in content:
            content = content.replace(MARKER_NO_FAQ, REPLACEMENT_NO_FAQ, 1)

        if content != original:
            with open(f, 'w') as fh:
                fh.write(content)
            print(f'  OK: {basename}')
            updated += 1
        else:
            print(f'  MISS: {basename}')

    print(f'\nUpdated {updated} files')


if __name__ == '__main__':
    main()
