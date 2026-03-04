<details open>
<summary>目录</summary>

- [演示](#演示)
- [简而言之](#简而言之)
- [快速开始](#快速开始)
  - [项目结构](#项目结构)
  - [命令](#命令)
  - [配置](#配置)
  - [添加新文章并部署](#添加新文章并部署)

</details>

<br>

## 演示

📌 [https://astrowind.vercel.app/](https://astrowind.vercel.app/)

<br>


## 简而言之

```shell
npm create astro@latest -- --template arthelokyo/astrowind
```

## 快速开始

**AstroWind** 旨在让您快速使用 [Astro 5.0](https://astro.build/) + [Tailwind CSS](https://tailwindcss.com/) 创建网站。这是一个免费主题，专注于简单性、最佳实践和高性能。

仅使用极少量的原生 JavaScript 提供基本功能，以便每个开发人员决定使用哪个框架（React、Vue、Svelte、Solid JS...）以及如何实现目标。

在此版本中，模板支持 `output` 配置中的所有选项：`static`、`hybrid` 和 `server`，但博客仅在 `prerender = true` 时工作。我们正在开发下一个版本，旨在使其完全兼容 SSR。

### 项目结构

在 **AstroWind** 模板中，您将看到以下文件夹和文件：

```
/
├── public/
│   ├── _headers
│   └── robots.txt
├── src/
│   ├── assets/
│   │   ├── favicons/
│   │   ├── images/
│   │   └── styles/
│   │       └── tailwind.css
│   ├── components/
│   │   ├── blog/
│   │   ├── common/
│   │   ├── ui/
│   │   ├── widgets/
│   │   │   ├── Header.astro
│   │   │   └── ...
│   │   ├── CustomStyles.astro
│   │   ├── Favicons.astro
│   │   └── Logo.astro
│   ├── content/
│   │   ├── post/
│   │   │   ├── post-slug-1.md
│   │   │   ├── post-slug-2.mdx
│   │   │   └── ...
│   │   └-- config.ts
│   ├── layouts/
│   │   ├── Layout.astro
│   │   ├── MarkdownLayout.astro
│   │   └── PageLayout.astro
│   ├── pages/
│   │   ├── [...blog]/
│   │   │   ├── [category]/
│   │   │   ├── [tag]/
│   │   │   ├── [...page].astro
│   │   │   └── index.astro
│   │   ├── index.astro
│   │   ├── 404.astro
│   │   ├-- rss.xml.ts
│   │   └── ...
│   ├── utils/
│   ├── config.yaml
│   └── navigation.js
├── package.json
├── astro.config.ts
└── ...
```

Astro 在 `src/pages/` 目录中查找 `.astro` 或 `.md` 文件。每个页面都根据其文件名作为路由公开。

`src/components/` 没什么特别的，但我们喜欢把任何 Astro/React/Vue/Svelte/Preact 组件放在这里。

任何静态资源（如图像）如果不需要任何转换，可以放在 `public/` 目录中；如果是直接导入的，则放在 `assets/` 目录中。

[![在 CodeSandbox 上编辑 AstroWind](https://codesandbox.io/static/img/play-codesandbox.svg)](https://githubbox.com/arthelokyo/astrowind/tree/main) [![在 Gitpod 中打开](https://svgshare.com/i/xdi.svg)](https://gitpod.io/?on=gitpod#https://github.com/arthelokyo/astrowind) [![在 StackBlitz 中打开](https://developer.stackblitz.com/img/open_in_stackblitz.svg)](https://stackblitz.com/github/arthelokyo/astrowind)

> 🧑‍🚀 **经验丰富的宇航员？** 删除此文件 `README.md`。更新 `src/config.yaml` 和内容。玩得开心！

<br>

### 命令

所有命令都在项目的根目录下的终端中运行：

| 命令                | 操作                                               |
| :------------------ | :------------------------------------------------- |
| `npm install`       | 安装依赖项                                         |
| `npm run dev`       | 在 `localhost:4321` 启动本地开发服务器             |
| `npm run build`     | 构建您的生产站点到 `./dist/`                       |
| `npm run preview`   | 在部署之前本地预览您的构建                         |
| `npm run check`     | 检查您的项目是否存在错误                           |
| `npm run fix`       | 运行 Eslint 并使用 Prettier 格式化代码             |
| `npm run astro ...` | 运行 CLI 命令，如 `astro add`、`astro preview`     |

<br>

### 配置

基本配置文件：`./src/config.yaml`

```yaml
site:
  name: 'Example'
  site: 'https://example.com'
  base: '/' # 如果您需要部署到 Github Pages 等，请更改此项
  trailingSlash: false # 生成末尾带有或不带有 "/" 的永久链接

  googleSiteVerificationId: false # 或某个值，

# 默认 SEO 元数据
metadata:
  title:
    default: 'Example'
    template: '%s — Example'
  description: '这是 Example 网站的默认元描述'
  robots:
    index: true
    follow: true
  openGraph:
    site_name: 'Example'
    images:
      - url: '~/assets/images/default.png'
        width: 1200
        height: 628
    type: website
  twitter:
    handle: '@twitter_user'
    site: '@twitter_user'
    cardType: summary_large_image

i18n:
  language: en
  textDirection: ltr

apps:
  blog:
    isEnabled: true # 是否启用博客
    postsPerPage: 6 # 每页文章数

    post:
      isEnabled: true
      permalink: '/blog/%slug%' # 变量: %slug%, %year%, %month%, %day%, %hour%, %minute%, %second%, %category%
      robots:
        index: true

    list:
      isEnabled: true
      pathname: 'blog' # 博客主路径，您可以将其更改为 "articles" (/articles)
      robots:
        index: true

    category:
      isEnabled: true
      pathname: 'category' # 分类主路径 /category/some-category，您可以将其更改为 "group" (/group/some-category)
      robots:
        index: true

    tag:
      isEnabled: true
      pathname: 'tag' # 标签主路径 /tag/some-tag，您可以将其更改为 "topics" (/topics/some-category)
      robots:
        index: false

    isRelatedPostsEnabled: true # 是否在每篇文章下方显示相关文章小部件
    relatedPostsCount: 4 # 显示的相关文章数量

analytics:
  vendors:
    googleAnalytics:
      id: null # 或 "G-XXXXXXXXXX"

ui:
  theme: 'system' # 值: "system" | "light" | "dark" | "light:only" | "dark:only"
```

<br>

#### 自定义设计

要自定义字体系列、颜色或更多元素，请参考以下文件：

- `src/components/CustomStyles.astro`
- `src/assets/styles/tailwind.css`

### 添加新文章并部署

在使用 GitHub Pages 的自动化部署工作流后，添加新文章并发布非常简单：

**1. 创建文章文件**

所有的博客文章都存放在 **`src/data/post/`** 目录下（支持 `.md` 或 `.mdx` 格式）。创建一个新的文件（例如 `my-first-post.md`），并在开头添加 Frontmatter 元数据：

```markdown
---
publishDate: 2024-03-01T00:00:00Z
title: '我的新文章标题'
excerpt: '这是文章的摘要，会显示在博客列表中。'
image: '~/assets/images/default.png' # 可选：封面图
category: '随笔' # 可选：文章分类
tags:
  - astro
  - blog
---

这里是文章的正文内容...
```

**2. 提交并推送到 GitHub**

项目已经配置了 GitHub Actions（如 `.github/workflows/deploy.yaml`），只要将更改推送到代码仓库主分支（如 `master` 分支），GitHub Pages 就会自动触发构建和上线流程：

```shell
# 1. 暂存新文章（如果有多处修改可以根据需要添加）
git add src/data/post/my-first-post.md

# 2. 提交修改
git commit -m "blog: 添加了一篇新文章"

# 3. 推送到 GitHub
git push origin master
```

推送完成后，稍等片刻，GitHub Actions 会动执行部署工作流并完成网站更新，您的新文章即会自动在博客上发布。

<br>
