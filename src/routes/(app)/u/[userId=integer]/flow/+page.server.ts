import type { PageServerLoad } from './$types';

import { client } from '$lib/server';
import { error } from '@sveltejs/kit';

export const load = (async ({ params }) => {
	const userId = parseInt(params.userId);

	let user: Awaited<ReturnType<typeof client.users.getUser>>;

	try {
		user = await client.users.getUser(userId, {
			urlParams: {
				mode: 'osu'
			}
		});
	} catch (e) {
		console.error(e);
		error(404, 'User not found');
	}

	if (user.is_deleted) {
		error(404, 'User is deleted');
	}

	return { user };
}) satisfies PageServerLoad;
