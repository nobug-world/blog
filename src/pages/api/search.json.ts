import { fetchPosts } from '~/utils/blog';
import { getPermalink } from '~/utils/permalinks';
import { findImage } from '~/utils/images';
import { APP_BLOG } from 'astrowind:config';

export const GET = async () => {
    const posts = await fetchPosts();

    const searchIndex = await Promise.all(posts.map(async (post) => {
        let imageUrl = '';
        if (post.image) {
            const image = await findImage(post.image);
            imageUrl = typeof image === 'string' ? image : (image as any)?.src || '';
        }

        return {
            title: post.title,
            excerpt: post.excerpt || '',
            content: post.rawContent?.replace(/[#*[\]()<>!_]/g, ' ') || '', // basic strip
            permalink: APP_BLOG?.post?.isEnabled ? getPermalink(post.permalink, 'post') : '',
            publishDate: post.publishDate,
            image: imageUrl,
            category: post.category,
            author: post.author,
            tags: post.tags,
        };
    }));

    return new Response(JSON.stringify(searchIndex), {
        status: 200,
        headers: {
            'Content-Type': 'application/json'
        }
    });
};
