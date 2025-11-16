<script lang="ts">
	import type { BeatmapSetSearch } from '$lib';
	import type { Attachment } from 'svelte/attachments';
	import type { Props } from 'tippy.js';

	import { getDifficultyColors } from '$lib';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import tippy from 'tippy.js';
	import DifficultyPill from './DifficultyPill.svelte';
	import OsuModeLogo from './OsuModeLogo.svelte';

	const { difficulty }: { difficulty: BeatmapSetSearch } = $props();

	const fillColour = $derived(getDifficultyColors(difficulty.Stars).bg);
	const selected = $derived(page.params.beatmapId === difficulty.BeatmapId.toString());

	let tooltipElement: HTMLDivElement | undefined = $state(undefined);

	function tooltip(props?: Partial<Props>): Attachment {
		return (element) => {
			const tooltip = tippy(element, { ...props, content: tooltipElement });
			tooltipElement?.style.setProperty('display', 'inline-flex');

			return () => tooltip.destroy();
		};
	}
</script>

<a
	href={resolve('/(app)/b/[beatmapId=integer]', { beatmapId: difficulty.BeatmapId.toString() })}
	class="btn btn-square btn-ghost outline-base-content p-1 text-base opacity-20 transition-opacity hover:opacity-100"
	class:outline-2={selected}
	class:opacity-100={selected}
	style="color: {fillColour};"
	aria-label="navigate to beatmap {difficulty.Version}"
	{@attach tooltip({ allowHTML: true })}>
	<OsuModeLogo />
</a>

<div
	bind:this={tooltipElement}
	class="hidden flex-row justify-center gap-2 text-center align-middle">
	{difficulty.Version}
	<DifficultyPill stars={difficulty.Stars} />
</div>
