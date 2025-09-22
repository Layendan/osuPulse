<script lang="ts">
	import type { Attachment } from 'svelte/attachments';
	import type { Props } from 'tippy.js';

	import BeatmapSearch from '$lib/components/BeatmapSearch.svelte';
	import PulseSearch from '$lib/components/PulseSearch.svelte';
	import UserSearch from '$lib/components/UserSearch.svelte';
	import { faDiscord, faGithub } from '@fortawesome/free-brands-svg-icons';
	import Fa from 'svelte-fa';
	import tippy from 'tippy.js';

	const title = 'osu!Pulse';

	function tooltip(content: string, props?: Partial<Props>): Attachment {
		return (element) => {
			const tooltip = tippy(element, { ...props, content });

			return () => tooltip.destroy();
		};
	}
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
			class="from-primary to-secondary text-primary ff-only:text-transparent inline-block bg-gradient-to-r bg-clip-text">
			{#each title.split('') as char, i (i)}
				<span
					class="wave-bounce inline-block will-change-transform motion-reduce:animate-none"
					style="animation-delay: {(i - title.length) * 100}ms">
					{char}
				</span>
			{/each}
		</div>
	</h1>

	<div class="mx-auto">
		<fieldset class="fieldset rounded-box border-base-300 bg-base-200 w-xs border p-4">
			<legend class="fieldset-legend">about</legend>
			<p class="label inline whitespace-normal">
				osu!Pulse is a project I've been working on in my spare time meant to help osu! players find
				fun maps. Using <a
					href="https://github.com/Kuuuube/osu_skills_rs?tab=readme-ov-file"
					target="_blank"
					rel="noopener noreferrer"
					class="link link-primary">
					Kuuuube's
				</a>
				implementation of
				<a
					href="https://osuskills.com/"
					target="_blank"
					rel="noopener noreferrer"
					class="link link-primary">
					osu!Skills
				</a>, players can find similar beatmaps per skillset and then expand those to their top
				plays and recently played beatmaps.
			</p>
		</fieldset>

		<BeatmapSearch />

		<UserSearch />

		<PulseSearch />

		<fieldset class="fieldset rounded-box border-base-300 bg-base-200 w-xs border p-4">
			<legend class="fieldset-legend">socials</legend>
			<span class="mx-auto grid grid-flow-col gap-4">
				<a
					href="https://discord.gg/smyaYEM7V4"
					target="_blank"
					rel="noopener noreferrer"
					class="text-2xl"
					{@attach tooltip('discord')}>
					<Fa icon={faDiscord} />
				</a>
				<a
					href="https://github.com/Layendan/OsuPulse"
					target="_blank"
					rel="noopener noreferrer"
					class="text-2xl"
					{@attach tooltip('github')}>
					<Fa icon={faGithub} />
				</a>
			</span>
		</fieldset>
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
