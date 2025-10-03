import type { Mod } from 'osu-web.js';

import { ModsEnum } from 'osu-web.js';

export type FormError = { status: number; body: { message: string } };

export type NeighborInfo = {
	beatmap_id: number;
	beatmapset_id: number;
	mods: number;
	title: string;
	version: string;
	distance: number;
};

export type UserNeighbor = {
	BeatmapID: number;
	BeatmapsetID: number;
	Mods: number;
	Count: number;
	AvgDistance: number;
	AvgWeight: number;
	AvgAccuracy: number;
	Title: string;
	Version: string;
	ZDistance: number;
	Score: number;
	Neighbors: NeighborInfo[];
};

export type BeatmapNeighbor = {
	BeatmapID: number;
	BeatmapsetID: number;
	Mods: number;
	Title: string;
	Version: string;
	Distance: number;
	AccMult: number;
	Stamina: number;
	Streams: number;
	Aim: number;
	Accuracy: number;
	Precision: number;
	Reaction: number;
	Flashlight: number;
};

export const ModsList = [ModsEnum.EZ, ModsEnum.HD, ModsEnum.HR, ModsEnum.DT, ModsEnum.HT];

const difficultyIncreaseMods = ['HD', 'HR', 'DT'];
export function isDifficultyIncrease(mod: Mod) {
	return difficultyIncreaseMods.includes(mod);
}
