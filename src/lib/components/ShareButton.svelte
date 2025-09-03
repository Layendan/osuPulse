<script lang="ts">
	import type { Attachment } from 'svelte/attachments';
	import type { Props } from 'tippy.js';

	import { faCheck } from '@fortawesome/free-solid-svg-icons';
	import { page } from '$app/state';
	import Fa from 'svelte-fa';
	import tippy from 'tippy.js';

	let clicked = $state(false);

	function updateContent() {
		return clicked ? 'copied to clipboard' : 'copy to clipboard';
	}

	function tooltip(
		content: string,
		props?: Partial<Props>,
		updateContent?: () => string
	): Attachment {
		return (element) => {
			const tooltip = tippy(element, { ...props, content });

			if (updateContent)
				$effect(() => {
					element && tooltip.setContent(updateContent());
				});

			return () => tooltip.destroy();
		};
	}
</script>

<button
	class="btn btn-soft btn-accent"
	class:btn-success={clicked}
	{@attach tooltip(
		updateContent(),
		{
			placement: 'bottom',
			hideOnClick: false
		},
		updateContent
	)}
	onclick={() => {
		navigator.clipboard.writeText(page.url.href);
		clicked = true;
		setTimeout(() => (clicked = false), 5000);
	}}>
	{#if clicked}
		<Fa icon={faCheck} />
	{/if}
	{clicked ? 'shared' : 'share'} page
</button>
