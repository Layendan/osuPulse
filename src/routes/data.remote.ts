import type { UserExtended } from 'osu-web.js';

import { client } from '$lib/server';
import { error, redirect } from '@sveltejs/kit';
import { form } from '$app/server';
import { isOsuJSError } from 'osu-web.js';

export const navigateToBeatmap = form((data) => {
	const beatmap = data.get('beatmap');

	if (typeof beatmap !== 'string' || beatmap.length === 0) {
		error(400, 'Beatmap URL is required');
	}

	let parsedUrl: URL;
	try {
		parsedUrl = new URL(beatmap);
	} catch (e) {
		console.error(e);
		error(400, 'Invalid URL');
	}

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
});

export const navigateToUser = form(async (data) => {
	const user = data.get('user');

	if (typeof user !== 'string' || user.length === 0) {
		error(400, 'Username is required');
	}

	let userData: UserExtended;
	try {
		userData = await client.users.getUser(user);
	} catch (e) {
		console.error(e);
		if (isOsuJSError(e)) {
			console.error(`Message: ${e.message}`, `Cause: ${e.cause}`);
			switch (e.type) {
				case 'invalid_json_syntax':
					error(400, 'Invalid JSON syntax');
					break;
				case 'network_error':
					error(500, 'Network error');
					break;
				case 'unexpected_response': {
					const response = e.response();

					if (response.status === 404) {
						error(404, 'User not found');
					}

					const text = await response.text();
					console.error(response.status, text);
					error(response.status, text);
					break;
				}
				default:
					error(500, 'Something went wrong');
					break;
			}
		}
		error(500, 'Something went wrong');
	}

	redirect(303, `/u/${userData.id}`);
});

export const navigateToUserFlow = form(async (data) => {
	const user = data.get('user');

	if (typeof user !== 'string' || user.length === 0) {
		error(400, 'Username is required');
	}

	let userData;
	try {
		userData = await client.users.getUser(user);
	} catch (e) {
		console.error(e);
		if (isOsuJSError(e)) {
			console.error(`Message: ${e.message}`, `Cause: ${e.cause}`);
			switch (e.type) {
				case 'invalid_json_syntax':
					error(400, 'Invalid JSON syntax');
					break;
				case 'network_error':
					error(500, 'Network error');
					break;
				case 'unexpected_response': {
					const response = e.response();

					if (response.status === 404) {
						error(404, 'User not found');
					}

					const text = await response.text();
					console.error(response.status, text);
					error(response.status, text);
					break;
				}
				default:
					error(500, 'Something went wrong');
					break;
			}
		}
		error(500, 'Something went wrong');
	}

	redirect(303, `/u/${userData.id}/flow`);
});
