import type { APIError, User } from 'osu-api-v2-js';
import type { PageServerLoad } from './$types';

import { api } from '$lib/server';
import { error } from '@sveltejs/kit';
import { Ruleset } from 'osu-api-v2-js';

export const load = (async ({ params }) => {
	const userId = parseInt(params.userId);

	let user: User.Extended;

	try {
		user = await api.getUser(userId, Ruleset.osu);
	} catch (e) {
		const errorVar = e as APIError;
		error(errorVar.status_code ?? 500, errorVar.message);
	}

	if (user.is_deleted) {
		error(404, 'User is deleted');
	}

	return { user };
}) satisfies PageServerLoad;
