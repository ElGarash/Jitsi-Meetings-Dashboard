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
export const user = persistentWritable(null, {
	storage: sessionStorageAdapter('user')
});
export const popupOpen = persistentWritable(false, {
	storage: sessionStorageAdapter('popupOpen')
});
export const error = writable(null);

export const accessTokenStore = persistentWritable(null, {
	storage: sessionStorageAdapter('accessTokenStore')
});
