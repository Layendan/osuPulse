import type { BeatmapNeighbor } from '$lib';

import { error } from '@sveltejs/kit';
import { query } from '$app/server';
import { EMBED_API_URL } from '$env/static/private';
import { number, object } from 'valibot';

type NeighborResponse = {
	skill_sum: number;
	neighbors: BeatmapNeighbor[];
};

export const getBeatmapNeighbors = query(
	object({ beatmapId: number(), mods: number() }),
	async ({ beatmapId, mods = 0 }) => {
		const url = new URL(`http://${EMBED_API_URL}/similar_beatmaps/`);

		url.searchParams.set('beatmap_id', beatmapId.toString());
		url.searchParams.set('mods', mods.toString());
		url.searchParams.set('top_n', '50');

		const response = await fetch(url, {
			headers: {
				accept: 'application/json',
				'Content-Type': 'application/json'
			}
		});

		if (!response.ok) error(404, 'Not found');

		const neighbors: NeighborResponse = await response.json();

		return neighbors;
	}
);
