<script lang="ts">
	import { getDifficultyColors } from '$lib';
	import { faStar } from '@fortawesome/free-solid-svg-icons';
	import Fa from 'svelte-fa';

	const { stars }: { stars: number } = $props();

	const { bg: starBg, fg: starFg } = $derived(getDifficultyColors(stars));
</script>

<div
	class="badge badge-sm gap-1 border-none font-bold uppercase"
	style="--badge-bg: {starBg}; --badge-fg: {starFg}">
	<Fa icon={faStar} />
	{new Intl.NumberFormat(undefined, {
		minimumFractionDigits: 2,
		maximumFractionDigits: 2
	}).format(stars)}
</div>
