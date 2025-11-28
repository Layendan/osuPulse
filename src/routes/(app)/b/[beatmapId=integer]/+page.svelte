<script lang="ts">
	import type { Attachment } from 'svelte/attachments';
	import type { Props } from 'tippy.js';
	import type { PageProps } from './$types';

	import { ModsList } from '$lib';
	import Beatmap from '$lib/components/Beatmap.svelte';
	import BeatmapDetailToggle from '$lib/components/BeatmapDetailToggle.svelte';
	import BeatmapSearch from '$lib/components/BeatmapSearch.svelte';
	import FilterButton from '$lib/components/FilterButton.svelte';
	import Header from '$lib/components/Header.svelte';
	import Mod from '$lib/components/Mod.svelte';
	import OsuDifficultyButton from '$lib/components/OsuDifficultyButton.svelte';
	import RefetchButton from '$lib/components/RefetchButton.svelte';
	import ShareButton from '$lib/components/ShareButton.svelte';
	import UserSearch from '$lib/components/UserSearch.svelte';
	import { faFileArrowDown, faInfoCircle } from '@fortawesome/free-solid-svg-icons';
	import { page } from '$app/state';
	import { getEnumMods, getModsEnum } from 'osu-web.js';
	import Fa from 'svelte-fa';
	import { flip } from 'svelte/animate';
	import { fade } from 'svelte/transition';
	import tippy from 'tippy.js';
	import { getBeatmapNeighbors } from './data.remote';

	let { data }: PageProps = $props();

	let mods = $derived(data.mods);
	let enumMods = $derived(getEnumMods(mods));
	const url = $derived.by(() => {
		const url = new URL(page.url);
		url.searchParams.set('mods', mods.toString());
		return url.href;
	});

	let addModModal: HTMLDialogElement | undefined = $state(undefined);

	let showNsfw: boolean = $state(true);

	let minStars: number | undefined = $state(undefined);
	let maxStars: number | undefined = $state(undefined);

	let minPp: number | undefined = $state(undefined);
	let maxPp: number | undefined = $state(undefined);

	let minHitLength: number | undefined = $state(undefined);
	let maxHitLength: number | undefined = $state(undefined);

	let minBpm: number | undefined = $state(undefined);
	let maxBpm: number | undefined = $state(undefined);

	let excludedMods: number | undefined = $state(undefined);
	let includedMods: number | undefined = $state(undefined);

	let isDetailed: boolean = $state(false);

	const query = $derived(
		getBeatmapNeighbors({
			beatmapId: data.beatmap.id,
			mods,
			showNsfw,
			minStars,
			maxStars,
			minPp,
			maxPp,
			minHitLength,
			maxHitLength,
			minBpm,
			maxBpm,
			excludedMods,
			includedMods
		})
	);

	function tooltip(
		content: string,
		props?: Partial<Props>,
		updateContent?: () => string
	): Attachment {
		return (element) => {
			const tooltip = tippy(element, { ...props, content });

			if (updateContent)
				$effect(() => {
					if (element) tooltip.setContent(updateContent());
				});

			return () => tooltip.destroy();
		};
	}
</script>

<svelte:head>
	<title>osu!Pulse - Recommended maps for {data.beatmap.beatmapset.title}</title>
	<meta
		name="description"
		content="Get detailed data for {data.beatmap.beatmapset
			.title} with osu!Pulse. View key stats, difficulty levels, and performance insights while exploring personalized recommendations for similar maps to enhance your osu! gameplay experience." />
	<meta name="twitter:card" content="summary" />
	<meta
		name="twitter:title"
		content="osu!Pulse - Recommended maps for {data.beatmap.beatmapset.title}" />
	<meta
		name="twitter:description"
		content="Get detailed data for {data.beatmap.beatmapset
			.title} with osu!Pulse. View key stats, difficulty levels, and performance insights while exploring personalized recommendations for similar maps to enhance your osu! gameplay experience." />
	<meta property="og:type" content="website" />
	<meta
		property="og:title"
		content="osu!Pulse - Recommended maps for {data.beatmap.beatmapset.title}" />
	<meta
		property="og:description"
		content="Get detailed data for {data.beatmap.beatmapset
			.title} with osu!Pulse. View key stats, difficulty levels, and performance insights while exploring personalized recommendations for similar maps to enhance your osu! gameplay experience." />
	<meta property="og:url" content="https://pulse.layendan.dev" />
	<meta property="og:site_name" content="osu!Pulse" />
	<meta property="og:locale" content="en_US" />
	<meta property="og:image" content={data.beatmap.beatmapset.covers['card@2x']} />
	<meta property="og:image:alt" content="{data.beatmap.beatmapset.title} card" />
	<meta property="og:image:secure_url" content={data.beatmap.beatmapset.covers['card@2x']} />
</svelte:head>

<div class="bg-base-200 container mx-auto gap-2 overflow-clip rounded-xl" id="main">
	<Header data={$state.eager(data.beatmap)} />

	<div class="bg-base-300 grid grid-cols-1 items-center gap-4 p-4 2xl:grid-cols-2">
		<div class="flex flex-col justify-around gap-2 text-center 2xl:justify-self-end">
			<h2 class="text-4xl font-bold 2xl:text-end">
				similar beatmaps
				<button
					class="cursor-context-menu text-xl"
					aria-label="more information"
					{@attach tooltip(
						`these beatmaps are the most similar to ${data.beatmap.beatmapset.title}, based on the estimated skills required to pass it (accuracy, aim, flashlight, precision, reaction, stamina, and streams)`,
						{ placement: 'bottom' }
					)}>
					<Fa icon={faInfoCircle} />
				</button>
			</h2>
			<div class="inline-flex flex-row flex-wrap justify-center gap-2 2xl:justify-end">
				<a
					href="osu://b/{data.beatmap.id}"
					class="btn btn-soft btn-secondary"
					{@attach tooltip('open in osu!direct', {
						placement: 'bottom'
					})}>
					<Fa icon={faFileArrowDown} />
					download beatmap
				</a>
				<ShareButton {url} />
				<RefetchButton queryFunction={query} />
				<FilterButton
					bind:showNsfw
					bind:minStars
					bind:maxStars
					bind:minPp
					bind:maxPp
					bind:minHitLength
					bind:maxHitLength
					bind:minBpm
					bind:maxBpm
					bind:excludedMods
					bind:includedMods />
				<BeatmapDetailToggle bind:isDetailed />
			</div>
		</div>
		<div class="flex flex-row flex-wrap gap-2 max-2xl:justify-center">
			<BeatmapSearch />
			<UserSearch />
		</div>
	</div>

	<span class="bg-base-300 inline-flex w-full flex-row justify-center">
		<span
			class="bg-base-200 lg:3/5 inline-flex w-fit max-w-4/5 flex-row flex-wrap justify-center gap-2 rounded-xl p-2">
			{#each $state
				.eager(data.difficulties)
				.sort((a, b) => a.Stars - b.Stars) as difficulty (difficulty.BeatmapId)}
				<OsuDifficultyButton {difficulty} />
			{/each}
		</span>
	</span>

	<span class="bg-base-300 inline-flex w-full flex-row justify-center gap-2 py-4">
		{#if enumMods.length > 0}
			<span class="inline-flex flex-row gap-1">
				{#each enumMods as mod (mod)}
					<Mod {mod} {@attach tooltip(mod)} />
				{/each}
			</span>
		{/if}
		<button onclick={() => addModModal?.showModal()} class="btn btn-primary btn-soft">
			edit mods
		</button>
		<dialog id="add_mod_modal" class="modal" bind:this={addModModal}>
			<div class="modal-box">
				<form method="dialog">
					<button class="btn btn-sm btn-circle btn-ghost absolute top-2 right-2">✕</button>
				</form>

				<h3 class="mb-2 text-lg font-bold">edit map mods</h3>
				<ul class="inline-flex flex-row flex-wrap gap-2">
					{#each ModsList as mod (mod)}
						{@const [modVal] = getEnumMods(mod)}
						{@const included = enumMods.includes(modVal)}
						{@const updateContent = () => (included ? `remove ${modVal}` : `add ${modVal}`)}
						<li>
							<button
								onclick={() => {
									if (included) mods = getModsEnum(enumMods.filter((item) => item !== modVal));
									else {
										mods = getModsEnum(
											[...enumMods, modVal].filter((item) => {
												if (modVal === 'DT' || modVal === 'NC')
													return item !== 'HT' && item !== 'DC';
												else if (modVal === 'HT' || modVal === 'DC')
													return item !== 'DT' && item !== 'NC';
												else if (modVal === 'HR') return item !== 'EZ';
												else if (modVal === 'EZ') return item !== 'HR';
												else return true;
											})
										);
									}
								}}
								class="cursor-pointer transition-opacity"
								class:opacity-20={!included}>
								<Mod
									mod={modVal}
									{@attach tooltip(
										updateContent(),
										{
											appendTo: addModModal
										},
										updateContent
									)} />
							</button>
						</li>
					{/each}
					<li>
						<button
							onclick={() => {
								mods = 0;
								enumMods = [];
							}}
							class="btn btn-warning btn-soft">
							reset
						</button>
					</li>
				</ul>
			</div>
			<form method="dialog" class="modal-backdrop">
				<button>close</button>
			</form>
		</dialog>
	</span>

	<div class="grid min-h-[60svh] place-items-center py-4">
		<svelte:boundary>
			{@const { neighbors } = await query}

			<ul class="grid w-full grid-cols-1 gap-4 px-4 lg:grid-cols-2">
				{#each neighbors as neighbor, i (`${neighbor.BeatmapId}-${neighbor.Mods}`)}
					{@const neighborExtended = {
						...neighbor,
						Neighbors: [
							{
								beatmap_id: data.beatmap.id,
								beatmapset_id: data.beatmap.beatmapset_id,
								mods: data.mods,
								title: data.beatmap.beatmapset.title,
								version: data.beatmap.version,
								ranked: data.beatmap.ranked,
								distance: neighbor.Distance
							}
						]
					}}
					<li transition:fade={{ duration: 500 }} animate:flip={{ duration: 500 }}>
						<Beatmap neighbor={neighborExtended} rank={i + 1} {isDetailed} />
					</li>
				{:else}
					<h2 class="col-span-2 text-center">
						{#if data.beatmap.status !== 'ranked'}
							currently, only ranked beatmaps are available
						{:else}
							no beatmaps found
						{/if}
					</h2>
				{/each}
			</ul>

			{#snippet pending()}
				<div>
					<span class="loading loading-ring loading-xl mr-2"></span>
					loading beatmaps...
				</div>
			{/snippet}

			{#snippet failed(error, reset)}
				{@const errorVar: {status: number, body: {message: string}} = (error as typeof errorVar)}
				<div class="flex flex-col gap-2">
					something went wrong - {errorVar.status}: {errorVar.body.message}
					<button class="btn btn-outline btn-warning" onclick={reset}> try again </button>
				</div>
			{/snippet}
		</svelte:boundary>
	</div>
</div>
