import { OSU_CLIENT_ID, OSU_CLIENT_SECRET } from '$env/static/private';
import { Auth, Client } from 'osu-web.js';

const auth = new Auth(parseInt(OSU_CLIENT_ID), OSU_CLIENT_SECRET, '');
const token = await auth.clientCredentialsGrant();
export const client = new Client(token.access_token);

async function refreshToken() {
	const token = await auth.clientCredentialsGrant();
	client.setAccessToken(token.access_token);

	setTimeout(() => refreshToken(), token.expires_in);
}

setTimeout(() => refreshToken(), token.expires_in);
