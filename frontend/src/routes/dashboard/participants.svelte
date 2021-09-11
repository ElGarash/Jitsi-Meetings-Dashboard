<script lang="ts">
  import type { Participant } from '../../utils/types';
  import { onDestroy, onMount } from 'svelte';
  import { Datatable, rows } from 'svelte-simple-datatables';
  import { participants, settings, isAuthenticated, authToken } from '../../utils/stores';
  import query from '../../utils/query';
  import { modal } from '../../utils/stores';
  import { bind } from 'svelte-simple-modal';
  import { patchResource, postResource, deleteResource } from '../../utils/requests';
  import ParticipantsLabelsForm from '../../components/form/ParticipantsLabelsForm.svelte';
  import FormModal from '../../components/form/FormModal.svelte';

  onMount(() =>
    query('SELECT * FROM participant').then((values: Participant[]) => participants.set(values))
  );

  onDestroy(() => modal.set(null));

  let handleEdit = (event, index) => {
    modal.set(
      bind(ParticipantsLabelsForm, {
        index: index,
        resourceId: event.target.attributes['data-id'].value,
        resourceType: event.target.attributes['data-type'].value,
        formMethod: patchResource
      })
    );
  };

  let handleDelete = (event) => {
    // A UI optimization would be to use a modal form to confirm but I might not make it for now.
    let deleteConfirmation = confirm('Are you sure you want to delete this record?');
    if (deleteConfirmation) {
      let resourceId = event.target.attributes['data-id'].value;
      let resourceType = event.target.attributes['data-type'].value;
      deleteResource(resourceId, resourceType, $authToken)
        .then(() => {
          participants.set($participants.filter((element) => element.id != resourceId));
        })
        .catch((error) => alert(error));
    }
  };

  let handlePost = (event) => {
    modal.set(
      bind(ParticipantsLabelsForm, {
        resourceType: event.target.attributes['data-type'].value,
        formMethod: postResource
      })
    );
  };
</script>

{#if $isAuthenticated}
  <button data-type="participants" on:click={handlePost}> Add participant </button>
{/if}
<Datatable settings={$settings} data={$participants}>
  <thead>
    <th data-key="id">ID</th>
    <th data-key="name">Name</th>
    {#if $isAuthenticated}
      <th>Actions</th>
    {/if}
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
        {#if $isAuthenticated}
          <td>
            <button
              data-type="participants"
              data-id={id}
              on:click={(event, index = i) => handleEdit(event, index)}>Edit</button
            >
            <button data-type="participants" data-id={id} on:click={handleDelete}>Delete</button>
          </td>
        {/if}
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
