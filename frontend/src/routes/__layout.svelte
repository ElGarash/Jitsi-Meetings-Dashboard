<script>
  import { goto } from '$app/navigation';
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
    <button on:click={() => goto('/')}>Home</button>
    <button on:click={() => goto('/meeting')}>Rooms Panel</button>
    <button on:click={() => goto('/dashboard')}>Dashboard</button>

    {#if $isAuthenticated}
      <button on:click={() => logout()}>Logout</button>
    {:else}
      <button on:click={() => login()}>Login</button>
    {/if}
  </div>
</header>

<slot />
