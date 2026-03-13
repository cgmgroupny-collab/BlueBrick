#!/usr/bin/env python3
"""Fix missing <footer> wrapper in all blog posts.
The opening <footer> tag + .footer-bg div got stripped during a prior script run.
This adds them back before .footer-top so the dark background renders."""

import os
import glob

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

OLD = '        <div class="footer-top">'

NEW = '    <footer role="contentinfo">\n        <div class="footer-bg"></div>\n        <div class="footer-top">'


def main():
    files = sorted(glob.glob(os.path.join(BASE_DIR, 'blog', '*.html')))
    updated = 0

    for filepath in files:
        basename = os.path.basename(filepath)
        with open(filepath, 'r') as f:
            content = f.read()

        # Skip if already has opening <footer> tag (like blog/index.html)
        if '<footer' in content:
            print(f'  SKIP (has <footer>): {basename}')
            continue

        if OLD not in content:
            print(f'  SKIP (no footer-top): {basename}')
            continue

        content = content.replace(OLD, NEW, 1)

        with open(filepath, 'w') as f:
            f.write(content)

        print(f'  OK: {basename}')
        updated += 1

    print(f'\nUpdated {updated} files')


if __name__ == '__main__':
    main()
