import { error, redirect } from '@sveltejs/kit';
import { form } from '$app/server';

export const navigateToBeatmap = form((data) => {
	const beatmap = data.get('beatmap');

	if (typeof beatmap !== 'string' || beatmap.length === 0) {
		error(400, 'Beatmap URL is required');
	}

	let parsedUrl: URL;
	try {
		parsedUrl = new URL(beatmap);
	} catch (e) {
		console.log(e);
		error(400, 'Invalid URL');
	}

	if (parsedUrl.hostname !== 'osu.ppy.sh') {
		error(400, 'Invalid URL');
	}

	const pathMatch = parsedUrl.pathname.match(/^\/beatmapsets\/\d+$/);
	if (!pathMatch) {
		error(400, 'Invalid URL');
	}

	// Hash expected to be #osu/{beatmapId}
	const hashMatch = parsedUrl.hash.match(/^#osu\/(\d+)$/);
	if (!hashMatch) {
		error(400, 'Invalid URL');
	}

	// Parse beatmap id to number
	const beatmapId = parseInt(hashMatch[1], 10);
	if (isNaN(beatmapId)) {
		error(400, 'Invalid URL');
	}

	redirect(303, `/b/${beatmapId}`);
});

export const navigateToUser = form((data) => {
	const user = data.get('user');

	if (typeof user !== 'string' || user.length === 0) {
		error(400, 'User URL is required');
	}

	let parsedUrl: URL;
	try {
		parsedUrl = new URL(user);
	} catch (e) {
		console.error(e);
		error(400, 'Invalid URL');
	}

	// Validate hostname
	if (parsedUrl.hostname !== 'osu.ppy.sh') {
		error(400, 'User URL is required');
	}

	const match = parsedUrl.pathname.match(/^\/users\/(\d+)(\/(osu|taiko|fruits|mania))?\/?$/);
	if (!match) {
		error(400, 'Invalid URL');
	}

	const userId = parseInt(match[1], 10);
	if (isNaN(userId)) {
		error(400, 'Invalid URL');
	}

	redirect(303, `/u/${userId}`);
});

export const navigateToUserFlow = form((data) => {
	const user = data.get('user');

	if (typeof user !== 'string' || user.length === 0) {
		error(400, 'User URL is required');
	}

	let parsedUrl: URL;
	try {
		parsedUrl = new URL(user);
	} catch (e) {
		console.error(e);
		error(400, 'Invalid URL');
	}

	// Validate hostname
	if (parsedUrl.hostname !== 'osu.ppy.sh') {
		error(400, 'User URL is required');
	}

	const match = parsedUrl.pathname.match(/^\/users\/(\d+)(\/(osu|taiko|fruits|mania))?\/?$/);
	if (!match) {
		error(400, 'Invalid URL');
	}

	const userId = parseInt(match[1], 10);
	if (isNaN(userId)) {
		error(400, 'Invalid URL');
	}

	redirect(303, `/u/${userId}/flow`);
});
