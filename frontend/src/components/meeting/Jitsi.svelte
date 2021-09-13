<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import {
    userInfo,
    selectingRoom,
    authToken,
    currentRoomID,
    meetingLabels,
    roomName
  } from '../../utils/stores';
  import { patchResource } from '../../utils/requests';
  import { goto } from '$app/navigation';

  let api;
  let streamingStatus = false;
  let participants = new Set();

  function startMeeting(roomName) {
    let domain = 'meet.jit.si';
    let options = {
      roomName: roomName,
      height: '100%',
      width: '100%',

      parentNode: document.getElementById('meeting'),
      userInfo: {
        displayName: $userInfo['name']
      },
      configOverwrite: {
        startWithAudioMuted: false,
        startWithVideoMuted: true,
        requireDisplayName: true
      },
      interfaceConfigOverwrite: {
        SHOW_CHROME_EXTENSION_BANNER: false
      },
      onload: () => {
        api.addEventListener('participantJoined', (participant) => {
          participants.add(participant.id);
        });

        api.addEventListener('participantLeft', async () => {
          if (participants.size > 0 && api.getNumberOfParticipants() === 1) {
            patchResource($currentRoomID, 'meetings', { endingFlag: true }, $authToken).catch(
              (error) => alert(error)
            );
          }
        });

        api.addEventListener('videoConferenceLeft', () => {
          goto(window.location.origin + '/meeting/outro');
        });
      }
    };
    api = new JitsiMeetExternalAPI(domain, options);
    api.executeCommand('subject', $meetingLabels);
  }

  onMount(() => {
    startMeeting($roomName);
  });

  onDestroy(() => {
    if (api) {
      api.dispose();
    }
  });
  let handleStreaming = () => {
    if (streamingStatus) {
      api.executeCommand('stopRecording', 'stream');
      streamingStatus = false;
    } else {
      if (!api.getNumberOfParticipants()) {
        alert("You aren't in a meeting");
        return;
      }
      api.executeCommand('startRecording', {
        mode: `stream`,
        shouldShare: true,
        youtubeStreamKey: `8fx0-x8a3-jyr6-sp69-dmqw`
      });
      streamingStatus = true;
    }
  };

  const sendParticipants = () => {
    let participant_names = api.getParticipantsInfo().map((p) => p.displayName);

    patchResource(
      $currentRoomID,
      'meetings',
      { participants: participant_names },
      $authToken
    ).catch((error) => alert(error));
  };

  const leaveRoom = () => {
    if (api) {
      selectingRoom.set(true);
      meetingLabels.set(null);
      api.dispose();
      goto(window.location.origin + '/meeting');
    }
  };
</script>

<div id="meeting-nav-bar">
  <button on:click={handleStreaming}>{!streamingStatus ? 'Start' : 'Stop'} Streaming</button>
  <button on:click={sendParticipants}>Send Participants</button>
  <button on:click={leaveRoom}>Leave Room</button>
</div>

<div id="meeting" />

<style>
  #meeting {
    width: 100%;
    height: 90%;
  }
</style>
