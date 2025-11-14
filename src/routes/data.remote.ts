import type { APIError, User } from 'osu-api-v2-js';

import { api } from '$lib/server';
import { error, redirect } from '@sveltejs/kit';
import { form } from '$app/server';
import { Ruleset } from 'osu-api-v2-js';
import { integer, nonEmpty, number, object, pipe, string, union, url } from 'valibot';

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
	object({ user: union([pipe(string(), nonEmpty()), pipe(number(), integer())]) }),
	async ({ user }) => {
		if (typeof user === 'number' || !isNaN(parseInt(user, 10))) redirect(303, `/u/${user}`);

		let userData: User.Extended;
		try {
			userData = await api.getUser(user.trim(), Ruleset.osu);
		} catch (e) {
			const errorVar = e as APIError;
			error(errorVar.status_code ?? 500, errorVar.message);
		}

		redirect(303, `/u/${userData.id}`);
	}
);

export const navigateToUserPulse = form(
	object({ user: union([pipe(string(), nonEmpty()), pipe(number(), integer())]) }),
	async ({ user }) => {
		if (typeof user === 'number' || !isNaN(parseInt(user, 10))) redirect(303, `/u/${user}`);

		let userData: User.Extended;
		try {
			userData = await api.getUser(user.trim(), Ruleset.osu);
		} catch (e) {
			const errorVar = e as APIError;
			error(errorVar.status_code ?? 500, errorVar.message);
		}

		redirect(303, `/u/${userData.id}/pulse`);
	}
);
