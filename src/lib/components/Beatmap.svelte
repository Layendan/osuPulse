<script lang="ts">
	import type { UserNeighbor } from '$lib';
	import type { Attachment } from 'svelte/attachments';
	import type { Props } from 'tippy.js';

	import { faFileArrowDown } from '@fortawesome/free-solid-svg-icons';
	import { buildUrl, getEnumMods } from 'osu-web.js';
	import Fa from 'svelte-fa';
	import tippy from 'tippy.js';
	import Mod from './Mod.svelte';

	let {
		neighbor,
		rank
	}: {
		neighbor: Pick<UserNeighbor, 'BeatmapsetID' | 'BeatmapID' | 'Mods' | 'Title' | 'Version'> &
			Partial<Pick<UserNeighbor, 'AvgAccuracy'>>;
		rank: number;
	} = $props();

	function tooltip(content: string, props?: Partial<Props>): Attachment {
		return (element) => {
			const tooltip = tippy(element, { ...props, content });

			return () => tooltip.destroy();
		};
	}
</script>

<div
	class="group ring-primary relative inline-flex h-20 w-full flex-row overflow-clip rounded-xl focus-within:ring-2">
	<img
		src={buildUrl.beatmapsetCover(neighbor.BeatmapsetID)}
		class="absolute z-0 h-full w-full object-cover blur-xs"
		alt="beatmapset cover" />
	<div class="bg-base-100/80 pointer-events-none absolute inset-0 z-10"></div>
	<a
		href="/b/{neighbor.BeatmapID}?mods={neighbor.Mods}"
		class="relative z-10 inline-flex w-full flex-row outline-none">
		<div class="relative aspect-square h-full rounded-r-xl">
			<img
				src={buildUrl.beatmapsetThumbnail(neighbor.BeatmapsetID)}
				class="aspect-square h-full rounded-r-xl object-cover transition-all group-focus-within:brightness-[20%] group-hover:brightness-[20%]"
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
		class="bg-base-300 z-10 flex w-0 items-center justify-center rounded-xl transition-[width] duration-200 group-focus-within:w-14 group-hover:w-14 md:w-4">
		<a
			href="osu://b/{neighbor.BeatmapID}"
			class="opacity-0 transition-opacity duration-200 group-focus-within:opacity-100 group-hover:opacity-100"
			{@attach tooltip('open in osu!direct')}>
			<Fa icon={faFileArrowDown} />
		</a>
	</div>
</div>
