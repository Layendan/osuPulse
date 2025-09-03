<script lang="ts">
	import type { Mod } from 'osu-web.js';
	import type { HTMLAttributes } from 'svelte/elements';

	import { isDifficultyIncrease } from '$lib';

	let { mod, ...props }: { mod: Mod } & HTMLAttributes<HTMLDivElement> = $props();

	const isModDifficultyIncrease: boolean = $derived(isDifficultyIncrease(mod));
</script>

<div
	class="mask mask-hexagon-2 grid aspect-square size-10 items-center justify-center {isModDifficultyIncrease
		? 'bg-[#ff6666]'
		: 'bg-[#b3ff66]'}"
	{...props}>
	<img src="/mod-{mod.toLowerCase()}.svg" class="w-10 opacity-60" alt="{mod} mod icon" />
</div>
