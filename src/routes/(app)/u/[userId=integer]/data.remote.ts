import type { UserNeighbor } from '$lib';

import { error } from '@sveltejs/kit';
import { query } from '$app/server';
import { EMBED_API_URL } from '$env/static/private';
import { number, object, optional } from 'valibot';

type NeighborResponse = {
	user_id: number;
	top_neighbors: UserNeighbor[];
};

export const getUserNeighbors = query(
	object({ userId: number(), excludedMods: optional(number()), includedMods: optional(number()) }),
	async ({ userId, excludedMods, includedMods }) => {
		const url = new URL(`${EMBED_API_URL}/user_top_neighbors/`);
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

		return neighbors;
	}
);
