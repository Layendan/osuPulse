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
		excludedMods: number | undefined;
		includedMods: number | undefined;
	}

	let { excludedMods = $bindable(), includedMods = $bindable() }: FilterProps = $props();

	let filterModal: HTMLDialogElement | undefined = $state(undefined);
	let excludedModsTemp: number | undefined = $state(undefined);
	let excludedEnumMods = $derived(excludedModsTemp ? getEnumMods(excludedModsTemp) : []);
	let includedModsTemp: number | undefined = $state(undefined);
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

<button onclick={() => filterModal?.showModal()} class="btn btn-primary btn-soft">
	<Fa icon={faFilter} />
	filter
</button>
<dialog id="add_mod_modal" class="modal" bind:this={filterModal}>
	<div class="modal-box">
		<form method="dialog">
			<button class="btn btn-sm btn-circle btn-ghost absolute top-2 right-2">✕</button>
		</form>

		<h3 class="mb-2 text-lg font-bold">exclude mods</h3>
		<ul class="inline-flex flex-row gap-2">
			{#each ModsList as mod (mod)}
				{@const [modVal] = getEnumMods(mod)}
				{@const included = excludedEnumMods.includes(modVal)}
				{@const updateContent = () => (included ? `remove ${modVal}` : `add ${modVal}`)}
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
			{/each}
			<button
				onclick={() => {
					excludedModsTemp = undefined;
				}}
				class="btn btn-warning btn-soft">
				reset
			</button>
			<button
				onclick={() => {
					excludedModsTemp = ModsList.reduce((partialSum, a) => partialSum + a, 0);
				}}
				class="btn btn-accent btn-soft">
				exclude all
			</button>
		</ul>

		<h3 class="mb-2 text-lg font-bold">include mods</h3>
		<ul class="inline-flex flex-row gap-2">
			{#each ModsList as mod (mod)}
				{@const [modVal] = getEnumMods(mod)}
				{@const included = includedEnumMods.includes(modVal)}
				{@const updateContent = () => (included ? `remove ${modVal}` : `add ${modVal}`)}
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
			{/each}
			<button
				onclick={() => {
					includedMods = undefined;
					includedEnumMods = [];
				}}
				class="btn btn-warning btn-soft">
				reset
			</button>
		</ul>

		<div class="modal-action">
			<form method="dialog">
				<button
					onclick={() => {
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
		<button>close</button>
	</form>
</dialog>
