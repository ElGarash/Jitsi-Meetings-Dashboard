<script lang="ts">
	import { onMount } from 'svelte';
	import { isAuthenticated } from '../utils/stores';
	import auth from '../utils/authentication';

	let auth0Client;

	function login() {
		auth.loginWithPopup(auth0Client);
	}

	function logout() {
		auth.logout(auth0Client);
	}

	onMount(async () => {
		auth0Client = await auth.createClient();
	});
</script>

<nav>
	<div>
		{#if $isAuthenticated}
			<button on:click={logout}>Logout</button>
		{:else}
			<button on:click={login}>Login</button>
		{/if}
	</div>
</nav>
<slot />
