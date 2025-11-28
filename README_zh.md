# 🚀 AstroWind

<img src="https://raw.githubusercontent.com/arthelokyo/.github/main/resources/astrowind/lighthouse-score.png" align="right"
     alt="AstroWind Lighthouse Score" width="100" height="358">

🌟 _2022、2023 和 2024 年最受欢迎（Star 和 Fork 数最多）的 Astro 主题_。 🌟

**AstroWind** 是一个免费开源的模板，用于使用 **[Astro 5.0](https://astro.build/) + [Tailwind CSS](https://tailwindcss.com/)** 制作您的网站。专为新项目设计，并充分考虑了网络最佳实践。

- ✅ **PageSpeed Insights** 报告中达到 **生产级** 分数。
- ✅ 集成 **Tailwind CSS**，支持 **深色模式** 和 **_RTL_**。
- ✅ **快速且 SEO 友好的博客**，具有自动 **RSS 订阅**、**MDX** 支持、**分类与标签**、**社交分享**等功能...
- ✅ **图像优化**（使用新的 **Astro Assets** 和 **Unpic** 通用图像 CDN）。
- ✅ 基于路由生成 **项目站点地图**。
- ✅ 用于社交媒体分享的 **Open Graph 标签**。
- ✅ 内置 **分析**，集成 Google Analytics 和 Splitbee。

<br>

![AstroWind 主题截图](https://raw.githubusercontent.com/arthelokyo/.github/main/resources/astrowind/screenshot-astrowind-1.0.png)

[![arthelokyo](https://custom-icon-badges.demolab.com/badge/made%20by%20-arthelokyo-556bf2?style=flat-square&logo=arthelokyo&logoColor=white&labelColor=101827)](https://github.com/arthelokyo)
[![License](https://img.shields.io/github/license/arthelokyo/astrowind?style=flat-square&color=dddddd&labelColor=000000)](https://github.com/arthelokyo/astrowind/blob/main/LICENSE.md)
[![Maintained](https://img.shields.io/badge/maintained%3F-yes-brightgreen.svg?style=flat-square)](https://github.com/arthelokyo)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat-square)](https://github.com/arthelokyo/astrowind#contributing)
[![Known Vulnerabilities](https://snyk.io/test/github/arthelokyo/astrowind/badge.svg?style=flat-square)](https://snyk.io/test/github/arthelokyo/astrowind)
[![Stars](https://img.shields.io/github/stars/arthelokyo/astrowind.svg?style=social&label=stars&maxAge=86400&color=ff69b4)](https://github.com/arthelokyo/astrowind)
[![Forks](https://img.shields.io/github/forks/arthelokyo/astrowind.svg?style=social&label=forks&maxAge=86400&color=ff69b4)](https://github.com/arthelokyo/astrowind)

<br>

<details open>
<summary>目录</summary>

- [演示](#演示)
- [即将推出：AstroWind 2.0 – 我们需要您的愿景！](#-即将推出astrowind-20--我们需要您的愿景)
- [简而言之](#简而言之)
- [快速开始](#快速开始)
  - [项目结构](#项目结构)
  - [命令](#命令)
  - [配置](#配置)
  - [部署](#部署)
- [常见问题](#常见问题)
- [相关项目](#相关项目)
- [贡献](#贡献)
- [致谢](#致谢)
- [许可证](#许可证)

</details>

<br>

## 演示

📌 [https://astrowind.vercel.app/](https://astrowind.vercel.app/)

<br>

## 🔔 即将推出：AstroWind 2.0 – 我们需要您的愿景！

我们正在开启 **AstroWind 2.0** 的激动人心的旅程，我们希望您能参与其中！我们目前正在迈出开发这个新版本的第一步，您的见解是非常宝贵的。加入讨论，分享您的反馈、想法和建议，帮助塑造 **AstroWind** 的未来。让我们一起让 **AstroWind 2.0** 变得更好！

[在我们的讨论中分享您的反馈！](https://github.com/arthelokyo/astrowind/discussions/392)

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

### 部署

#### 部署到生产环境（手动）

您可以使用以下命令创建优化的生产构建：

```shell
npm run build
```

现在，您的网站已准备好部署。所有生成的文件都位于 `dist` 文件夹中，您可以将该文件夹部署到您喜欢的任何托管服务。

#### 部署到 Netlify

将此存储库克隆到您自己的 GitHub 帐户并部署到 Netlify：

[![Netlify Deploy button](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/arthelokyo/astrowind)

#### 部署到 Vercel

将此存储库克隆到您自己的 GitHub 帐户并部署到 Vercel：

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Farthelokyo%2Fastrowind)

<br>

## 常见问题

- 为什么？
-
-

<br>

## 相关项目

- [TailNext](https://tailnext.vercel.app/) - 使用 Next.js 14 和 Tailwind CSS 以及新 App Router 的免费模板。
- [Qwind](https://qwind.pages.dev/) - 使用 Qwik + Tailwind CSS 制作网站的免费模板。

## 贡献

如果您有任何想法、建议或发现任何错误，请随时开启讨论、提出 issue 或创建 pull request。
这对我们所有人都非常有用，我们很乐意倾听并采取行动。

## 致谢

最初由 **Arthelokyo** 创建，并由 [贡献者](https://github.com/arthelokyo/astrowind/graphs/contributors) 社区维护。

## 许可证

**AstroWind** 根据 MIT 许可证授权 — 详情请参阅 [LICENSE](./LICENSE.md) 文件。
