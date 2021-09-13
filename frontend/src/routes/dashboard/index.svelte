<script>
  import { goto } from '$app/navigation';
</script>

<div>
  <button on:click={() => goto('/dashboard/meetings')}>Meetings</button>
  <button on:click={() => goto('/dashboard/participants')}>Participants</button>
  <button on:click={() => goto('/dashboard/labels')}>Labels</button>
</div>
