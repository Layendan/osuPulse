<script lang="ts">
	import BeatmapSearch from '$lib/components/BeatmapSearch.svelte';
	import FlowSearch from '$lib/components/FlowSearch.svelte';
	import UserSearch from '$lib/components/UserSearch.svelte';

	const title = 'osu!Pulse';
</script>

<svelte:head>
	<title>osu!Pulse</title>
	<meta name="description" content="Find similar beatmaps." />
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content="osu!Pulse" />
	<meta name="twitter:description" content="Find similar beatmaps." />
	<meta property="og:type" content="website" />
	<meta property="og:title" content="osu!Pulse" />
	<meta property="og:description" content="Find similar beatmaps." />
	<meta property="og:url" content="https://pulse.layendan.dev" />
	<meta property="og:site_name" content="osu!Pulse" />
	<meta property="og:locale" content="en_US" />
	<meta property="og:image" content="/logo.png" />
	<meta property="og:image:alt" content="osu!Pulse Logo" />
	<meta property="og:image:type" content="image/png" />
	<meta property="og:image:width" content="506" />
	<meta property="og:image:height" content="505" />
	<meta property="og:image:secure_url" content="https://pulse.layendan.dev/logo.png" />
</svelte:head>

<div class="grid min-h-dvh w-dvw content-center items-center gap-12 py-8 md:px-8">
	<h1 class="text-center text-6xl font-extrabold">
		welcome to
		<br />
		<div
			class="from-primary to-secondary inline-block bg-gradient-to-r bg-clip-text text-transparent">
			{#each title.split('') as char, i (i)}
				<span
					class="wave-bounce inline-block motion-reduce:animate-none"
					style="animation-delay: {(i - title.length) * 100}ms">
					{char}
				</span>
			{/each}
		</div>
	</h1>

	<div class="mx-auto">
		<BeatmapSearch />

		<UserSearch />

		<FlowSearch />
	</div>
</div>

<style>
	@keyframes waveBounce {
		0%,
		100% {
			transform: translateY(0.25rem);
		}
		50% {
			transform: translateY(-0.125rem);
		}
	}

	.wave-bounce {
		animation-name: waveBounce;
		animation-duration: 1.5s;
		animation-timing-function: ease-in-out;
		animation-iteration-count: infinite;
	}
</style>
