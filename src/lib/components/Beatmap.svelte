<script lang="ts">
	import type { UserNeighbor } from '$lib';
	import type { Attachment } from 'svelte/attachments';
	import type { Props } from 'tippy.js';

	import { faCertificate, faCopy, faFileArrowDown } from '@fortawesome/free-solid-svg-icons';
	import { resolve } from '$app/paths';
	import { Beatmapset } from 'osu-api-v2-js';
	import { buildUrl, getEnumMods } from 'osu-web.js';
	import Fa from 'svelte-fa';
	import { quintOut } from 'svelte/easing';
	import { Tween } from 'svelte/motion';
	import { slide } from 'svelte/transition';
	import tippy from 'tippy.js';
	import DifficultyPill from './DifficultyPill.svelte';
	import Mod from './Mod.svelte';

	let {
		neighbor,
		rank,
		isDetailed = false
	}: {
		neighbor: Pick<
			UserNeighbor,
			| 'BeatmapSetId'
			| 'BeatmapId'
			| 'Mods'
			| 'Title'
			| 'Version'
			| 'Neighbors'
			| 'Ranked'
			| 'Stars'
			| 'PP'
		> &
			Partial<Pick<UserNeighbor, 'AvgAccuracy' | 'Score' | 'LastUpdated'>>;
		rank: number;
		isDetailed?: boolean;
	} = $props();

	const tweenParams = { easing: quintOut, duration: 2000 };
	const score = Tween.of(() => neighbor.Score, tweenParams);
	const mods = getEnumMods(neighbor.Mods);
	const { text: badgeText, style: badgeStyle } = getBadgeData(neighbor.Ranked);

	function tooltip(content: string, props?: Partial<Props>): Attachment {
		return (element) => {
			const tooltip = tippy(element, { ...props, content });

			return () => tooltip.destroy();
		};
	}

	function getBadgeData(ranked: Beatmapset.RankStatus) {
		switch (ranked) {
			case Beatmapset.RankStatus.Ranked:
				return {
					style: `--badge-bg: hsl(90,100%,70%); --badge-fg: hsl(200,10%,25%);`,
					text: 'Ranked'
				};

			case Beatmapset.RankStatus.Approved:
				return {
					style: `--badge-bg: hsl(90,100%,70%); --badge-fg: hsl(200,10%,25%);`,
					text: 'Approved'
				};

			case Beatmapset.RankStatus.Loved:
				return {
					style: `--badge-bg: hsl(333,100%,70%); --badge-fg: hsl(200,10%,25%);`,
					text: 'Loved'
				};

			default:
				return {
					style: `--badge-bg: hsl(0,25%,65%); --badge-fg: hsl(200,10%,25%);`,
					text: 'Unknown'
				};
		}
	}
</script>

<div
	class="group ring-primary bg-base-300 relative grid h-full grid-cols-1 overflow-clip rounded-xl transition-all duration-200 focus-within:ring-2">
	<div
		class="relative inline-flex h-20 w-full flex-row overflow-clip rounded-xl sm:h-28"
		class:rounded-b-none={isDetailed}>
		<img
			src={buildUrl.beatmapsetCover(neighbor.BeatmapSetId)}
			class="not-safari-only:blur-xs absolute inset-0 z-0 size-full object-cover"
			alt="beatmapset cover" />
		<div
			class="bg-base-100/80 safari-only:backdrop-blur-xs pointer-events-none absolute inset-0 z-10 size-full">
		</div>
		<a
			href={resolve(`/b/${neighbor.BeatmapId}?mods=${neighbor.Mods}`)}
			class="relative z-10 inline-flex w-full flex-row outline-none">
			<div class="relative aspect-square h-full rounded-r-xl">
				<img
					src={buildUrl.beatmapsetThumbnail(neighbor.BeatmapSetId)}
					class="aspect-square h-full rounded-r-xl object-cover transition-all group-focus-within:brightness-20 group-hover:brightness-20"
					class:rounded-b-none={isDetailed}
					alt="beatmapset thumbnail" />
				<p
					class="absolute inset-0 z-20 inline-flex size-full items-center justify-center text-2xl font-bold opacity-0 transition-opacity group-focus-within:opacity-100 group-hover:opacity-100">
					#{rank}
				</p>
			</div>
			<span class="flex h-full w-full items-center justify-between gap-0 pr-4 sm:gap-4">
				<div class="inline-flex flex-col justify-around gap-2 px-4">
					<div class="inline-flex flex-col">
						<h1 class="line-clamp-1 text-base font-bold break-all sm:text-2xl">{neighbor.Title}</h1>
						<h2 class="line-clamp-1 text-sm font-light break-all sm:text-lg">
							[{neighbor.Version}]
						</h2>
					</div>
					<div class="inline-flex flex-row gap-1">
						<div class="badge badge-sm font-bold uppercase" style={badgeStyle}>
							{badgeText}
						</div>
						<DifficultyPill stars={neighbor.Stars} />
						{#if neighbor.LastUpdated && (Date.now() - neighbor.LastUpdated.getTime()) / (1000 * 3600 * 24) <= 90}
							<div class="badge-sm badge badge-accent hidden font-bold uppercase sm:inline-flex">
								<Fa icon={faCertificate} />
								New
							</div>
						{/if}
					</div>
				</div>
				<div class="inline-flex flex-row items-center gap-1">
					<ul
						class="grid w-max place-items-center gap-x-1 gap-y-0.5"
						class:grid-rows-2={mods.length >= 2}
						class:grid-cols-2={mods.length >= 3}>
						{#each mods as mod, i (mod)}
							<li class:col-span-2={i === 2 && mods.length === 3}>
								<Mod {mod} {@attach tooltip(mod)} />
							</li>
						{/each}
					</ul>

					<div class="hidden flex-col justify-center gap-2 sm:ml-3 sm:flex">
						{#if neighbor.AvgAccuracy}
							<p class="inline-flex flex-col text-right text-lg font-light">
								<legend class="text-xs">Exp.&nbsp;Accuracy</legend>
								{new Intl.NumberFormat(undefined, {
									style: 'percent',
									minimumFractionDigits: 2,
									maximumFractionDigits: 2
								}).format(neighbor.AvgAccuracy)}
							</p>
						{/if}
						<p class="inline-flex flex-col text-right text-lg font-light">
							<legend class="text-xs">Maximum&nbsp;PP</legend>
							{new Intl.NumberFormat(undefined, {
								maximumFractionDigits: 0
							}).format(neighbor.PP)}pp
						</p>
					</div>
				</div>
			</span>
		</a>
		<div
			class="bg-base-300 z-10 grid w-0 grid-rows-2 items-center justify-center rounded-xl py-2 transition-[width] duration-200 group-focus-within:w-14 group-hover:w-14 sm:w-4"
			class:rounded-b-none={isDetailed}>
			<button
				onclick={() => navigator.clipboard.writeText(neighbor.BeatmapId.toString())}
				class="cursor-pointer opacity-0 transition-opacity duration-200 group-focus-within:opacity-100 group-hover:opacity-100"
				aria-label="copy beatmap id"
				{@attach tooltip('copy beatmap id')}>
				<Fa icon={faCopy} />
			</button>
			<a
				href="osu://b/{neighbor.BeatmapId}"
				class="opacity-0 transition-opacity duration-200 group-focus-within:opacity-100 group-hover:opacity-100"
				aria-label="open in osu!direct"
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
					&nbsp;{new Intl.NumberFormat(undefined, {
						minimumFractionDigits: 2,
						maximumFractionDigits: 2
					}).format(score.current)} points
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
								<h1 class="-mb-0.5 line-clamp-1 text-lg font-semibold break-all">
									{neighborInfo.title}
								</h1>
								<h2 class="-mt-0.5 line-clamp-1 text-base font-light break-all">
									[{neighborInfo.version}]
								</h2>
							</div>
							<p class="ml-3 inline-flex flex-col text-right text-base font-light">
								<legend class="text-xs">Similarity</legend>
								{new Intl.NumberFormat(undefined, {
									minimumFractionDigits: 2,
									maximumFractionDigits: 2
								}).format(neighborInfo.distance)}
							</p>
						</a>
					</li>
				{/each}
			</ul>
		</div>
	{/if}
</div>
