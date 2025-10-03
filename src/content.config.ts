import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
	// Load Markdown and MDX files in the `src/content/blog/` directory, excluding drafts
	loader: glob({ base: './src/content/blog', pattern: '**/*.{md,mdx}', ignore: ['**/_drafts/**'] }),
	// Type-check frontmatter using a schema
	schema: ({ image }) =>
		z.object({
			title: z.string(),
			description: z.string().optional(), // Make optional since many posts don't have it
			// Support both date formats for WordPress imports and Astro templates
			date: z.coerce.date().optional(),
			pubDate: z.coerce.date().optional(),
			updatedDate: z.coerce.date().optional(),
			heroImage: image().optional(),
			// WordPress-specific fields
			categories: z.array(z.string()).optional(),
			tags: z.array(z.string()).optional(),
			excerpt: z.string().optional(),
			draft: z.boolean().optional(),
		}).refine(data => data.date || data.pubDate, {
			message: "Either 'date' or 'pubDate' is required",
			path: ["date", "pubDate"]
		}),
});

const pages = defineCollection({
	// Load Markdown and MDX files in the `src/content/pages/` directory, excluding drafts
	loader: glob({ base: './src/content/pages', pattern: '**/*.{md,mdx}', ignore: ['**/_drafts/**'] }),
	// Type-check frontmatter using a schema
	schema: ({ image }) =>
		z.object({
			title: z.string().optional(), // Some pages may not have titles yet
			description: z.string().optional(),
			date: z.coerce.date().optional(),
			pubDate: z.coerce.date().optional(),
			updatedDate: z.coerce.date().optional(),
			heroImage: image().optional(),
			draft: z.boolean().optional(),
			// Page-specific fields
			slug: z.string().optional(),
			template: z.string().optional(),
		}),
});

const custom = defineCollection({
	// Load custom content like font configurations
	loader: glob({ base: './src/content/custom', pattern: '**/*.{md,mdx}' }),
	schema: z.object({
		title: z.string().optional(),
		date: z.coerce.date().optional(),
		// Allow any additional properties for custom content
	}).passthrough(),
});

const posts = defineCollection({
	// Load Keystatic-managed posts in the `src/content/posts/` directory
	loader: glob({ base: './src/content/posts', pattern: '**/*.{md,mdx,mdoc}' }),
	schema: ({ image }) =>
		z.object({
			title: z.string(),
			description: z.string().optional(),
			date: z.coerce.date().optional(),
			pubDate: z.coerce.date().optional(),
			updatedDate: z.coerce.date().optional(),
			heroImage: image().optional(),
			categories: z.array(z.string()).optional(),
			tags: z.array(z.string()).optional(),
			excerpt: z.string().optional(),
			draft: z.boolean().optional(),
		}),
});

export const collections = { blog, pages, custom, posts };
