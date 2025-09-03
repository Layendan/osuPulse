<script lang="ts">
	import '../app.css';
	import '../nprogress.css';

	import favicon from '$lib/assets/favicon.webp';
	import { navigating } from '$app/state';
	import NProgress from 'nprogress';

	let { children } = $props();

	NProgress.configure({
		minimum: 0.16,
		showSpinner: false
	});

	$effect(() => {
		if (navigating.to) NProgress.start();
		else NProgress.done();
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{@render children?.()}
