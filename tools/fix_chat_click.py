"""Fix chat widget bug: option buttons close chat panel.

The bug: when a .chat-opt-btn is clicked, it removes itself from the DOM.
The click then bubbles to the document listener which checks
chatWidget2.contains(e.target) — but since the button is gone,
contains() returns false and the chat closes.

Fix: add e.stopPropagation() to the button click handler.
"""

import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The broken line (inside chatAddOptions):
OLD = "btn.addEventListener('click', function() {"
NEW = "btn.addEventListener('click', function(e) { e.stopPropagation();"

files = glob.glob(os.path.join(ROOT, 'blog', '*.html'))
files += [
    os.path.join(ROOT, 'index.html'),
    os.path.join(ROOT, 'cities.html'),
    os.path.join(ROOT, 'tools', 'quote-calculator.html'),
]

fixed = 0
for fpath in files:
    if not os.path.isfile(fpath):
        continue
    with open(fpath, 'r') as f:
        content = f.read()

    if OLD not in content:
        continue

    # Only replace the FIRST occurrence (inside chatAddOptions),
    # not the quick-btn listener which also uses addEventListener('click', function()
    # The option button one is specifically: btn.addEventListener('click', function() {
    # We need to be precise — find it within the chatAddOptions context
    new_content = content.replace(OLD, NEW, 1)  # Replace first occurrence only

    if new_content != content:
        with open(fpath, 'w') as f:
            f.write(new_content)
        fixed += 1
        print(f"Fixed: {os.path.basename(fpath)}")

print(f"\nDone: {fixed} files patched.")
