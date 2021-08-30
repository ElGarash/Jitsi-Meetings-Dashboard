<script lang="ts">
	import { onMount } from 'svelte';
	import { Datatable, rows } from 'svelte-simple-datatables';
	import { meetings, settings } from '../utils/stores';
	import query from '../utils/query';
	import { modal } from '../utils/stores';
	import { bind } from 'svelte-simple-modal';
	import requests from '../utils/requests';
	import MeetingsForm from '../components/form/MeetingsForm.svelte';
	import FormModal from '../components/form/FormModal.svelte';

	onMount(() => query('SELECT * FROM meeting').then((values) => meetings.set(values)));

	let handleEdit = (event, index) => {
		modal.set(
			bind(MeetingsForm, {
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
					meetings.set($meetings.filter((element) => element.id != resourceId));
				})
				.catch((error) => alert(error));
		}
	};
</script>

<Datatable settings={$settings} data={$meetings}>
	<thead>
		<th data-key="id">ID</th>
		<th data-key="name">Name</th>
		<th data-key="date_started">Start date</th>
		<th data-key="date_ended">End date</th>
		<th data-key="link">YouTube link</th>
		<th>Actions</th>
	</thead>
	<tbody>
		{#each $rows as { id, name, date_started, date_ended, link }, i}
			<tr>
				<td>
					{id}
				</td>
				<td>
					{name}
				</td>
				<td>
					{date_started}
				</td>
				<td>
					{date_ended}
				</td>
				<td>
					{link}
				</td>
				<td>
					<button
						data-type="meetings"
						data-id={id}
						on:click={(event, index = i) => handleEdit(event, index)}>Edit</button
					>
					<button data-type="meetings" data-id={id} on:click={handleDelete}>Delete</button>
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
