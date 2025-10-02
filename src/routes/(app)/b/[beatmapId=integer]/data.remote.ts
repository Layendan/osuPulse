import type { BeatmapNeighbor } from '$lib';

import { error } from '@sveltejs/kit';
import { query } from '$app/server';
import { EMBED_API_URL } from '$env/static/private';
import { number, object, optional } from 'valibot';

type NeighborResponse = {
	skill_sum: number;
	neighbors: BeatmapNeighbor[];
};

export const getBeatmapNeighbors = query(
	object({
		beatmapId: number(),
		mods: number(),
		excludedMods: optional(number()),
		includedMods: optional(number())
	}),
	async ({ beatmapId, mods = 0, excludedMods, includedMods }) => {
		const url = new URL(`${EMBED_API_URL}/similar_beatmaps/`);

		url.searchParams.set('beatmap_id', beatmapId.toString());
		url.searchParams.set('mods', mods.toString());
		url.searchParams.set('top_n', '50');
		if (excludedMods) url.searchParams.set('exclude_mods_filter', excludedMods.toString());
		if (includedMods) url.searchParams.set('include_mods_filter', includedMods.toString());

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
