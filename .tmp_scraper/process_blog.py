import json
import os
import urllib.request
import re
import urllib.parse

target_dir = "../src/assets/images/unit-testing-6"
os.makedirs(target_dir, exist_ok=True)

with open("images.json", "r") as f:
    images = json.load(f)

with open("article.md", "r") as f:
    md = f.read()

# Filter out non-article images (wechatpay, etc.)
article_images = [img for img in images if "image-" in img]

for idx, img_url in enumerate(article_images):
    # Extract filename
    filename = img_url.split("/")[-1]
    local_path = os.path.join(target_dir, filename)
    
    # Download if not exists
    if not os.path.exists(local_path):
        print(f"Downloading {img_url}...")
        try:
            req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(local_path, 'wb') as out_file:
                out_file.write(response.read())
        except Exception as e:
            print(f"Failed to download {img_url}: {e}")
    else:
        print(f"Already downloaded {filename}")
        
    path_only = urllib.parse.urlparse(img_url).path
    
    md = md.replace(img_url, f"~/assets/images/unit-testing-6/{filename}")
    md = md.replace(path_only, f"~/assets/images/unit-testing-6/{filename}")

# Clean up Markdown (Header and Footer)
md_lines = md.split("\n")
start_idx = 0
for i, line in enumerate(md_lines):
    if line.startswith("# ") and "第六章" in line:
        start_idx = max(0, i - 1)
        break

end_idx = len(md_lines)   
for i in range(start_idx, len(md_lines)):
    if "请我一杯咖啡吧" in md_lines[i]:
        end_idx = i
        while end_idx > 0 and not md_lines[end_idx - 1].strip():
            end_idx -= 1
        break

cleaned_md = "\n".join(md_lines[start_idx:end_idx])

# Generate Frontmatter
frontmatter = """---
publishDate: 2024-09-13T00:00:00Z
title: '单元测试原则、实践与模式（六）'
excerpt: '本章内容涵盖比较单元测试的三种风格，理解函数式架构，过渡到函数式架构和基于输出的测试，以及了解函数式架构的缺点。'
category: '测试'
tags:
  - 单元测试
metadata:
  canonical: https://nobug.world/blogs/22747/
---

> 译者声明：本译文仅作为学习的记录，不作为任务商业用途，如有侵权请告知我删除。  
> **本文禁止转载！**  
> 请支持原书正版：[https://www.manning.com/books/unit-testing](https://www.manning.com/books/unit-testing)

"""

final_md = frontmatter + cleaned_md

with open("../src/data/post/unit-testing-6.mdx", "w") as f:
    f.write(final_md)

print("Migration completed successfully!")
