<script lang="ts">
	import { faTriangleExclamation } from '@fortawesome/free-solid-svg-icons';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import Fa from 'svelte-fa';
</script>

<svelte:head>
	<title>osu!Pulse - {page.error?.message ?? page.status}</title>
	<meta name="description" content="Error {page.status} - {page.error?.message}." />
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content="osu!Pulse - {page.error?.message ?? page.status}" />
	<meta name="twitter:description" content="Error {page.status} - {page.error?.message}." />
	<meta property="og:type" content="website" />
	<meta property="og:title" content="osu!Pulse - {page.error?.message ?? page.status}" />
	<meta property="og:description" content="Error {page.status} - {page.error?.message}." />
	<meta property="og:url" content="https://pulse.layendan.dev" />
	<meta property="og:site_name" content="osu!Pulse" />
	<meta property="og:locale" content="en_US" />
	<meta property="og:image" content="/favicon.png" />
	<meta property="og:image:alt" content="osu!Pulse Logo" />
	<meta property="og:image:type" content="image/png" />
	<meta property="og:image:width" content="506" />
	<meta property="og:image:height" content="506" />
	<meta property="og:image:secure_url" content="https://pulse.layendan.dev/favicon.png" />
</svelte:head>

<div class="flex h-full min-h-screen w-full flex-col items-center justify-center gap-4">
	<Fa icon={faTriangleExclamation} class="mb-4 text-9xl" />
	<h1 class="text-center text-5xl font-bold">
		{page.status}
	</h1>
	<h2 class="text-center text-2xl">
		{page.error?.message}
	</h2>
	<a href={resolve('/')} class="btn btn-soft btn-primary">return home</a>
</div>
