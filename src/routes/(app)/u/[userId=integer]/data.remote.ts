import type { UserNeighbor } from '$lib';

import { error } from '@sveltejs/kit';
import { query } from '$app/server';
import { EMBED_API_URL } from '$env/static/private';
import { number } from 'valibot';

type NeighborResponse = {
	user_id: number;
	top_neighbors: UserNeighbor[];
};

export const getUserNeighbors = query(number(), async (userId) => {
	const url = new URL(`${EMBED_API_URL}/user_top_neighbors/`);
	const response = await fetch(url, {
		method: 'POST',
		headers: {
			accept: 'application/json',
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			user_id: userId
		})
	});

	if (!response.ok) error(404, 'Not found');

	const neighbors: NeighborResponse = await response.json();

	return neighbors;
});
