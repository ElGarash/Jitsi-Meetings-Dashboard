<script lang="ts">
	import { onMount } from 'svelte';

	import load from '../utils/query';
	onMount(() => {
		load(`SELECT * FROM participant`);
	});
</script>

<h2>Hello</h2>
