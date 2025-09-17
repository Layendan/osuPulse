<script lang="ts">
	import icon from '$lib/assets/icon.png?enhanced';
	import { faDiscord, faGithub } from '@fortawesome/free-brands-svg-icons';
	import Fa from 'svelte-fa';

	import 'tippy.js/dist/tippy.css';

	let { children } = $props();
</script>

<nav class="navbar bg-base-200 mb-4 shadow-sm">
	<div class="container mx-auto inline-flex text-center">
		<a href="/" class="group inline-flex text-2xl font-bold">
			<enhanced:img
				src={icon}
				alt="icon"
				class="mr-2 size-10 transition-[scale] duration-200 group-hover:scale-110 motion-safe:group-hover:animate-pulse"
				width="80"
				height="80"></enhanced:img>
			<h1
				class="from-primary to-secondary inline-block bg-gradient-to-r bg-clip-text text-transparent">
				osu!Pulse
			</h1>
		</a>
	</div>
</nav>

{@render children?.()}

<footer
	class="footer footer-horizontal footer-center bg-base-200 text-base-content mt-4 rounded p-10">
	<nav>
		<div class="grid grid-flow-col gap-4">
			<a
				href="https://discord.gg/smyaYEM7V4"
				target="_blank"
				rel="noopener noreferrer"
				class="text-2xl">
				<Fa icon={faDiscord} />
			</a>
			<a
				href="https://github.com/Layendan/OsuPulse"
				target="_blank"
				rel="noopener noreferrer"
				class="text-2xl">
				<Fa icon={faGithub} />
			</a>
		</div>
	</nav>
	<aside>
		<p>Copyright © {new Date().getFullYear()} - All right reserved by Layendan</p>
	</aside>
</footer>
