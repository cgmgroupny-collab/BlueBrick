#!/usr/bin/env python3
"""
Fix broken JS syntax where floating CTA code was injected inside backToTop block.
"""

import os
import glob

BLOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'blog')

# The broken pattern (backToTop click handler missing ); and })
BROKEN = """            backToTop.addEventListener('click', () => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        // -- Floating side CTA --
        const floatingCta = document.getElementById('floatingCta');
        if (floatingCta) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 400) {
                    floatingCta.classList.add('visible');
                } else {
                    floatingCta.classList.remove('visible');
                }
            });
        });
        }"""

FIXED = """            backToTop.addEventListener('click', () => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }

        // -- Floating side CTA --
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


def main():
    blog_dir = os.path.abspath(BLOG_DIR)
    files = sorted(glob.glob(os.path.join(blog_dir, '*.html')))

    updated = 0
    still_broken = 0
    for f in files:
        basename = os.path.basename(f)
        if basename == 'index.html':
            continue

        with open(f, 'r') as fh:
            content = fh.read()

        if BROKEN in content:
            content = content.replace(BROKEN, FIXED)
            with open(f, 'w') as fh:
                fh.write(content)
            print(f'  FIXED: {basename}')
            updated += 1
        elif 'Floating side CTA' in content:
            # Check if it's already correct
            if FIXED in content:
                print(f'  OK: {basename}')
            else:
                print(f'  NEEDS MANUAL: {basename}')
                still_broken += 1
        else:
            print(f'  NO CTA: {basename}')

    print(f'\nFixed {updated} files, {still_broken} need manual review')


if __name__ == '__main__':
    main()
