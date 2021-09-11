import { readable, writable } from 'svelte/store';
import type { Writable } from 'svelte/store';
import type { Participant, Label, Meeting } from './types';
import { persistentWritable, sessionStorageAdapter } from 'svelte-persistent-writable';

// Dashboard stores
export const modal = writable(null);
export const participants: Writable<Array<Participant>> = writable([]);
export const labels: Writable<Array<Label>> = writable([]);
export const meetings: Writable<Array<Meeting>> = writable([]);
export const settings = readable({ columnFilter: true });

// Auth0 stores
export const isAuthenticated = persistentWritable(false, {
  storage: sessionStorageAdapter('isAuthenticated')
});

export const isLoading = persistentWritable(true, {
  storage: sessionStorageAdapter('isLoading')
});
export const userInfo = persistentWritable(
  {},
  {
    storage: sessionStorageAdapter('userInfo')
  }
);

export const authError = persistentWritable(null, {
  storage: sessionStorageAdapter('authError')
});

export const authToken = persistentWritable('', {
  storage: sessionStorageAdapter('authToken')
});

// Jitsi stores
export const selectingRoom = writable(true);
export const currentRoomID = writable(null)
export const meetingLabels = writable("")
export const roomName = writable("")
