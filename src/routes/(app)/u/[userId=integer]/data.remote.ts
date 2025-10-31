import type { UserNeighbor } from '$lib';

import { api } from '$lib/server';
import { error } from '@sveltejs/kit';
import { query } from '$app/server';
import { EMBED_API_URL } from '$env/static/private';
import { boolean, integer, number, object, optional, pipe, toMinValue } from 'valibot';

type NeighborResponse = {
	user_id: number;
	top_neighbors: UserNeighbor[];
};

export const getUserNeighbors = query(
	object({
		userId: pipe(number(), integer(), toMinValue(0)),
		showNsfw: optional(boolean()),
		minStars: optional(pipe(number(), integer(), toMinValue(0))),
		maxStars: optional(pipe(number(), integer(), toMinValue(0))),
		minPp: optional(pipe(number(), integer(), toMinValue(0))),
		maxPp: optional(pipe(number(), integer(), toMinValue(0))),
		minHitLength: optional(pipe(number(), integer(), toMinValue(0))),
		maxHitLength: optional(pipe(number(), integer(), toMinValue(0))),
		excludedMods: optional(pipe(number(), integer(), toMinValue(0))),
		includedMods: optional(pipe(number(), integer(), toMinValue(0)))
	}),
	async ({
		userId,
		showNsfw,
		minStars,
		maxStars,
		minPp,
		maxPp,
		minHitLength,
		maxHitLength,
		excludedMods,
		includedMods
	}) => {
		const url = new URL(`${EMBED_API_URL}/user_top_neighbors/`);
		const response = await fetch(url, {
			method: 'POST',
			headers: {
				accept: 'application/json',
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				user_id: userId,
				show_nsfw: showNsfw,
				min_stars: minStars,
				max_stars: maxStars,
				min_pp: minPp,
				max_pp: maxPp,
				min_hit_length: minHitLength,
				max_hit_length: maxHitLength,
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
