<script lang="ts">
	import type { Label } from 'src/utils/types';
	import { onMount } from 'svelte';
	import { Datatable, rows } from 'svelte-simple-datatables';
	import { isAuthenticated, labels, settings } from '../../utils/stores';
	import query from '../../utils/query';
	import { modal } from '../../utils/stores';
	import { bind } from 'svelte-simple-modal';
	import requests from '../../utils/requests';
	import ParticipantsLabelsForm from '../../components/form/ParticipantsLabelsForm.svelte';
	import FormModal from '../../components/form/FormModal.svelte';

	onMount(() => query('SELECT * FROM label').then((values: Label[]) => labels.set(values)));

	let handleEdit = (event, index) => {
		modal.set(
			bind(ParticipantsLabelsForm, {
				index: index,
				resourceId: event.target.attributes['data-id'].value,
				resourceType: event.target.attributes['data-type'].value,
				formMethod: requests.patchResource
			})
		);
	};
	let handleDelete = (event) => {
		// A UI optimization would be to use a modal form to confirm but I might not make it for now.
		let deleteConfirmation = confirm('Are you sure you want to delete this record?');
		if (deleteConfirmation) {
			let resourceId = event.target.attributes['data-id'].value;
			let resourceType = event.target.attributes['data-type'].value;
			requests
				.deleteResource(resourceId, resourceType)
				.then(() => {
					labels.set($labels.filter((element) => element.id != resourceId));
				})
				.catch((error) => alert(error));
		}
	};

	let handlePost = (event) => {
		modal.set(
			bind(ParticipantsLabelsForm, {
				resourceType: event.target.attributes['data-type'].value,
				formMethod: requests.postResource
			})
		);
	};
</script>

{#if $isAuthenticated}
	<button data-type="labels" on:click={handlePost}> Add label </button>

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
						<button data-type="labels" data-id={id} on:click={handleDelete}>Delete</button>
					</td>
				</tr>
			{/each}
		</tbody>
	</Datatable>

	<FormModal />
{:else}
	<h2>You must be authenticated to access the dashboard</h2>
{/if}

<style>
	td {
		text-align: center;
		padding: 4px 0;
	}
</style>
