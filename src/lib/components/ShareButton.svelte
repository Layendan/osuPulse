<script lang="ts">
	import type { Attachment } from 'svelte/attachments';
	import type { Props } from 'tippy.js';

	import { faCheck, faLink } from '@fortawesome/free-solid-svg-icons';
	import { page } from '$app/state';
	import Fa from 'svelte-fa';
	import tippy from 'tippy.js';

	let { url }: { url?: string } = $props();

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
					if (element) tooltip.setContent(updateContent());
				});

			return () => tooltip.destroy();
		};
	}
</script>

<button
	class="btn btn-soft btn-accent group"
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
		navigator.clipboard.writeText(url ?? page.url.href);
		clicked = true;
		setTimeout(() => (clicked = false), 5000);
	}}>
	<Fa icon={clicked ? faCheck : faLink} class="group-hover:animate-bounce" />
	{clicked ? 'shared' : 'share'} page
</button>
