import type { ParamMatcher } from '@sveltejs/kit';

export const match = ((param: string): param is string => {
	return !isNaN(parseInt(param));
}) satisfies ParamMatcher;
