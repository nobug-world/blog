# 使用指南 (How To Use)

这份文档记录了您关于本项目的常见疑问和操作指南。

## 常见问题 (FAQ)

### Q: 我的新文章应该写在哪个位置？

**A:** 您的新文章应该创建在 **`src/data/post`** 目录下。

该目录下的文件将被自动识别为博客文章。支持的文件格式为 Markdown (`.md`) 或 MDX (`.mdx`)。

### Q: `src/pages` 目录下的文件是生成的还是手动编写的？

**A:** `src/pages` 目录下的文件是 **手动编写的源代码**（或者来自模板）。

Astro 使用基于文件的路由系统。该目录下的每个文件都对应网站上的一个页面或路由：
- `src/pages/index.astro` -> 对应网站首页 `/`
- `src/pages/about.astro` -> 对应 `/about`
- `src/pages/[...blog]/` -> 这是一个动态路由目录，用于生成博客文章页面。

当你运行 `npm run build` 时，Astro 会读取这些源代码文件，并将它们**编译/生成**为最终的静态 HTML 文件，存放在 `dist/` 目录下（这个目录才是自动生成的）。

### Q: `src/pages/homes` 目录下的文件是做什么的？

**A:** 是的，正如您所猜测的，`src/pages/homes` 目录下包含了几种不同类型网站的**首页示例模板**。

该目录通常包含以下文件（具体取决于模板版本）：
- `saas.astro`: 适用于 SaaS 软件产品的首页。
- `startup.astro`: 适用于初创公司的首页。
- `mobile-app.astro`: 适用于移动应用推广的首页。
- `personal.astro`: 适用于个人作品集或简历的首页。

**如何使用这些示例？**
如果您喜欢其中某个示例（例如 `personal.astro`）的设计，您可以将其内容复制并覆盖到 **`src/pages/index.astro`** 文件中，这样您的网站主页就会变成那个样式。您可以直接在浏览器中访问 `/homes/personal` (例如 `http://localhost:4321/homes/personal`) 来预览它们的效果。

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

### 5. 创建草稿文章

如果您希望创建一篇草稿文章（不发布到网站上），请在文章的 Frontmatter 中添加 `draft: true`。

**示例:**

```markdown
---
title: '我的草稿文章'
draft: true
...
---
```

带有 `draft: true` 的文章将不会在网站上显示，也不会被构建到生产环境中。

### 6. 修改网站导航栏和页脚

网站的顶部导航栏（Header）和底部页脚（Footer）的内容由 **`src/navigation.ts`** 文件控制。

#### 文件作用

- **`headerData`**: 定义顶部导航栏的菜单链接和操作按钮。
- **`footerData`**: 定义底部页脚的链接列、社交媒体图标和版权信息。

#### 如何修改

打开 `src/navigation.ts` 文件，找到对应的数据结构进行修改。

**修改导航栏示例:**

```typescript
export const headerData = {
  links: [
    {
      text: '首页',
      href: '/',
    },
    {- **`footerData`**: 定义底部页脚的链接列、社交媒体图标和版权信息。

      text: '博客',
      href: '/blog',
    },
    // ... 添加更多链接
  ],
  actions: [{ text: 'Github', href: 'https://github.com/your-repo', target: '_blank' }],
};
```

**修改页脚示例:**

```typescript
export const footerData = {
  links: [
    // ... 页脚链接列
  ],
  socialLinks: [
    // 修改社交媒体链接
    { ariaLabel: 'X', icon: 'tabler:brand-x', href: 'https://twitter.com/your-handle' },
    { ariaLabel: 'Github', icon: 'tabler:brand-github', href: 'https://github.com/your-handle' },
  ],
  footNote: `
    Made by <a class="text-blue-600 underline dark:text-muted" href="https://your-website.com"> Your Name</a> · All rights reserved.
  `,
};
```

修改保存后，开发服务器会自动刷新，您可以立即看到更改效果。
