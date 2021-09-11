<script lang="ts">
  import Jitsi from '../components/meeting/Jitsi.svelte';
  import { isAuthenticated, selectingRoom } from '../utils/stores';
</script>

{#if !$selectingRoom && $isAuthenticated}
  <Jitsi />
{:else if !$isAuthenticated}
  <h2>You must login before starting a meeting</h2>
{:else if $selectingRoom}
  <h2>Please select or create a room at the index page</h2>
{/if}
