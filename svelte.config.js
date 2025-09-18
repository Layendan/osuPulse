import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Consult https://svelte.dev/docs/kit/integrations
	// for more information about preprocessors
	preprocess: vitePreprocess(),
	kit: {
		adapter: adapter(),
		experimental: {
			remoteFunctions: true
		},
		csp: {
			// default-src 'self'; img-src 'self' https://*.ppy.sh; connect-src 'self' https://*.ppy.sh; frame-src 'none'; frame-ancestors 'none'; upgrade-insecure-requests; block-all-mixed-content;
			directives: {
				'default-src': ['self'],
				'img-src': ['self', 'https://*.ppy.sh'],
				'connect-src': ['self', 'https://*.ppy.sh'],
				'frame-src': ['none'],
				'frame-ancestors': ['none'],
				'upgrade-insecure-requests': true
			},
			mode: 'hash'
		}
	},
	compilerOptions: {
		experimental: {
			async: true
		}
	}
};

export default config;
