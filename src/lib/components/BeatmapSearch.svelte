<script lang="ts">
	import type { FormError } from '$lib';

	import { navigateToBeatmap } from '../../routes/data.remote';

	let submitting: boolean = $state(false);
	let beatmapError: string | null = $state(null);
</script>

<fieldset class="fieldset rounded-box border-base-300 bg-base-200 w-xs border p-4">
	<legend class="fieldset-legend">beatmap</legend>
	<form
		{...navigateToBeatmap.enhance(async ({ submit }) => {
			try {
				submitting = true;
				await submit();
			} catch (e) {
				console.error(e);
				beatmapError = (e as FormError).body.message;
			} finally {
				submitting = false;
			}
		})}>
		<div class="join">
			<input
				name="beatmap"
				type="text"
				class="input join-item input-ghost bg-base-100"
				placeholder="beatmap URL" />
			<button
				type="submit"
				class="btn join-item btn-soft btn-primary"
				disabled={submitting}
				aria-disabled={submitting}>
				{#if submitting}
					<span class="loading loading-ring"></span>
				{/if}
				search
			</button>
		</div>
		{#if beatmapError}
			<div class="validator-hint text-error visible">{beatmapError}</div>
		{/if}
	</form>
	<p class="label">search for similar beatmaps</p>
</fieldset>
