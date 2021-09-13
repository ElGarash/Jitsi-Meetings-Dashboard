<script lang="ts">
  import { isAuthenticated } from '../utils/stores';
</script>

{#if $isAuthenticated}
  <h2>Lorem Ipsum</h2>
{:else}
  <h2>You aren't signed in</h2>
{/if}
