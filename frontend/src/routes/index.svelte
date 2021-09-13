<script lang="ts">
  import {
    selectingRoom,
    isAuthenticated,
    authToken,
    currentRoomID,
    meetingLabels,
    roomName
  } from '../utils/stores';
  import { postResource } from '../utils/requests';
  import { v4 as uuidv4 } from 'uuid';
  import { goto } from '$app/navigation';
  import query from '../utils/query';

  let activeMeetingsQuery = `SELECT m.id AS id, m.name AS name, group_concat(l.name) AS labels
                            FROM meeting m
                            LEFT JOIN meetings_labels ml ON ml.meeting_id = m.id
                            LEFT JOIN label l ON ml.label_id = l.id
                            WHERE m.date_ended is NULL
                            GROUP BY m.id, m.name`;

  let selectMeeting = (activeRoom) => {
    roomName.set(activeRoom.name);
    currentRoomID.set(activeRoom.id);
    meetingLabels.set(activeRoom.labels);
    selectingRoom.set(false);
  };

  let createMeeting = () => {
    roomName.set(uuidv4());
    postResource(
      'meetings',
      { roomName: $roomName, labels: $meetingLabels.split(', ') },
      $authToken
    )
      .then((response) => {
        currentRoomID.set(response.data.id);
      })
      .catch((error) => alert(error));
    selectingRoom.set(false);
  };
</script>

{#if $isAuthenticated}
  {#if $selectingRoom}
    <div>
      {#await query(activeMeetingsQuery) then activeRooms}
        <form on:submit|preventDefault={() => createMeeting()}>
          <input placeholder="Label1, Label2" bind:value={$meetingLabels} />
          <input type="submit" value="Create Room" />
        </form>
        <hr />
        <h2>Active Meetings</h2>
        {#each activeRooms as activeRoom}
          <div>
            <button on:click={() => selectMeeting(activeRoom)}
              >{activeRoom.labels > 0 ? activeRoom.labels : 'No labels'}</button
            >
          </div>
        {/each}
      {/await}
    </div>
  {:else}
    {goto($roomName)}
  {/if}
{:else}
  <h2>Please sign in to continue</h2>
{/if}
