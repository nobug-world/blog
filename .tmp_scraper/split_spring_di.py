import re
import os

filepath = '/home/jiajun/nobug-world-blog/src/data/post/spring-di.md'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# parse frontmatter
in_frontmatter = False
frontmatter = []
content_start = 0

for i, line in enumerate(lines):
    if line.strip() == '---':
        if not in_frontmatter:
            in_frontmatter = True
            frontmatter.append(line)
        else:
            frontmatter.append(line)
            content_start = i + 1
            break
    else:
        if in_frontmatter:
            frontmatter.append(line)

parts = [
    {
        "filename": "spring-di-1.md",
        "title_suffix": " (一) - 基础功能与实例构造",
        "start_headers": ["# [](#TDD-实现-DI-容器简介"],
        "end_header": "# [](#将依赖的检查提前到获取实例之前",
        "lines": []
    },
    {
        "filename": "spring-di-2.md",
        "title_suffix": " (二) - 依赖检查提取",
        "start_headers": ["# [](#将依赖的检查提前到获取实例之前"],
        "end_header": "# [](#Field-Injection",
        "lines": []
    },
    {
        "filename": "spring-di-3.md",
        "title_suffix": " (三) - 字段注入与方法注入",
        "start_headers": ["# [](#Field-Injection"],
        "end_header": "# [](#重构测试代码",
        "lines": []
    },
    {
        "filename": "spring-di-4.md",
        "title_suffix": " (四) - 代码与测试重构",
        "start_headers": ["# [](#重构测试代码"],
        "end_header": "# [](#增加新功能-支持注入Provider",
        "lines": []
    },
    {
        "filename": "spring-di-5.md",
        "title_suffix": " (五) - Provider 依赖注入",
        "start_headers": ["# [](#增加新功能-支持注入Provider"],
        "end_header": "# [](#Qualifier",
        "lines": []
    },
    {
        "filename": "spring-di-6.md",
        "title_suffix": " (六) - Qualifier 支持",
        "start_headers": ["# [](#Qualifier"],
        "end_header": "# [](#Singleton-生命周期管理",
        "lines": []
    },
    {
        "filename": "spring-di-7.md",
        "title_suffix": " (七) - 生命周期管理",
        "start_headers": ["# [](#Singleton-生命周期管理"],
        "end_header": None,
        "lines": []
    }
]

content = lines[content_start:]

current_part = 0
for line in content:
    if current_part < len(parts) - 1:
        if line.startswith(parts[current_part]["end_header"]):
            current_part += 1
            
    parts[current_part]["lines"].append(line)

fm_str = ''.join(frontmatter)
# We will inject the new titles.
import re

for part in parts:
    new_fm = fm_str
    # Replace title: '...' with title: '... (suffix)'
    new_fm = re.sub(r'(title:.*)([\'"])\n', r'\1' + part["title_suffix"] + r'\2\n', new_fm)
    
    with open('/home/jiajun/nobug-world-blog/src/data/post/' + part["filename"], 'w', encoding='utf-8') as f:
        f.write(new_fm)
        f.writelines(part["lines"])

os.remove(filepath)
print("Splitting completed successfully.")
