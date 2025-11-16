import type { Beatmapset } from 'osu-api-v2-js';
import type { Mod } from 'osu-web.js';

import { interpolateRgb, scaleLinear } from 'd3';
import { ModsEnum } from 'osu-web.js';

export type FormError = { status: number; body: { message: string } };

export type NeighborInfo = {
	beatmap_id: number;
	beatmapset_id: number;
	mods: number;
	title: string;
	version: string;
	ranked: Beatmapset.RankStatus;
	distance: number;
};

export type UserNeighbor = {
	BeatmapId: number;
	BeatmapSetId: number;
	Mods: number;
	Ranked: Beatmapset.RankStatus;
	LastUpdated: Date;
	Count: number;
	MinDistance: number;
	MaxWeight: number;
	AvgAccuracy: number;
	Title: string;
	Version: string;
	Score: number;
	Stars: number;
	PP: number;
	Neighbors: NeighborInfo[];
};

export type BeatmapNeighbor = {
	BeatmapId: number;
	BeatmapSetId: number;
	Mods: number;
	Ranked: Beatmapset.RankStatus;
	LastUpdated: Date;
	Title: string;
	Version: string;
	Distance: number;
	AccMult: number;
	Stars: number;
	PP: number;
};

export type BeatmapSetSearch = {
	BeatmapId: number;
	BeatmapSetId: number;
	Title: string;
	Version: string;
	Ranked: number;
	Nsfw: boolean;
	Stars: number;
	PP: number;
};

export const ModsList = [ModsEnum.EZ, ModsEnum.HD, ModsEnum.HR, ModsEnum.DT, ModsEnum.HT];

const difficultyIncreaseMods = ['HD', 'HR', 'DT'];
export function isDifficultyIncrease(mod: Mod) {
	return difficultyIncreaseMods.includes(mod);
}

export function getDifficultyColors(stars: number) {
	const difficultyColourSpectrum = scaleLinear<string>()
		.domain([0.1, 1.25, 2, 2.5, 3.3, 4.2, 4.9, 5.8, 6.7, 7.7, 9])
		.clamp(true)
		.range([
			'#4290FB',
			'#4FC0FF',
			'#4FFFD5',
			'#7CFF4F',
			'#F6F05C',
			'#FF8068',
			'#FF4E6F',
			'#C645B8',
			'#6563DE',
			'#18158E',
			'#000000'
		])
		.interpolate(interpolateRgb.gamma(2.2));
	const foregroundColour = stars >= 6.5 ? 'hsl(45,100%,70%)' : 'hsl(200,10%,10%)';

	return {
		bg: difficultyColourSpectrum(stars),
		fg: foregroundColour
	};
}
