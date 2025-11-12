import type { UserNeighbor } from '$lib';

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
		minStars: optional(pipe(number(), toMinValue(0))),
		maxStars: optional(pipe(number(), toMinValue(0))),
		minPp: optional(pipe(number(), toMinValue(0))),
		maxPp: optional(pipe(number(), toMinValue(0))),
		minHitLength: optional(pipe(number(), integer(), toMinValue(0))),
		maxHitLength: optional(pipe(number(), integer(), toMinValue(0))),
		minBpm: optional(pipe(number(), toMinValue(0))),
		maxBpm: optional(pipe(number(), toMinValue(0))),
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
		minBpm,
		maxBpm,
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
				min_bpm: minBpm,
				max_bpm: maxBpm,
				exclude_mods_filter: excludedMods,
				include_mods_filter: includedMods
			})
		});

		if (!response.ok) {
			console.error(response.status, await response.text());
			error(response.status, response.statusText);
		}

		const neighbors: NeighborResponse = await response.json();

		return neighbors;
	}
);
