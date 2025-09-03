import { OSU_CLIENT_ID, OSU_CLIENT_SECRET } from '$env/static/private';
import { Auth, Client } from 'osu-web.js';

const auth = new Auth(parseInt(OSU_CLIENT_ID), OSU_CLIENT_SECRET, '');
const token = await auth.clientCredentialsGrant();
export const client = new Client(token.access_token);
