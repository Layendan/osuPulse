<script lang="ts">
	import '../app.css';
	import '../nprogress.css';

	import { navigating } from '$app/state';
	import NProgress from 'nprogress';

	import 'tippy.js/dist/tippy.css';

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

{@render children?.()}
