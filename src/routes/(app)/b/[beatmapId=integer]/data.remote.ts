import type { BeatmapNeighbor } from '$lib';

import { error } from '@sveltejs/kit';
import { query } from '$app/server';
import { EMBED_API_URL } from '$env/static/private';
import { boolean, integer, number, object, optional, pipe, toMinValue } from 'valibot';

type NeighborResponse = {
	skill_sum: number;
	neighbors: BeatmapNeighbor[];
};

export const getBeatmapNeighbors = query(
	object({
		beatmapId: pipe(number(), integer(), toMinValue(0)),
		mods: pipe(number(), integer(), toMinValue(0)),
		showNsfw: optional(boolean()),
		spotlightOnly: optional(boolean()),
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
		beatmapId,
		mods = 0,
		showNsfw,
		spotlightOnly,
		minStars,
		maxStars,
		minPp,
		maxPp,
		minHitLength,
		maxHitLength,
		excludedMods,
		includedMods
	}) => {
		const url = new URL(`${EMBED_API_URL}/similar_beatmaps/`);

		url.searchParams.set('beatmap_id', beatmapId.toString());
		url.searchParams.set('mods', mods.toString());
		url.searchParams.set('top_n', '50');
		if (showNsfw) url.searchParams.set('show_nsfw', showNsfw.toString());
		if (spotlightOnly) url.searchParams.set('spotlight_only', spotlightOnly.toString());
		if (minStars) url.searchParams.set('min_stars', minStars.toString());
		if (maxStars) url.searchParams.set('max_stars', maxStars.toString());
		if (minPp) url.searchParams.set('min_pp', minPp.toString());
		if (maxPp) url.searchParams.set('max_pp', maxPp.toString());
		if (minHitLength) url.searchParams.set('min_hit_length', minHitLength.toString());
		if (maxHitLength) url.searchParams.set('max_hit_length', maxHitLength.toString());
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
