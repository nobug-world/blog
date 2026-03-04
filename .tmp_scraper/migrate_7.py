import os
import json
import re
import urllib.parse
import urllib.request
import subprocess

url = 'https://nobug.world/blogs/25729/'
chapter_id = 'spring-di'
title = 'TDD实现Spring（DI容器）'

print(f"Processing chapter {chapter_id} from {url}...")

# 1. Scrape
subprocess.run(["node", "scrape.cjs", url])

frontmatter = f"""---
publishDate: 2024-08-21T00:00:00Z
title: '{title}'
excerpt: '本文介绍了如何使用 TDD 的方式实现一个简单的 Spring DI 容器，包含注入点的支持、组件的构造、依赖的选择以及生命周期控制。'
category: 'TDD'
tags:
  - TDD
metadata:
  canonical: {url}
---
"""

# 2. Process article.md
target_dir = f"../src/assets/images/{chapter_id}"
os.makedirs(target_dir, exist_ok=True)

with open("images.json", "r") as f:
    images = json.load(f)

with open("article.md", "r") as f:
    md = f.read()

# filter generic images like wechat
article_images = [img for img in images if "wechat" not in img.lower()]

for idx, img_url in enumerate(article_images):
    filename = img_url.split("/")[-1]
    local_path = os.path.join(target_dir, filename)
    
    if not os.path.exists(local_path):
        print(f"Downloading {img_url}...")
        try:
            req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(local_path, 'wb') as out_file:
                out_file.write(response.read())
        except Exception as e:
            print(f"Failed to download {img_url}: {e}")
        
    path_only = urllib.parse.urlparse(img_url).path
    md = md.replace(img_url, f"~/assets/images/{chapter_id}/{filename}")
    md = md.replace(path_only, f"~/assets/images/{chapter_id}/{filename}")

# Clean up Markdown (Header)
md_lines = md.split("\n")
start_idx = 0
for i, line in enumerate(md_lines):
    if line.startswith("# ") and "TDD" in line:
        start_idx = max(0, i - 1)
        break

# Try to find a good end marker, e.g. "WeChat"
end_idx = len(md_lines)
for i in range(start_idx, len(md_lines)):
    if "请我一杯咖啡吧" in md_lines[i] or "打赏" in md_lines[i] or "阅读原文" in md_lines[i] or "WeChat ![]" in md_lines[i]:
        end_idx = i
        while end_idx > 0 and not md_lines[end_idx - 1].strip():
            end_idx -= 1
        break

cleaned_md = "\n".join(md_lines[start_idx:end_idx])
# Remove the first H1 that duplicates the title
cleaned_md = re.sub(r'^# TDD实现Spring（DI容器）\n+.*本文字数.*阅读时长.*\n+', '', cleaned_md, flags=re.MULTILINE)

final_md = frontmatter + cleaned_md

with open(f"../src/data/post/{chapter_id}.md", "w") as f:
    f.write(final_md)

print(f"Migration for {chapter_id} completed successfully!")
