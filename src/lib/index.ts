import type { Beatmapset } from 'osu-api-v2-js';
import type { Mod } from 'osu-web.js';

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
};

export const ModsList = [ModsEnum.EZ, ModsEnum.HD, ModsEnum.HR, ModsEnum.DT, ModsEnum.HT];

const difficultyIncreaseMods = ['HD', 'HR', 'DT'];
export function isDifficultyIncrease(mod: Mod) {
	return difficultyIncreaseMods.includes(mod);
}
