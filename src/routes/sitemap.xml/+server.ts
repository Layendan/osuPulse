import type { RequestHandler } from '@sveltejs/kit';

export const GET: RequestHandler = ({ setHeaders }) => {
	setHeaders({
		'Content-Type': 'application/xml'
	});

	const site = 'https://pulse.layendan.dev';

	const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
		<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
		<url>
		<loc>${site}</loc>
		<changefreq>daily</changefreq>
		<priority>1</priority>
		</url>
		</urlset>`;
	return new Response(sitemap);
};
