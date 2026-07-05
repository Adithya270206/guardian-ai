import re
with open('src/app/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()
content = re.sub(r'id:\s*Date\.now\(\)\s*,', r'id: Date.now() + Math.random(),', content)
with open('src/app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
