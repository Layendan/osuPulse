<script lang="ts">
	import type { Attachment } from 'svelte/attachments';
	import type { Props } from 'tippy.js';
	import type { PageProps } from './$types';

	import { ModsList } from '$lib';
	import Beatmap from '$lib/components/Beatmap.svelte';
	import BeatmapSearch from '$lib/components/BeatmapSearch.svelte';
	import Mod from '$lib/components/Mod.svelte';
	import ShareButton from '$lib/components/ShareButton.svelte';
	import UserSearch from '$lib/components/UserSearch.svelte';
	import { faStar } from '@fortawesome/free-solid-svg-icons';
	import { pushState } from '$app/navigation';
	import { page } from '$app/state';
	import { buildUrl, getEnumMods, getModsEnum } from 'osu-web.js';
	import Fa from 'svelte-fa';
	import { flip } from 'svelte/animate';
	import { fade } from 'svelte/transition';
	import tippy from 'tippy.js';
	import { getBeatmapNeighbors } from './data.remote';

	let { data }: PageProps = $props();

	let mods = $derived(data.mods);
	let enumMods = $derived(getEnumMods(mods));

	let addModModal: HTMLDialogElement | undefined = $state(undefined);

	$effect(() => pushState(`${data.beatmap.id}/?mods=${mods}`, page.state));

	function tooltip(
		content: string,
		props?: Partial<Props>,
		updateContent?: () => string
	): Attachment {
		return (element) => {
			const tooltip = tippy(element, { ...props, content });

			if (updateContent)
				$effect(() => {
					element && tooltip.setContent(updateContent());
				});

			return () => tooltip.destroy();
		};
	}
</script>

<svelte:head>
	<title>osu!Pulse - Recommended maps for {data.beatmap.beatmapset.title}</title>
	<meta name="description" content="Find similar beatmaps for {data.beatmap.beatmapset.title}." />
	<meta name="twitter:card" content="summary" />
	<meta
		name="twitter:title"
		content="osu!Pulse - Recommended maps for {data.beatmap.beatmapset.title}" />
	<meta
		name="twitter:description"
		content="Find similar beatmaps for {data.beatmap.beatmapset.title}." />
	<meta property="og:type" content="website" />
	<meta
		property="og:title"
		content="osu!Pulse - Recommended maps for {data.beatmap.beatmapset.title}" />
	<meta
		property="og:description"
		content="Find similar beatmaps for {data.beatmap.beatmapset.title}." />
	<meta property="og:url" content="https://pulse.layendan.dev" />
	<meta property="og:site_name" content="osu!Pulse" />
	<meta property="og:locale" content="en_US" />
	<meta property="og:image" content={data.beatmap.beatmapset.covers['card@2x']} />
	<meta property="og:image:alt" content="{data.beatmap.beatmapset.title} card" />
	<meta property="og:image:secure_url" content={data.beatmap.beatmapset.covers['card@2x']} />
</svelte:head>

<div class="bg-base-200 container mx-auto gap-2 overflow-clip rounded-xl" id="main">
	<a
		href={buildUrl.beatmap(data.beatmap.id)}
		target="_blank"
		rel="noopener noreferrer"
		class="relative grid w-full place-items-center px-4">
		<img
			src={data.beatmap.beatmapset.covers['cover@2x']}
			class="absolute h-full w-full object-cover"
			alt="beatmap cover" />
		<div class="bg-base-100/80 absolute h-full w-full backdrop-blur-xs"></div>
		<div class="z-10 my-2 inline-flex items-center gap-4">
			<img
				src={data.beatmap.beatmapset.covers['card@2x']}
				class="aspect-square size-20 rounded-2xl object-cover md:size-32 md:rounded-4xl"
				alt="beatmap card" />
			<div class="inline-flex flex-col gap-2">
				<span class="inline-flex flex-col gap-0">
					<h1 class="text-3xl font-bold md:text-5xl">{data.beatmap.beatmapset.title}</h1>
					<h2 class="text-xl font-light md:text-2xl">[{data.beatmap.version}]</h2>
				</span>
				<span class="inline-flex gap-4">
					<h2 class="text-3xl font-light">
						<legend class="text-xs">Star Rating</legend>
						<span class="inline-flex flex-row items-center gap-1">
							{new Intl.NumberFormat().format(data.beatmap.difficulty_rating)}
							<Fa icon={faStar} class="text-xl" />
						</span>
					</h2>
					{#if data.beatmap.bpm}
						<h2 class="text-3xl font-light">
							<legend class="text-xs">Beats Per Minute</legend>
							{new Intl.NumberFormat().format(data.beatmap.bpm)}bpm
						</h2>
					{/if}
				</span>
			</div>
		</div>
	</a>

	<div class="bg-base-300 grid grid-cols-1 items-center gap-4 p-4 2xl:grid-cols-2">
		<div class="flex flex-col justify-around gap-2 text-center 2xl:justify-self-end">
			<h2 class="text-4xl font-bold 2xl:text-end">similar beatmaps</h2>
			<div class="inline-flex flex-row flex-wrap justify-center gap-2 2xl:justify-end">
				<a
					href="osu://b/{data.beatmap.id}"
					class="btn btn-soft btn-secondary"
					{@attach tooltip('open in osu!direct', {
						placement: 'bottom'
					})}>
					download beatmap
				</a>
				<ShareButton />
				<button
					onclick={() =>
						getBeatmapNeighbors({ beatmapId: data.beatmap.id, mods: data.mods }).refresh()}
					class="btn btn-warning btn-soft"
					disabled={getBeatmapNeighbors({ beatmapId: data.beatmap.id, mods: data.mods }).loading}
					aria-disabled={getBeatmapNeighbors({ beatmapId: data.beatmap.id, mods: data.mods })
						.loading}
					{@attach tooltip('refresh osu! data', {
						placement: 'bottom'
					})}>
					{#if getBeatmapNeighbors({ beatmapId: data.beatmap.id, mods: data.mods }).loading}
						<span class="loading loading-ring"></span>
					{/if}
					refetch data
				</button>
			</div>
		</div>
		<div class="flex flex-row flex-wrap gap-2 max-2xl:justify-center">
			<BeatmapSearch />
			<UserSearch />
		</div>
	</div>

	<div class="bg-base-300 grid place-items-center p-4">
		<span class="inline-flex flex-row gap-1">
			{#each enumMods as mod (mod)}
				<Mod {mod} {@attach tooltip(mod)} />
			{/each}
			<button onclick={() => addModModal?.showModal()} class="btn btn-primary btn-soft ml-3">
				edit mods
			</button>
			<dialog id="add_mod_modal" class="modal modal-bottom" bind:this={addModModal}>
				<div class="modal-box">
					<form method="dialog">
						<button class="btn btn-sm btn-circle btn-ghost absolute top-2 right-2">✕</button>
					</form>

					<h3 class="mb-2 text-lg font-bold">edit mods</h3>
					<ul class="inline-flex flex-row gap-2">
						{#each ModsList as mod (mod)}
							{@const [modVal] = getEnumMods(mod)}
							{@const included = enumMods.includes(modVal)}
							{@const updateContent = () => (included ? `remove ${modVal}` : `add ${modVal}`)}
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
						{/each}
					</ul>
				</div>
				<form method="dialog" class="modal-backdrop">
					<button>close</button>
				</form>
			</dialog>
		</span>
	</div>

	<div class="grid min-h-[60svh] place-items-center py-4">
		<svelte:boundary>
			{@const { neighbors } = await getBeatmapNeighbors({
				beatmapId: data.beatmap.id,
				mods
			})}

			<ul class="grid w-full grid-cols-1 gap-4 px-4 lg:grid-cols-2">
				{#each neighbors as neighbor, i (`${neighbor.BeatmapID}-${neighbor.Mods}`)}
					<li transition:fade={{ duration: 500 }} animate:flip={{ duration: 500 }}>
						<Beatmap {neighbor} rank={i + 1} />
					</li>
				{:else}
					<h2 class="col-span-2 text-center">no beatmaps found</h2>
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
