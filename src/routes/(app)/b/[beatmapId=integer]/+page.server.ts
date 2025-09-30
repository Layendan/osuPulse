import type { Beatmap } from 'osu-api-v2-js';
import type { PageServerLoad } from './$types';

import { api } from '$lib/server';
import { error } from '@sveltejs/kit';

export const load = (async ({ params, url }) => {
	const beatmapId = parseInt(params.beatmapId);

	let beatmap: Beatmap.Extended.WithFailtimesOwnersMaxcomboBeatmapset;

	try {
		beatmap = await api.getBeatmap(beatmapId);
	} catch (e) {
		console.error(e);
		error(404, 'Beatmap not found');
	}

	if (beatmap.mode !== 'osu') {
		error(400, 'Incorrect gamemode');
	}

	const mods = parseInt(url.searchParams.get('mods') ?? '0');

	if (isNaN(mods)) {
		error(400, 'Incorrect mods');
	}

	return { beatmap, mods };
}) satisfies PageServerLoad;
