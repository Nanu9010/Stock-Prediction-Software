import re, os

template_dir = r'c:\Users\karti\OneDrive\Desktop\Stock Prediction System\templates'
classes = set()
for root, dirs, files in os.walk(template_dir):
    for f in files:
        if f.endswith('.html'):
            with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
                for m in re.finditer(r'class="([^"]+)"', content):
                    for c in m.group(1).split():
                        if '{' not in c and '%' not in c:
                            classes.add(c)

sorted_classes = sorted(classes)
print(f'Total unique classes: {len(sorted_classes)}')
for c in sorted_classes:
    print(c)
