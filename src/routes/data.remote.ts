import type { User } from 'osu-api-v2-js';

import { api } from '$lib/server';
import { error, redirect } from '@sveltejs/kit';
import { form } from '$app/server';
import { Ruleset } from 'osu-api-v2-js';
import { nonEmpty, object, pipe, string, url } from 'valibot';

export const navigateToBeatmap = form(
	object({ beatmap: pipe(string(), url(), nonEmpty()) }),
	({ beatmap }) => {
		const parsedUrl = new URL(beatmap.trim());

		if (parsedUrl.hostname !== 'osu.ppy.sh') {
			error(400, 'Invalid URL');
		}

		// Define URLPatterns for the two cases
		const pattern1 = new URLPattern({
			hostname: 'osu.ppy.sh',
			pathname: '/beatmapsets/:setId',
			hash: 'osu/:beatmapId'
		});

		const pattern2 = new URLPattern({
			hostname: 'osu.ppy.sh',
			pathname: '/b/:beatmapId'
		});

		let beatmapId: number | null = null;

		// Try matching first pattern: /beatmapsets/{setId}#osu/{beatmapId}
		const match1 = pattern1.exec(parsedUrl.href);
		if (match1 && match1.hash && match1.hash.groups.beatmapId) {
			beatmapId = parseInt(match1.hash.groups.beatmapId, 10);
		}

		// If no match, try second pattern: /b/{beatmapId}
		if (beatmapId === null) {
			const match2 = pattern2.exec(parsedUrl.href);
			if (match2 && match2.pathname && match2.pathname.groups.beatmapId) {
				beatmapId = parseInt(match2.pathname.groups.beatmapId, 10);
			}
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
			userData = await api.getUser(user.trim(), Ruleset.osu);
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
			userData = await api.getUser(user.trim(), Ruleset.osu);
		} catch (e) {
			console.error(e);
			error(500, 'Something went wrong');
		}

		redirect(303, `/u/${userData.id}/pulse`);
	}
);
