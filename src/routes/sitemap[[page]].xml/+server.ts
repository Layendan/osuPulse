import type { RequestHandler } from './$types';

import { error } from '@sveltejs/kit';
import { EMBED_API_URL } from '$env/static/private';
import * as sitemap from 'super-sitemap/sveltekit';

const ORIGIN = 'https://pulse.layendan.dev';
const MAX_PER_PAGE = 45_000;
const CACHE_MS = 6 * 60 * 60 * 1000;

let cache: { ids: string[]; fetchedAt: number } | undefined;
let inflight: Promise<string[]> | undefined;

async function getBeatmapIds(): Promise<string[]> {
	if (cache && Date.now() - cache.fetchedAt < CACHE_MS) return cache.ids;
	inflight ??= fetch(`${EMBED_API_URL}/beatmap_ids/`)
		.then(async (res) => {
			if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
			const ids = ((await res.json()) as number[]).map(String);
			cache = { ids, fetchedAt: Date.now() };
			return ids;
		})
		.finally(() => (inflight = undefined));
	try {
		return await inflight;
	} catch (e) {
		console.error('Failed to fetch beatmap ids for sitemap', e);
		if (cache) return cache.ids; // serve stale
		error(503, 'Sitemap temporarily unavailable');
	}
}

export const GET: RequestHandler = async ({ params }) =>
	sitemap.response({
		origin: ORIGIN,
		page: params.page,
		maxPerPage: MAX_PER_PAGE,
		excludeRoutePatterns: [/^\/u\//], // user pages: not enumerable
		paramValues: {
			'/b/[beatmapId=integer]': await getBeatmapIds()
		},
		defaultChangefreq: 'monthly'
	});
