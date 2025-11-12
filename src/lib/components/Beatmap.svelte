<script lang="ts">
	import type { UserNeighbor } from '$lib';
	import type { Attachment } from 'svelte/attachments';
	import type { Props } from 'tippy.js';

	import {
		faCertificate,
		faCopy,
		faFileArrowDown,
		faStar
	} from '@fortawesome/free-solid-svg-icons';
	import { resolve } from '$app/paths';
	import { interpolateRgb, scaleLinear } from 'd3';
	import { Beatmapset } from 'osu-api-v2-js';
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

	const { bg: starBg, fg: starFg } = getDifficultyColors(neighbor.Stars);

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

	function getDifficultyColors(stars: number) {
		const difficultyColourSpectrum = scaleLinear<string>()
			.domain([0.1, 1.25, 2, 2.5, 3.3, 4.2, 4.9, 5.8, 6.7, 7.7, 9])
			.clamp(true)
			.range([
				'#4290FB',
				'#4FC0FF',
				'#4FFFD5',
				'#7CFF4F',
				'#F6F05C',
				'#FF8068',
				'#FF4E6F',
				'#C645B8',
				'#6563DE',
				'#18158E',
				'#000000'
			])
			.interpolate(interpolateRgb.gamma(2.2));
		const foregroundColour = stars >= 6.5 ? 'hsl(45,100%,70%)' : 'hsl(200,10%,10%)';

		return {
			bg: difficultyColourSpectrum(stars),
			fg: foregroundColour
		};
	}
</script>

<div
	class="group ring-primary bg-base-300 relative grid h-full grid-cols-1 overflow-clip rounded-xl transition-all duration-200 focus-within:ring-2">
	<div
		class="relative inline-flex h-20 w-full flex-row overflow-clip rounded-xl sm:h-28"
		class:rounded-b-none={isDetailed}>
		<img
			src={buildUrl.beatmapsetCover(neighbor.BeatmapSetId)}
			class="absolute z-0 h-full w-full object-cover blur-xs"
			alt="beatmapset cover" />
		<div class="bg-base-100/80 pointer-events-none absolute inset-0 z-10"></div>
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
						<div
							class="badge badge-sm gap-1 font-bold uppercase"
							style="--badge-bg: {starBg}; --badge-fg: {starFg}">
							<Fa icon={faStar} />
							{neighbor.Stars.toFixed(2)}
						</div>
						{#if neighbor.LastUpdated && (neighbor.LastUpdated.getTime() - Date.now()) / (1000 * 3600 * 24) <= 30}
							<div class="badge-sm sm:badge badge-primary hidden font-bold uppercase">
								<Fa icon={faCertificate} />
								New
							</div>
						{/if}
					</div>
				</div>
				<div class="inline-flex flex-row items-center gap-1">
					<ul
						class="grid place-items-center gap-x-1 gap-y-0.5"
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
							<p class="text-right text-lg font-light">
								<legend class="text-xs">Exp.&nbsp;Accuracy</legend>
								{(neighbor.AvgAccuracy * 100).toFixed(2)}%
							</p>
						{/if}
						<p class="text-right text-lg font-light">
							<legend class="text-xs">Maximum&nbsp;PP</legend>
							{neighbor.PP.toFixed(0)}pp
						</p>
					</div>
				</div>
			</span>
		</a>
		<div
			class="bg-base-300 z-10 grid w-0 grid-rows-2 items-center justify-center rounded-xl py-2 transition-[width] duration-200 group-focus-within:w-14 group-hover:w-14 sm:w-4"
			class:rounded-b-none={isDetailed}>
			<a
				href="osu://b/{neighbor.BeatmapId}"
				class="opacity-0 transition-opacity duration-200 group-focus-within:opacity-100 group-hover:opacity-100"
				{@attach tooltip('open in osu!direct')}>
				<Fa icon={faFileArrowDown} />
			</a>
			<button
				onclick={() => navigator.clipboard.writeText(neighbor.BeatmapId.toString())}
				class="cursor-pointer opacity-0 transition-opacity duration-200 group-focus-within:opacity-100 group-hover:opacity-100"
				{@attach tooltip('copy beatmap id')}>
				<Fa icon={faCopy} />
			</button>
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
								<h1 class="-mb-0.5 line-clamp-1 text-lg font-semibold break-all">
									{neighborInfo.title}
								</h1>
								<h2 class="-mt-0.5 line-clamp-1 text-base font-light break-all">
									[{neighborInfo.version}]
								</h2>
							</div>
							<p class="ml-3 text-right text-base font-light">
								<legend class="text-xs">Similarity</legend>
								{neighborInfo.distance.toFixed(2)}
							</p>
						</a>
					</li>
				{/each}
			</ul>
		</div>
	{/if}
</div>
