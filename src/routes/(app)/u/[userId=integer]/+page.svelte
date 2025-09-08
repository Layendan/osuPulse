<script lang="ts">
	import type { Attachment } from 'svelte/attachments';
	import type { Props } from 'tippy.js';
	import type { PageProps } from './$types';

	import Beatmap from '$lib/components/Beatmap.svelte';
	import BeatmapSearch from '$lib/components/BeatmapSearch.svelte';
	import RefetchButton from '$lib/components/RefetchButton.svelte';
	import ShareButton from '$lib/components/ShareButton.svelte';
	import UserSearch from '$lib/components/UserSearch.svelte';
	import { faWater } from '@fortawesome/free-solid-svg-icons';
	import { buildUrl } from 'osu-web.js';
	import Fa from 'svelte-fa';
	import { flip } from 'svelte/animate';
	import { fade } from 'svelte/transition';
	import tippy from 'tippy.js';
	import { getUserNeighbors } from './data.remote';

	let { data }: PageProps = $props();

	const globalRank = data.user.statistics.global_rank;
	const countryRank = data.user.statistics.country_rank;

	function tooltip(content: string, props?: Partial<Props>): Attachment {
		return (element) => {
			const tooltip = tippy(element, { ...props, content });

			return () => tooltip.destroy();
		};
	}
</script>

<svelte:head>
	<title>osu!Pulse - Recommended maps for {data.user.username}</title>
	<meta name="description" content="Find similar beatmaps for {data.user.username}." />
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content="osu!Pulse - Recommended maps for {data.user.username}" />
	<meta name="twitter:description" content="Find similar beatmaps for {data.user.username}." />
	<meta property="og:type" content="website" />
	<meta property="og:title" content="osu!Pulse - Recommended maps for {data.user.username}" />
	<meta property="og:description" content="Find similar beatmaps for {data.user.username}." />
	<meta property="og:url" content="https://pulse.layendan.dev" />
	<meta property="og:site_name" content="osu!Pulse" />
	<meta property="og:locale" content="en_US" />
	<meta property="og:image" content={data.user.avatar_url} />
	<meta property="og:image:alt" content="{data.user.username} avatar" />
	<meta property="og:image:secure_url" content={data.user.avatar_url} />
</svelte:head>

<div class="bg-base-200 container mx-auto gap-2 overflow-clip rounded-xl" id="main">
	<a
		href={buildUrl.user(data.user.id)}
		target="_blank"
		rel="noopener noreferrer"
		class="relative grid w-full place-items-center px-4">
		<img
			src={data.user.cover.custom_url ?? data.user.cover.url}
			class="absolute h-full w-full object-cover"
			alt="user cover" />
		<div class="bg-base-100/80 absolute h-full w-full backdrop-blur-xs"></div>
		<div class="z-10 my-2 inline-flex items-center gap-4">
			<img
				src={data.user.avatar_url}
				class="aspect-square size-20 rounded-2xl md:size-32 md:rounded-4xl"
				alt="user avatar" />
			<div class="inline-flex flex-col gap-2">
				<h1 class="text-3xl font-bold md:text-5xl">{data.user.username}</h1>
				<span class="inline-flex gap-4">
					{#if globalRank}
						<h2 class="text-3xl font-light">
							<legend class="text-xs">Global Ranking</legend>
							#{new Intl.NumberFormat().format(globalRank)}
						</h2>
					{/if}
					{#if countryRank}
						<h2 class="text-3xl font-light max-md:hidden">
							<legend class="text-xs">Country Ranking</legend>
							#{new Intl.NumberFormat().format(countryRank)}
						</h2>
					{/if}
					<h2 class="text-3xl font-light max-sm:hidden">
						<legend class="text-xs">Performance Points</legend>
						{new Intl.NumberFormat().format(parseInt(data.user.statistics.pp.toFixed(0)))}pp
					</h2>
				</span>
			</div>
		</div>
	</a>

	<div class="bg-base-300 grid grid-cols-1 items-center gap-4 p-4 2xl:grid-cols-2">
		<div class="flex flex-col justify-around gap-2 text-center 2xl:justify-self-end">
			<h2 class="text-4xl font-bold 2xl:text-end">we think you'd like these</h2>
			<div class="inline-flex flex-row flex-wrap justify-center gap-2 2xl:justify-end">
				<a
					href="{data.user.id}/flow"
					class="btn btn-soft btn-primary group"
					{@attach tooltip(`beatmaps from ${data.user.username}'s play session`, {
						placement: 'bottom'
					})}>
					<Fa icon={faWater} />
					<div
						class="from-primary to-secondary group-hover:text-primary-content group-focus-within:text-primary-content group-disabled:text-neutral-content bg-gradient-to-r bg-clip-text text-transparent group-disabled:opacity-20">
						{data.user.username}'s flow
					</div>
				</a>
				<ShareButton />
				<RefetchButton queryFunction={getUserNeighbors(data.user.id)} />
			</div>
		</div>
		<div class="flex flex-row flex-wrap gap-2 max-2xl:justify-center">
			<BeatmapSearch />
			<UserSearch />
		</div>
	</div>

	<div class="grid min-h-[60svh] place-items-center py-4">
		<svelte:boundary>
			{@const { top_neighbors } = await getUserNeighbors(data.user.id)}

			<ul class="grid w-full grid-cols-1 gap-4 px-4 lg:grid-cols-2">
				{#each top_neighbors as neighbor, i (`${neighbor.BeatmapID}-${neighbor.Mods}`)}
					<li transition:fade={{ duration: 500 }} animate:flip={{ duration: 500 }}>
						<Beatmap {neighbor} rank={i + 1} />
					</li>
				{:else}
					<h2 class="col-span-2 text-center">no beatmaps found <br /> play some beatmaps first</h2>
				{/each}
			</ul>

			{#snippet pending()}
				<div>
					<span class="loading loading-ring loading-xl mr-2"></span>
					loading beatmaps...
				</div>
			{/snippet}

			{#snippet failed(error, reset)}
				<div class="flex flex-col gap-2">
					something went wrong - {error}
					<button class="btn btn-outline btn-warning" onclick={reset}> try again </button>
				</div>
			{/snippet}
		</svelte:boundary>
	</div>
</div>
