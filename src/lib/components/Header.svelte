<script lang="ts">
	import type { Beatmap, User } from 'osu-api-v2-js';

	import { faStar } from '@fortawesome/free-solid-svg-icons';
	import { buildUrl } from 'osu-web.js';
	import Fa from 'svelte-fa';

	let { data }: { data: Beatmap.Extended.WithFailtimesOwnersMaxcomboBeatmapset | User.Extended } =
		$props();

	function isBeatmap(
		data: unknown
	): data is Beatmap.Extended.WithFailtimesOwnersMaxcomboBeatmapset {
		return typeof data === 'object' && data !== null && 'beatmapset' in data;
	}
</script>

{#if isBeatmap(data)}
	<a
		href={buildUrl.beatmap(data.id)}
		target="_blank"
		rel="noopener noreferrer external"
		class="relative grid w-full place-items-center px-4">
		<img
			src={data.beatmapset.covers['cover@2x']}
			class="absolute h-full w-full object-cover"
			alt="beatmap cover"
			fetchpriority="high" />
		<div class="bg-base-100/80 absolute h-full w-full backdrop-blur-xs"></div>
		<div class="z-10 my-2 inline-flex items-center gap-4 sm:max-w-10/12 lg:max-w-4/5 xl:max-w-3/5">
			<img
				src={data.beatmapset.covers['card@2x']}
				class="aspect-square size-20 rounded-2xl object-cover md:size-32 md:rounded-4xl"
				alt="beatmap card" />
			<div class="inline-flex flex-col gap-2">
				<span class="inline-flex flex-col gap-0">
					<h1 class="text-3xl font-bold md:text-5xl">{data.beatmapset.title}</h1>
					<h2 class="text-xl font-light md:text-2xl">[{data.version}]</h2>
				</span>
				<span class="inline-flex gap-4">
					<h2 class="text-3xl font-light">
						<legend class="text-xs">Star Rating</legend>
						<span class="inline-flex flex-row items-center gap-1">
							<Fa icon={faStar} class="text-xl" />
							{new Intl.NumberFormat(undefined, {
								minimumFractionDigits: 2,
								maximumFractionDigits: 2
							}).format(data.difficulty_rating)}
						</span>
					</h2>
					{#if data.bpm}
						<h2 class="text-3xl font-light">
							<legend class="text-xs">Beats Per Minute</legend>
							{new Intl.NumberFormat().format(data.bpm)}bpm
						</h2>
					{/if}
				</span>
			</div>
		</div>
	</a>
{:else}
	{@const globalRank = data.statistics.global_rank}
	{@const countryRank = data.statistics.country_rank}
	{@const pp = data.statistics.pp}

	<a
		href={buildUrl.user(data.id)}
		target="_blank"
		rel="noopener noreferrer external"
		class="relative grid w-full place-items-center px-4">
		<img
			src={data.cover.custom_url ?? data.cover.url}
			class="absolute h-full w-full object-cover"
			alt="user cover"
			fetchpriority="high" />
		<div class="bg-base-100/80 absolute h-full w-full backdrop-blur-xs"></div>
		<div class="z-10 my-2 inline-flex items-center gap-4">
			<img
				src={data.avatar_url}
				class="aspect-square size-20 rounded-2xl md:size-32 md:rounded-4xl"
				alt="user avatar" />
			<div class="inline-flex flex-col gap-2">
				<h1 class="text-3xl font-bold md:text-5xl">{data.username}</h1>
				<span class="inline-flex gap-4">
					<h2 class="text-3xl font-light">
						<legend class="text-xs">Global Ranking</legend>
						{#if globalRank}
							#{new Intl.NumberFormat().format(globalRank)}
						{:else}
							-
						{/if}
					</h2>
					<h2 class="text-3xl font-light max-md:hidden">
						<legend class="text-xs">Country Ranking</legend>
						{#if countryRank}
							#{new Intl.NumberFormat().format(countryRank)}
						{:else}
							-
						{/if}
					</h2>
					<h2 class="text-3xl font-light max-sm:hidden">
						<legend class="text-xs">Performance Points</legend>
						{#if pp}
							{new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(pp)}pp
						{:else}
							-
						{/if}
					</h2>
				</span>
			</div>
		</div>
	</a>
{/if}
