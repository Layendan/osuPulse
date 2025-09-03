<script lang="ts">
	import type { FormError } from '$lib';

	import { navigateToUserFlow } from '../../routes/data.remote';

	let flowError: string | null = $state(null);
</script>

<fieldset class="fieldset rounded-box border-base-300 bg-base-200 w-xs border p-4">
	<legend
		class="fieldset-legend from-primary to-secondary inline-block bg-gradient-to-r bg-clip-text text-transparent">
		pulse
	</legend>
	<form
		{...navigateToUserFlow.enhance(async ({ submit }) => {
			try {
				await submit();
			} catch (e) {
				console.error(e);
				flowError = (e as FormError).body.message;
			}
		})}>
		<div class="join">
			<input
				name="user"
				type="text"
				class="input join-item input-ghost bg-base-100"
				placeholder="user URL" />
			<button type="submit" class="btn join-item btn-soft btn-primary">search</button>
		</div>
		{#if flowError}
			<div class="validator-hint text-error visible">{flowError}</div>
		{/if}
	</form>
	<p class="label">playlist of similar beatmaps from your play session</p>
</fieldset>
