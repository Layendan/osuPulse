import type { User } from 'osu-api-v2-js';

import { api } from '$lib/server';
import { error, redirect } from '@sveltejs/kit';
import { form } from '$app/server';
import { Ruleset } from 'osu-api-v2-js';
import { nonEmpty, object, pipe, string, url } from 'valibot';

export const navigateToBeatmap = form(
	object({ beatmap: pipe(string(), url(), nonEmpty()) }),
	({ beatmap }) => {
		const parsedUrl = new URL(beatmap);

		if (parsedUrl.hostname !== 'osu.ppy.sh') {
			error(400, 'Invalid URL');
		}

		// Try "/beatmapsets/{setId}#osu/{beatmapId}" form first
		let beatmapId: number | null = null;

		// Case 1: /beatmapsets/{setId}#osu/{beatmapId}
		const beatmapsetMatch = parsedUrl.pathname.match(/^\/beatmapsets\/\d+$/);
		if (beatmapsetMatch) {
			const hashMatch = parsedUrl.hash.match(/^#osu\/(\d+)$/);
			if (hashMatch) {
				beatmapId = parseInt(hashMatch[1], 10);
			}
		}

		// Case 2: /b/{beatmapId}
		const bMatch = parsedUrl.pathname.match(/^\/b\/(\d+)$/);
		if (bMatch) {
			beatmapId = parseInt(bMatch[1], 10);
		}

		if (!beatmapId || isNaN(beatmapId)) {
			error(400, 'Invalid URL');
		}

		redirect(303, `/b/${beatmapId}`);
	}
);

export const navigateToUser = form(
	object({ user: pipe(string(), nonEmpty()) }),
	async ({ user }) => {
		let userData: User.Extended;
		try {
			userData = await api.getUser(user, Ruleset.osu);
		} catch (e) {
			console.error(e);
			error(500, 'Something went wrong');
		}

		redirect(303, `/u/${userData.id}`);
	}
);

export const navigateToUserPulse = form(
	object({ user: pipe(string(), nonEmpty()) }),
	async ({ user }) => {
		let userData;
		try {
			userData = await api.getUser(user, Ruleset.osu);
		} catch (e) {
			console.error(e);
			error(500, 'Something went wrong');
		}

		redirect(303, `/u/${userData.id}/pulse`);
	}
);
