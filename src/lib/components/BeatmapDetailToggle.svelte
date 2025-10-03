<script lang="ts">
	import type { Attachment } from 'svelte/attachments';
	import type { Props } from 'tippy.js';

	import { faGrip, faGripLines } from '@fortawesome/free-solid-svg-icons';
	import { onMount } from 'svelte';
	import Fa from 'svelte-fa';
	import tippy from 'tippy.js';

	let { isDetailed = $bindable() }: { isDetailed: boolean } = $props();

	onMount(() => {
		isDetailed = window.localStorage.getItem('isDetailed') === 'true' ? true : false;
		$effect(() => window.localStorage.setItem('isDetailed', `${isDetailed}`));
	});

	function tooltip(content: string, props?: Partial<Props>): Attachment {
		return (element) => {
			const tooltip = tippy(element, { ...props, content });

			return () => tooltip.destroy();
		};
	}
</script>

<label
	class="toggle toggle-xl text-base-content my-auto text-xl"
	{@attach tooltip('toggle beatmap details', { placement: 'bottom' })}>
	<input type="checkbox" bind:checked={isDetailed} />
	<Fa icon={faGripLines} class="m-auto" />
	<Fa icon={faGrip} class="m-auto" />
</label>
