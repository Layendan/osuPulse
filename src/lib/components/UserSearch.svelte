<script lang="ts">
	import type { FormError } from '$lib';

	import { navigateToUser } from '../../routes/data.remote';

	let userError: string | null = $state(null);
</script>

<fieldset class="fieldset rounded-box border-base-300 bg-base-200 w-xs border p-4">
	<legend class="fieldset-legend">user</legend>
	<form
		{...navigateToUser.enhance(async ({ submit }) => {
			try {
				await submit();
			} catch (e) {
				console.error(e);
				userError = `${(e as FormError).status}: ${(e as FormError).body.message}`;
			}
		})}>
		<div class="join">
			<input
				name="user"
				type="text"
				class="input join-item input-ghost bg-base-100"
				placeholder="username or id" />
			<button type="submit" class="btn join-item btn-soft btn-primary">search</button>
		</div>
		{#if userError}
			<div class="validator-hint text-error visible">{userError}</div>
		{/if}
	</form>
	<p class="label">find maps that you might like</p>
</fieldset>
