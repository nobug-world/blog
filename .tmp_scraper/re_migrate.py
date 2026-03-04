import os
import json
import re
import urllib.parse
import urllib.request
import subprocess

configs = [
    (1, 'https://nobug.world/blogs/8383/', '第一章'),
    (2, 'https://nobug.world/blogs/45253/', '第二章'),
    (3, 'https://nobug.world/blogs/48316/', '第三章'),
    (4, 'https://nobug.world/blogs/53885/', '第四章'),
    (5, 'https://nobug.world/blogs/4291/', '第五章'),
    (6, 'https://nobug.world/blogs/22747/', '第六章'),
]

for chapter_id, url, chap_str in configs:
    print(f"Processing chapter {chapter_id} from {url}...")
    
    # Extract existing frontmatter from the existing unit-testing-X.md
    existing_file = f"../src/data/post/unit-testing-{chapter_id}.md"
    with open(existing_file, "r") as f:
        content = f.read()
    
    parts = content.split("---")
    if len(parts) >= 3:
        frontmatter_part = parts[1]
    else:
        print(f"Error parsing frontmatter for {existing_file}")
        continue

    preamble = """

> 译者声明：本译文仅作为学习的记录，不作为任务商业用途，如有侵权请告知我删除。  
> **本文禁止转载！**  
> 请支持原书正版：[https://www.manning.com/books/unit-testing](https://www.manning.com/books/unit-testing)

"""
    frontmatter = f"---{frontmatter_part}---{preamble}"

    # Scrape
    result = subprocess.run(["node", "scrape.cjs", url])
    if result.returncode != 0:
        print(f"Failed to scrape {url}")
        continue
    
    target_dir = f"../src/assets/images/unit-testing-{chapter_id}"
    os.makedirs(target_dir, exist_ok=True)

    with open("images.json", "r") as f:
        images = json.load(f)

    with open("article.md", "r") as f:
        md = f.read()

    article_images = [img for img in images if "image-" in img]

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
        md = md.replace(img_url, f"~/assets/images/unit-testing-{chapter_id}/{filename}")
        md = md.replace(path_only, f"~/assets/images/unit-testing-{chapter_id}/{filename}")

    # Clean up Markdown
    md_lines = md.split("\n")
    start_idx = 0
    for i, line in enumerate(md_lines):
        if line.startswith("# ") and chap_str in line:
            start_idx = max(0, i - 1)
            break

    end_idx = len(md_lines)   
    for i in range(start_idx, len(md_lines)):
        if "请我一杯咖啡吧" in md_lines[i] or "打赏" in md_lines[i] or "阅读原文" in md_lines[i]:
            end_idx = i
            while end_idx > 0 and not md_lines[end_idx - 1].strip():
                end_idx -= 1
            break

    cleaned_md = "\n".join(md_lines[start_idx:end_idx])
    final_md = frontmatter + cleaned_md
    
    with open(existing_file, "w") as f:
        f.write(final_md)

print("All migrations completed successfully.")
