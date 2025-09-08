<script lang="ts">
	import type { RemoteQuery } from '@sveltejs/kit';
	import type { Attachment } from 'svelte/attachments';
	import type { Props } from 'tippy.js';

	import { faRotate } from '@fortawesome/free-solid-svg-icons';
	import Fa from 'svelte-fa';
	import tippy from 'tippy.js';

	let { queryFunction }: { queryFunction: RemoteQuery<unknown> } = $props();

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
	onclick={() => queryFunction.refresh()}
	class="btn btn-warning btn-soft group"
	disabled={queryFunction.loading}
	aria-disabled={queryFunction.loading}
	{@attach tooltip('refresh osu! data', {
		placement: 'bottom'
	})}>
	{#if queryFunction.loading}
		<span class="loading loading-ring"></span>
	{:else}
		<Fa icon={faRotate} class="group-hover:animate-spin" />
	{/if}
	refetch data
</button>
