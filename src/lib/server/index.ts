import { OSU_CLIENT_ID, OSU_CLIENT_SECRET } from '$env/static/private';
import { Auth, Client, isOsuJSError } from 'osu-web.js';

const auth = new Auth(parseInt(OSU_CLIENT_ID), OSU_CLIENT_SECRET, '');
// If this fails, the whole app breaks
const token = await auth.clientCredentialsGrant();
export const client = new Client(token.access_token);

async function refreshToken() {
	try {
		const token = await auth.clientCredentialsGrant();
		client.setAccessToken(token.access_token);

		setTimeout(() => refreshToken(), token.expires_in);
	} catch (e) {
		console.error('Error refreshing token', e);
		if (isOsuJSError(e))
			console.error(
				`Message: ${e.message}`,
				`Cause: ${e.cause}`,
				`Type: ${e.type}`,
				`Name: ${e.name}`
			);
	}
}

setTimeout(() => refreshToken(), token.expires_in);
