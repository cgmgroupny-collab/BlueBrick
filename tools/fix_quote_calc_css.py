#!/usr/bin/env python3
"""Replace quote-calc-embed CSS across all blog posts with new compact design."""

import os
import glob
import re

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

OLD_CSS = """        .quote-calc-embed {
            background: linear-gradient(135deg, #001D4A 0%, #002a5c 50%, #001840 100%);
            border: 1px solid rgba(236, 164, 0, 0.2);
            border-radius: 14px;
            padding: 1.1rem 1.5rem;
            margin: 2.5rem 0;
            color: #ffffff !important;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1.25rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 24px rgba(0, 29, 74, 0.25), 0 0 0 1px rgba(236, 164, 0, 0.08);
        }

        .quote-calc-embed::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #ECA400, #f4be3a, #ECA400);
        }

        .quote-calc-embed::after {
            content: '';
            position: absolute;
            top: -40%;
            right: -5%;
            width: 180px;
            height: 180px;
            background: radial-gradient(circle, rgba(236, 164, 0, 0.06) 0%, transparent 70%);
            pointer-events: none;
        }

        .quote-calc-header {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            flex: 1;
            min-width: 0;
        }

        .quote-calc-header span {
            font-size: 1.75rem;
            line-height: 1;
            flex-shrink: 0;
            filter: drop-shadow(0 2px 4px rgba(236, 164, 0, 0.3));
        }

        .quote-calc-header strong {
            display: block;
            font-size: 1.05rem;
            color: #ffffff !important;
            font-weight: 700;
            letter-spacing: -0.01em;
            line-height: 1.3;
        }

        .quote-calc-header p {
            margin: 0.15rem 0 0 !important;
            font-size: 0.82rem;
            color: rgba(255, 255, 255, 0.75) !important;
            line-height: 1.35;
            letter-spacing: 0.01em;
        }

        .quote-calc-btn {
            background: linear-gradient(135deg, #ECA400, #d4940a);
            color: #001D4A !important;
            font-weight: 700;
            padding: 0.6rem 1.3rem;
            border-radius: 8px;
            font-size: 0.85rem;
            text-decoration: none !important;
            white-space: nowrap;
            flex-shrink: 0;
            letter-spacing: 0.01em;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 2px 8px rgba(236, 164, 0, 0.3);
            position: relative;
            z-index: 1;
        }

        .quote-calc-btn:hover {
            background: linear-gradient(135deg, #f4be3a, #ECA400);
            transform: translateY(-1px);
            box-shadow: 0 4px 16px rgba(236, 164, 0, 0.4);
            color: #001D4A !important;
        }

        @media (max-width: 520px) {
            .quote-calc-embed {
                flex-direction: column;
                text-align: center;
                padding: 1.2rem;
                gap: 1rem;
            }
            .quote-calc-header {
                flex-direction: column;
                gap: 0.5rem;
            }
            .quote-calc-btn {
                width: 100%;
                text-align: center;
                padding: 0.7rem 1.2rem;
            }
        }"""

NEW_CSS = """        .quote-calc-embed {
            background: linear-gradient(135deg, #001D4A 0%, #0a2a5c 60%, #001D4A 100%);
            border: 1px solid rgba(236, 164, 0, 0.15);
            border-radius: 14px;
            padding: 1.25rem 1.5rem;
            margin: 2rem 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1.25rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 2px 16px rgba(0, 29, 74, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.04);
        }

        .quote-calc-embed::before {
            content: '';
            position: absolute;
            top: -40%;
            right: -10%;
            width: 200px;
            height: 200px;
            background: radial-gradient(circle, rgba(236, 164, 0, 0.08) 0%, transparent 70%);
            pointer-events: none;
        }

        .quote-calc-header {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            flex: 1;
            min-width: 0;
        }

        .quote-calc-header > span {
            font-size: 1.5rem;
            flex-shrink: 0;
            line-height: 1;
        }

        .quote-calc-header strong {
            display: block;
            color: #ffffff;
            font-size: 1rem;
            font-weight: 700;
            letter-spacing: -0.01em;
            line-height: 1.3;
        }

        .quote-calc-header p {
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.8rem;
            margin: 0.15rem 0 0;
            line-height: 1.3;
            font-weight: 400;
        }

        .quote-calc-btn {
            display: inline-flex;
            align-items: center;
            background: #ECA400;
            color: #001D4A;
            font-size: 0.82rem;
            font-weight: 700;
            padding: 0.55rem 1.15rem;
            border-radius: 8px;
            text-decoration: none;
            white-space: nowrap;
            flex-shrink: 0;
            letter-spacing: 0.01em;
            transition: background 0.2s, box-shadow 0.2s, transform 0.15s;
            box-shadow: 0 2px 8px rgba(236, 164, 0, 0.25);
        }

        .quote-calc-btn:hover {
            background: #f5b31a;
            box-shadow: 0 4px 16px rgba(236, 164, 0, 0.35);
            transform: translateY(-1px);
        }

        @media (max-width: 540px) {
            .quote-calc-embed {
                flex-direction: column;
                text-align: center;
                padding: 1.25rem;
                gap: 1rem;
            }
            .quote-calc-header {
                flex-direction: column;
                gap: 0.5rem;
            }
            .quote-calc-btn {
                width: 100%;
                justify-content: center;
                padding: 0.65rem 1.25rem;
            }
        }"""


def main():
    files = sorted(glob.glob(os.path.join(BASE_DIR, 'blog', '*.html')))
    updated = 0

    for filepath in files:
        with open(filepath, 'r') as f:
            content = f.read()

        if OLD_CSS not in content:
            print(f'  SKIP: {os.path.basename(filepath)}')
            continue

        content = content.replace(OLD_CSS, NEW_CSS)

        with open(filepath, 'w') as f:
            f.write(content)

        print(f'  OK: {os.path.basename(filepath)}')
        updated += 1

    print(f'\nUpdated {updated} files')


if __name__ == '__main__':
    main()
