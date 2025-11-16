import type { BeatmapSetSearch } from '$lib';
import type { APIError, Beatmap } from 'osu-api-v2-js';
import type { PageServerLoad } from './$types';

import { api } from '$lib/server';
import { error } from '@sveltejs/kit';
import { EMBED_API_URL } from '$env/static/private';

export const load = (async ({ params, url }) => {
	const beatmapId = parseInt(params.beatmapId);

	let beatmap: Beatmap.Extended.WithFailtimesOwnersMaxcomboBeatmapset;

	try {
		beatmap = await api.getBeatmap(beatmapId);
	} catch (e) {
		const errorVar = e as APIError;
		error(errorVar.status_code ?? 500, errorVar.message);
	}

	if (beatmap.mode !== 'osu') {
		error(400, 'Incorrect gamemode');
	}

	const mods = parseInt(url.searchParams.get('mods') ?? '0');

	if (isNaN(mods)) {
		error(400, 'Incorrect mods');
	}

	const apiUrl = new URL(`${EMBED_API_URL}/get_difficulties/`);
	apiUrl.searchParams.set('beatmapset_id', beatmap.beatmapset_id.toString());

	const response = await fetch(apiUrl, {
		headers: {
			accept: 'application/json',
			'Content-Type': 'application/json'
		}
	});

	if (!response.ok) {
		console.error(response.status, await response.text());
		error(response.status, response.statusText);
	}

	const difficulties: BeatmapSetSearch[] = await response.json();

	return { beatmap, difficulties, mods };
}) satisfies PageServerLoad;
