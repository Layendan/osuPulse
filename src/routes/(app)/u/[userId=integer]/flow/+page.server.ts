import type { PageServerLoad } from './$types';

import { redirect } from '@sveltejs/kit';

export const load = (async ({ params }) => {
	redirect(301, `/u/${params.userId}/pulse`);
}) satisfies PageServerLoad;
