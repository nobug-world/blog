const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const TurndownService = require("turndown");
const fs = require("fs");

const url = process.argv[2] || "https://nobug.world/blogs/22747/";

JSDOM.fromURL(url).then(dom => {
    const document = dom.window.document;

    const figures = document.querySelectorAll('figure.highlight');
    figures.forEach(figure => {
        const langClass = Array.from(figure.classList).find(c => c !== 'highlight') || '';
        const codeTd = figure.querySelector('td.code');

        let codeContent = '';
        if (codeTd) {
            const brs = codeTd.querySelectorAll('br');
            brs.forEach(br => {
                const textNode = document.createTextNode('\n');
                br.parentNode.replaceChild(textNode, br);
            });
            codeContent = codeTd.textContent || '';
        } else {
            const brs = figure.querySelectorAll('br');
            brs.forEach(br => {
                const textNode = document.createTextNode('\n');
                br.parentNode.replaceChild(textNode, br);
            });
            codeContent = figure.textContent || '';
        }

        // Remove empty lines at the start or end
        codeContent = codeContent.replace(/^\s*\n/, '').replace(/\n\s*$/, '');

        let lang = langClass;
        if (lang === 'c#') lang = 'csharp';

        // Use PRE so turndown preserves whitespace!
        const codeBlock = document.createElement('pre');
        codeBlock.className = 'custom-code-block';
        codeBlock.setAttribute('data-lang', lang);
        codeBlock.textContent = codeContent;
        figure.parentNode.replaceChild(codeBlock, figure);
    });

    const article = document.querySelector(".article-container") || document.querySelector("article") || document.body;

    const praiseSection = article.querySelector(".praise-box");
    if (praiseSection) praiseSection.remove();

    const turndownService = new TurndownService({
        headingStyle: 'atx',
        codeBlockStyle: 'fenced'
    });

    turndownService.addRule('customCodeBlock', {
        filter: function (node, options) {
            return node.nodeName === 'PRE' && node.className === 'custom-code-block';
        },
        replacement: function (content, node, options) {
            const lang = node.getAttribute('data-lang') || '';
            let code = node.textContent;

            let lines = code.split('\n');
            if (lines.length > 0 && lines[lines.length - 1].trim() === '') {
                lines.pop();
            }

            let numberedLines = lines.map((line, idx) => {
                return `${(idx + 1).toString().padEnd(2, ' ')}  ${line}`;
            });

            return `\n\n\`\`\`${lang}\n${numberedLines.join('\n')}\n\`\`\`\n\n`;
        }
    });

    const images = Array.from(article.querySelectorAll("img")).map(img => img.src);
    fs.writeFileSync("images.json", JSON.stringify(images, null, 2));

    const markdown = turndownService.turndown(article.innerHTML);
    fs.writeFileSync("article.md", markdown);
    console.log("Markdown saved to article.md for URL:", url);
}).catch(err => {
    console.error("Error scraping:", err);
});
