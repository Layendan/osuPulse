import { OSU_CLIENT_ID, OSU_CLIENT_SECRET } from '$env/static/private';
import * as osu from 'osu-api-v2-js';

export const api = await osu.API.createAsync(
	parseInt(OSU_CLIENT_ID),
	OSU_CLIENT_SECRET,
	undefined,
	{ verbose: 'errors', refresh_token_on_expires: true }
);
