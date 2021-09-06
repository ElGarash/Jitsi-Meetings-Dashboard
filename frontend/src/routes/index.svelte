<script lang="ts">
  import Jitsi from '../components/meeting/Jitsi.svelte';
  import { selectingRoom, isAuthenticated, authToken } from '../utils/stores';
  import { getActiveRooms, postResource } from '../utils/requests';
  import { v4 as uuidv4 } from 'uuid';

  let currentRoomID;
  let meetingLabels;
  let roomName;

  let selectMeeting = (activeRoom) => {
    roomName = activeRoom.name;
    currentRoomID = activeRoom.id;
    meetingLabels = activeRoom.labels.join(', ');
    selectingRoom.set(false);
  };

  let createMeeting = () => {
    roomName = uuidv4();
    postResource('meetings', { roomName, labels: meetingLabels.split(', ') }, $authToken)
      .then((response) => {
        currentRoomID = response.data.id;
      })
      .catch((error) => alert(error));
    selectingRoom.set(false);
  };
</script>

{#if $isAuthenticated && $authToken}
  {#if $selectingRoom}
    <div>
      {#await getActiveRooms($authToken) then activeRooms}
        <form on:submit|preventDefault={() => createMeeting()}>
          <input placeholder="Label1, Label2" bind:value={meetingLabels} />
          <input type="submit" value="Create Room" />
        </form>
        <hr />
        <h2>Active Meetings</h2>
        {#each activeRooms as activeRoom}
          <div>
            <button on:click={() => selectMeeting(activeRoom)}
              >{activeRoom.labels.length > 0 ? activeRoom.labels : 'No labels'}</button
            >
          </div>
        {/each}
      {/await}
    </div>
  {:else}
    <Jitsi {currentRoomID} {meetingLabels} {roomName} />
  {/if}
{:else}
  <h2>Please sign in to continue</h2>
{/if}
