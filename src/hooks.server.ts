// src/hooks.server.ts
import { SvelteKitSecurityHeaders } from '@faranglao/sveltekit-security-headers';

export const handle = SvelteKitSecurityHeaders().handle;
