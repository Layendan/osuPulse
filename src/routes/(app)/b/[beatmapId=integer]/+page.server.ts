import type { PageServerLoad } from './$types';

import { client } from '$lib/server';
import { error } from '@sveltejs/kit';

export const load = (async ({ params, url }) => {
	const beatmapId = parseInt(params.beatmapId);

	let beatmap: Awaited<ReturnType<typeof client.beatmaps.getBeatmap>>;

	try {
		beatmap = await client.beatmaps.getBeatmap(beatmapId);
	} catch (e) {
		console.error(e);
		error(404, 'Beatmap not found');
	}

	if (beatmap.mode !== 'osu') {
		error(400, 'Incorrect gamemode');
	}

	if (beatmap.ranked !== 1) {
		error(400, 'Beatmap not ranked');
	}

	const mods = parseInt(url.searchParams.get('mods') ?? '0');

	if (isNaN(mods)) {
		error(400, 'Incorrect mods');
	}

	return { beatmap, mods };
}) satisfies PageServerLoad;
