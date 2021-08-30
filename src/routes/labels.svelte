<script lang="ts">
	import { onMount } from 'svelte';
	import { Datatable, rows } from 'svelte-simple-datatables';
	import { labels, settings } from '../utils/stores';
	import load from '../utils/query';
	import { modal } from '../utils/stores';
	import { bind } from 'svelte-simple-modal';
	import requests from '../utils/requests';
	import Form from '../components/Form.svelte';
	import FormModal from '../components/FormModal.svelte';

	onMount(() => load('SELECT * FROM label').then((values) => labels.set(values)));

	let handleEdit = (event, index) => {
		modal.set(
			bind(Form, {
				index: index,
				resourceId: event.target.attributes['data-id'].value,
				resourceType: event.target.attributes['data-type'].value,
				formMethod: requests.patchResource
			})
		);
	};
</script>

<Datatable settings={$settings} data={$labels}>
	<thead>
		<th data-key="id">ID</th>
		<th data-key="name">Label</th>
		<th>Actions</th>
	</thead>
	<tbody>
		{#each $rows as { id, name }, i}
			<tr>
				<td>
					{id}
				</td>
				<td>
					{name}
				</td>
				<td>
					<button
						data-type="labels"
						data-id={id}
						on:click={(event, index = i) => handleEdit(event, index)}>Edit</button
					>
				</td>
			</tr>
		{/each}
	</tbody>
</Datatable>

<FormModal />

<style>
	td {
		text-align: center;
		padding: 4px 0;
	}
</style>
