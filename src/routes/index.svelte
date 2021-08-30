<script lang="ts">
	import { onMount } from 'svelte';
	import { participants } from '../utils/stores';

	import load from '../utils/query';
	onMount(() => {
		load(`SELECT * FROM participant`).then((values) => participants.set(values));
	});
</script>

<h2>Hello</h2>
