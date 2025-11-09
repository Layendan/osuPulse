<script lang="ts">
	import type { Attachment } from 'svelte/attachments';
	import type { Props } from 'tippy.js';

	import { ModsList } from '$lib';
	import { faFilter } from '@fortawesome/free-solid-svg-icons';
	import { getEnumMods, getModsEnum } from 'osu-web.js';
	import Fa from 'svelte-fa';
	import tippy from 'tippy.js';
	import Mod from './Mod.svelte';

	interface FilterProps {
		showNsfw: boolean;
		minStars: number | undefined;
		maxStars: number | undefined;
		minPp: number | undefined;
		maxPp: number | undefined;
		minHitLength: number | undefined;
		maxHitLength: number | undefined;
		minBpm: number | undefined;
		maxBpm: number | undefined;
		excludedMods: number | undefined;
		includedMods: number | undefined;
	}

	let {
		showNsfw = $bindable(true),
		minStars = $bindable(undefined),
		maxStars = $bindable(undefined),
		minPp = $bindable(undefined),
		maxPp = $bindable(undefined),
		minHitLength = $bindable(undefined),
		maxHitLength = $bindable(undefined),
		minBpm = $bindable(undefined),
		maxBpm = $bindable(undefined),
		excludedMods = $bindable(undefined),
		includedMods = $bindable(undefined)
	}: FilterProps = $props();

	let filterModal: HTMLDialogElement | undefined = $state(undefined);

	let showNsfwTemp: boolean = $state(showNsfw);

	let minStarsTemp: number | undefined = $state(minStars);
	let maxStarsTemp: number | undefined = $state(maxStars);

	let minPpTemp: number | undefined = $state(minPp);
	let maxPpTemp: number | undefined = $state(maxPp);

	let minHitLengthTemp: number | undefined = $state(minHitLength);
	let maxHitLengthTemp: number | undefined = $state(maxHitLength);

	let minBpmTemp: number | undefined = $state(minBpm);
	let maxBpmTemp: number | undefined = $state(maxBpm);

	let excludedModsTemp: number | undefined = $state(excludedMods);
	let excludedEnumMods = $derived(excludedModsTemp ? getEnumMods(excludedModsTemp) : []);
	let includedModsTemp: number | undefined = $state(includedMods);
	let includedEnumMods = $derived(includedModsTemp ? getEnumMods(includedModsTemp) : []);

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

<button
	onclick={() => filterModal?.showModal()}
	class="btn btn-primary btn-soft"
	{@attach tooltip('filtering options', { placement: 'bottom' })}>
	<Fa icon={faFilter} />
	filter
</button>
<dialog id="add_mod_modal" class="modal max-md:modal-bottom" bind:this={filterModal}>
	<div class="modal-box text-start">
		<form method="dialog">
			<button
				onclick={() => {
					showNsfwTemp = showNsfw;
					minStarsTemp = minStars;
					maxStarsTemp = maxStars;
					minPpTemp = minPp;
					maxPpTemp = maxPp;
					minHitLengthTemp = minHitLength;
					maxHitLengthTemp = maxHitLength;
					minBpmTemp = minBpm;
					maxBpmTemp = maxBpm;
					excludedModsTemp = excludedMods;
					includedModsTemp = includedMods;
				}}
				class="btn btn-sm btn-circle btn-ghost absolute top-2 right-2">✕</button>
		</form>

		<h3 class="mb-4 text-xl font-bold">filter settings</h3>

		<label class="label">
			<input type="checkbox" bind:checked={showNsfwTemp} class="toggle" />
			show explicit beatmaps
		</label>

		<div class="divider"></div>

		<h3 class="mb-3 text-lg font-bold">star range</h3>
		<div class="grid w-full max-w-sm grid-cols-2 gap-2">
			<label class="floating-label">
				<span class="label">min. stars</span>
				<input
					type="number"
					placeholder="minimum star value"
					bind:value={minStarsTemp}
					min="0"
					max={maxStarsTemp}
					class="input" />
			</label>

			<label class="floating-label">
				<span class="label">max. stars</span>
				<input
					type="number"
					placeholder="maximum star value"
					bind:value={maxStarsTemp}
					min={minStarsTemp}
					class="input" />
			</label>
		</div>

		<div class="divider"></div>

		<h3 class="mb-3 text-lg font-bold">performance points range</h3>
		<div class="grid w-full max-w-sm grid-cols-2 gap-2">
			<label class="floating-label">
				<span class="label">min. pp</span>
				<input
					type="number"
					placeholder="minimum pp value"
					bind:value={minPpTemp}
					min="0"
					max={maxPpTemp}
					step="50"
					class="input" />
			</label>

			<label class="floating-label">
				<span class="label">max. pp</span>
				<input
					type="number"
					placeholder="maximum pp value"
					bind:value={maxPpTemp}
					min={minPpTemp}
					step="50"
					class="input" />
			</label>
		</div>

		<div class="divider"></div>

		<h3 class="mb-3 text-lg font-bold">song length range (seconds)</h3>
		<div class="grid w-full max-w-sm grid-cols-2 gap-2">
			<label class="floating-label">
				<span class="label">min. length</span>
				<input
					type="number"
					placeholder="minimum length"
					bind:value={minHitLengthTemp}
					min="0"
					max={maxHitLengthTemp}
					step="30"
					class="input" />
			</label>

			<label class="floating-label">
				<span class="label">max. length</span>
				<input
					type="number"
					placeholder="maximum length"
					bind:value={maxHitLengthTemp}
					min={minHitLengthTemp}
					step="30"
					class="input" />
			</label>
		</div>

		<div class="divider"></div>

		<h3 class="mb-3 text-lg font-bold">song bpm</h3>
		<div class="grid w-full max-w-sm grid-cols-2 gap-2">
			<label class="floating-label">
				<span class="label">min. bpm</span>
				<input
					type="number"
					placeholder="minimum bpm"
					bind:value={minBpmTemp}
					min="0"
					max={maxBpmTemp}
					step="10"
					class="input" />
			</label>

			<label class="floating-label">
				<span class="label">max. bpm</span>
				<input
					type="number"
					placeholder="maximum bpm"
					bind:value={maxBpmTemp}
					min={minBpmTemp}
					step="10"
					class="input" />
			</label>
		</div>

		<div class="divider"></div>

		<h3 class="mb-2 text-lg font-bold">exclude mods</h3>
		<ul class="mb-2 inline-flex flex-row flex-wrap gap-2">
			{#each ModsList as mod (mod)}
				{@const [modVal] = getEnumMods(mod)}
				{@const included = excludedEnumMods.includes(modVal)}
				{@const updateContent = () => (included ? `remove ${modVal}` : `add ${modVal}`)}
				<li>
					<button
						onclick={() => {
							if (included)
								excludedModsTemp = getModsEnum(excludedEnumMods.filter((item) => item !== modVal));
							else {
								excludedModsTemp = getModsEnum([...excludedEnumMods, modVal]);
							}
						}}
						class="cursor-pointer transition-opacity"
						class:opacity-20={!included}>
						<Mod
							mod={modVal}
							{@attach tooltip(
								updateContent(),
								{
									appendTo: filterModal
								},
								updateContent
							)} />
					</button>
				</li>
			{/each}
			<li>
				<button
					onclick={() => {
						excludedModsTemp = undefined;
					}}
					class="btn btn-warning btn-soft">
					reset
				</button>
			</li>
			<li>
				<button
					onclick={() => {
						excludedModsTemp = ModsList.reduce((partialSum, a) => partialSum + a, 0);
					}}
					class="btn btn-accent btn-soft">
					exclude all
				</button>
			</li>
		</ul>

		<h3 class="mb-2 text-lg font-bold">include mods</h3>
		<ul class="inline-flex flex-row flex-wrap gap-2">
			{#each ModsList as mod (mod)}
				{@const [modVal] = getEnumMods(mod)}
				{@const included = includedEnumMods.includes(modVal)}
				{@const updateContent = () => (included ? `remove ${modVal}` : `add ${modVal}`)}
				<li>
					<button
						onclick={() => {
							if (included)
								includedModsTemp = getModsEnum(includedEnumMods.filter((item) => item !== modVal));
							else {
								includedModsTemp = getModsEnum(
									[...includedEnumMods, modVal].filter((item) => {
										if (modVal === 'DT' || modVal === 'NC') return item !== 'HT' && item !== 'DC';
										else if (modVal === 'HT' || modVal === 'DC')
											return item !== 'DT' && item !== 'NC';
										else if (modVal === 'HR') return item !== 'EZ';
										else if (modVal === 'EZ') return item !== 'HR';
										else return true;
									})
								);
							}
							includedEnumMods = getEnumMods(includedModsTemp);
						}}
						class="cursor-pointer transition-opacity"
						class:opacity-20={!included}>
						<Mod
							mod={modVal}
							{@attach tooltip(
								updateContent(),
								{
									appendTo: filterModal
								},
								updateContent
							)} />
					</button>
				</li>
			{/each}
			<li>
				<button
					onclick={() => {
						includedModsTemp = undefined;
						includedEnumMods = [];
					}}
					class="btn btn-warning btn-soft">
					reset
				</button>
			</li>
		</ul>

		<div class="modal-action">
			<form method="dialog">
				<button
					onclick={() => {
						showNsfw = showNsfwTemp;
						if (minStarsTemp)
							minStars = maxStarsTemp ? Math.min(minStarsTemp, maxStarsTemp) : minStarsTemp;
						if (maxStarsTemp)
							maxStars = minStarsTemp ? Math.max(minStarsTemp, maxStarsTemp) : maxStarsTemp;
						if (minPpTemp) minPp = maxPpTemp ? Math.min(minPpTemp, maxPpTemp) : minPpTemp;
						if (maxPpTemp) maxPp = minPpTemp ? Math.max(minPpTemp, maxPpTemp) : maxPpTemp;
						if (minHitLengthTemp)
							minHitLength = maxHitLengthTemp
								? Math.min(minHitLengthTemp, maxHitLengthTemp)
								: minHitLengthTemp;
						if (maxHitLengthTemp)
							maxHitLength = minHitLengthTemp
								? Math.max(minHitLengthTemp, maxHitLengthTemp)
								: maxHitLengthTemp;
						if (minBpmTemp) minBpm = maxBpmTemp ? Math.min(minBpmTemp, maxBpmTemp) : minBpmTemp;
						if (maxBpmTemp) maxBpm = minBpmTemp ? Math.max(minBpmTemp, maxBpmTemp) : maxBpmTemp;
						excludedMods = excludedModsTemp;
						includedMods = includedModsTemp;
					}}
					class="btn btn-primary btn-soft">
					save
				</button>
			</form>
		</div>
	</div>

	<form method="dialog" class="modal-backdrop">
		<button
			onclick={() => {
				showNsfwTemp = showNsfw;
				minStarsTemp = minStars;
				maxStarsTemp = maxStars;
				minPpTemp = minPp;
				maxPpTemp = maxPp;
				minHitLengthTemp = minHitLength;
				maxHitLengthTemp = maxHitLength;
				minBpmTemp = minBpm;
				maxBpmTemp = maxBpm;
				excludedModsTemp = excludedMods;
				includedModsTemp = includedMods;
			}}>close</button>
	</form>
</dialog>
