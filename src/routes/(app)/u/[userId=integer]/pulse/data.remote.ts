import type { UserNeighbor } from '$lib';

import { api } from '$lib/server';
import { error } from '@sveltejs/kit';
import { query } from '$app/server';
import { EMBED_API_URL } from '$env/static/private';
import { number, object, optional } from 'valibot';

type NeighborResponse = {
	user_id: number;
	top_neighbors: UserNeighbor[];
};

export const getUserPulseNeighbors = query(
	object({ userId: number(), excludedMods: optional(number()), includedMods: optional(number()) }),
	async ({ userId, excludedMods, includedMods }) => {
		const url = new URL(`${EMBED_API_URL}/user_pulse/`);
		const response = await fetch(url, {
			method: 'POST',
			headers: {
				accept: 'application/json',
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				user_id: userId,
				exclude_mods_filter: excludedMods,
				include_mods_filter: includedMods
			})
		});

		if (!response.ok) error(404, 'Not found');

		const neighbors: NeighborResponse = await response.json();

		const beatmapIds = neighbors.top_neighbors.reduce<{ [key: number]: number }>(
			(a, val) => ({
				...a,
				...val.Neighbors.reduce<{ [key: number]: number }>(
					(aN, valN) => ({ ...aN, [valN.beatmap_id]: valN.beatmap_id }),
					{}
				)
			}),
			{}
		);

		const beatmaps = await api.getBeatmaps(Object.values(beatmapIds));
		const beatmapDict = beatmaps.reduce<{ [key: number]: { title: string; version: string } }>(
			(a, val) => ({ ...a, [val.id]: { title: val.beatmapset.title, version: val.version } }),
			{}
		);

		const filledNeighbors = neighbors.top_neighbors.map((val) => ({
			...val,
			Neighbors: val.Neighbors.map((valN) => ({
				...valN,
				title: beatmapDict[valN.beatmap_id].title,
				version: beatmapDict[valN.beatmap_id].version
			}))
		}));

		return { top_neighbors: filledNeighbors, user_id: neighbors.user_id };
	}
);
