<script lang="ts">
	import type { UserNeighbor } from '$lib';
	import type { Attachment } from 'svelte/attachments';
	import type { Props } from 'tippy.js';

	import { faFileArrowDown } from '@fortawesome/free-solid-svg-icons';
	import { resolve } from '$app/paths';
	import { buildUrl, getEnumMods } from 'osu-web.js';
	import Fa from 'svelte-fa';
	import { quintOut } from 'svelte/easing';
	import { Tween } from 'svelte/motion';
	import { slide } from 'svelte/transition';
	import tippy from 'tippy.js';
	import Mod from './Mod.svelte';

	let {
		neighbor,
		rank,
		isDetailed = false
	}: {
		neighbor: Pick<
			UserNeighbor,
			'BeatmapsetID' | 'BeatmapID' | 'Mods' | 'Title' | 'Version' | 'Neighbors'
		> &
			Partial<Pick<UserNeighbor, 'AvgAccuracy' | 'Score'>>;
		rank: number;
		isDetailed?: boolean;
	} = $props();

	const tweenParams = { easing: quintOut, duration: 2000 };
	const score = Tween.of(() => neighbor.Score, tweenParams);

	function tooltip(content: string, props?: Partial<Props>): Attachment {
		return (element) => {
			const tooltip = tippy(element, { ...props, content });

			return () => tooltip.destroy();
		};
	}
</script>

<div
	class="group ring-primary bg-base-300 relative grid h-full grid-cols-1 overflow-clip rounded-xl transition-all duration-200 focus-within:ring-2">
	<div
		class="relative inline-flex h-20 w-full flex-row overflow-clip rounded-xl"
		class:rounded-b-none={isDetailed}>
		<img
			src={buildUrl.beatmapsetCover(neighbor.BeatmapsetID)}
			class="absolute z-0 h-full w-full object-cover blur-xs"
			alt="beatmapset cover" />
		<div class="bg-base-100/80 pointer-events-none absolute inset-0 z-10"></div>
		<a
			href={resolve(`/b/${neighbor.BeatmapID}?mods=${neighbor.Mods}`)}
			class="relative z-10 inline-flex w-full flex-row outline-none">
			<div class="relative aspect-square h-full rounded-r-xl">
				<img
					src={buildUrl.beatmapsetThumbnail(neighbor.BeatmapsetID)}
					class="aspect-square h-full rounded-r-xl object-cover transition-all group-focus-within:brightness-[20%] group-hover:brightness-[20%]"
					class:rounded-b-none={isDetailed}
					alt="beatmapset thumbnail" />
				<p
					class="absolute inset-0 z-20 inline-flex size-full items-center justify-center text-2xl font-bold opacity-0 transition-opacity group-focus-within:opacity-100 group-hover:opacity-100">
					#{rank}
				</p>
			</div>
			<span class="flex w-full items-center justify-between pr-4">
				<div class="inline-flex flex-col px-4">
					<h1 class="line-clamp-1 text-xl font-bold break-all md:text-2xl">{neighbor.Title}</h1>
					<h2 class="line-clamp-1 text-xl font-light break-all">[{neighbor.Version}]</h2>
				</div>
				<ul class="inline-flex flex-row items-center gap-1">
					{#each getEnumMods(neighbor.Mods) as mod (mod)}
						<li>
							<Mod {mod} {@attach tooltip(mod)} />
						</li>
					{/each}

					{#if neighbor.AvgAccuracy}
						<p class="ml-3 text-right text-xl font-light">
							<legend class="text-xs">Exp.&nbsp;Accuracy</legend>
							{(neighbor.AvgAccuracy * 100).toFixed(2)}%
						</p>
					{/if}
				</ul>
			</span>
		</a>
		<div
			class="bg-base-300 z-10 flex w-0 items-center justify-center rounded-xl transition-[width] duration-200 group-focus-within:w-14 group-hover:w-14 md:w-4"
			class:rounded-b-none={isDetailed}>
			<a
				href="osu://b/{neighbor.BeatmapID}"
				class="opacity-0 transition-opacity duration-200 group-focus-within:opacity-100 group-hover:opacity-100"
				{@attach tooltip('open in osu!direct')}>
				<Fa icon={faFileArrowDown} />
			</a>
		</div>
	</div>
	{#if isDetailed}
		<div class="rounded-b-xl p-4" transition:slide>
			{#if score.current}
				<span class="mb-4 inline-flex w-full justify-center">
					<h2 class="font-semibold">pulse score:</h2>
					&nbsp;{score.current.toFixed(2)} points
				</span>
			{/if}
			<ul class="flex flex-col gap-4">
				{#each neighbor.Neighbors.sort((a, b) => a.distance - b.distance) as neighborInfo (`${neighborInfo.beatmap_id}-${neighborInfo.mods}`)}
					<li
						class="focus-within:outline-base-content hover:outline-base-content outline-base-content/20 rounded-xl p-2 outline-2 transition-all">
						<a
							class="flex items-center gap-2 outline-none"
							href={resolve(`/b/${neighborInfo.beatmap_id}?mods=${neighborInfo.mods}`)}>
							<img
								src={buildUrl.beatmapsetThumbnail(neighborInfo.beatmapset_id)}
								class="aspect-square h-14 rounded-xl object-cover"
								alt="beatmapset thumbnail" />
							<div class="inline-flex w-full flex-col">
								<h1 class="line-clamp-1 text-lg font-semibold break-all">
									{neighborInfo.title}
								</h1>
								<h2 class="line-clamp-1 text-base font-light break-all">
									[{neighborInfo.version}]
								</h2>
							</div>
							<p class="ml-3 text-right text-base font-light">
								<legend class="text-xs">Distance</legend>
								{neighborInfo.distance.toFixed(2)}
							</p>
						</a>
					</li>
				{/each}
			</ul>
		</div>
	{/if}
</div>
