// @ts-check

import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'astro/config';

import react from '@astrojs/react';
import markdoc from '@astrojs/markdoc';
import netlify from '@astrojs/netlify';

// https://astro.build/config
export default defineConfig({
    site: 'https://soultravelers3.com',
    output: 'static',
    integrations: [mdx(), sitemap(), react(), markdoc()],
    vite: {
        plugins: [tailwindcss()],
    },
});