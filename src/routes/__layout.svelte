<script>
	import { createAuth } from '../utils/authentication';
	import { isAuthenticated } from '../utils/stores';

	const { login, logout } = createAuth({
		domain: 'elgarash.us.auth0.com',
		client_id: 'vV2NGwEyc9tL75dBW9017SBR8oqhAzWA',
		audience: 'AzureServerlessFunction'
	});
</script>

<header>
	<div>
		{#if $isAuthenticated}
			<button on:click={() => logout()}>Logout</button>
		{:else}
			<button on:click={() => login()}>Login</button>
		{/if}
	</div>
</header>

<slot />
