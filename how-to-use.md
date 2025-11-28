# 使用指南 (How To Use)

这份文档记录了您关于本项目的常见疑问和操作指南。

## 常见问题 (FAQ)

### Q: 我的新文章应该写在哪个位置？

**A:** 您的新文章应该创建在 **`src/data/post`** 目录下。

该目录下的文件将被自动识别为博客文章。支持的文件格式为 Markdown (`.md`) 或 MDX (`.mdx`)。

## 常用操作

### 1. 创建新文章

在 `src/data/post` 目录下创建一个新的 `.md` 或 `.mdx` 文件。

**示例文件名:** `my-first-post.md`

**文件内容示例 (Frontmatter):**

文章的开头必须包含 Frontmatter（元数据），格式如下：

```markdown
---
publishDate: 2024-01-01T00:00:00Z
title: '我的第一篇文章'
excerpt: '这是文章的摘要，会显示在列表中。'
image: '~/assets/images/post-image.jpg' # 可选，文章封面图
category: '随笔' # 可选，文章分类
tags: # 可选，文章标签
  - astro
  - tailwind css
  - blog
metadata:
  canonical: https://astrowind.vercel.app/astrowind-template-in-depth
---

这里是文章的正文内容...
```

### 2. 启动开发服务器

在终端中运行以下命令以启动本地预览：

```bash
npm run dev
```

启动后，访问 `http://localhost:4321` 即可查看网站。

### 3. 构建生产版本

当您准备发布网站时，运行以下命令生成静态文件：

```bash
npm run build
```

构建完成后，生成的文件将位于 `dist/` 目录下。

### 4. 预览生产构建

在部署前，您可以在本地预览构建后的效果：

```bash
npm run preview
```
