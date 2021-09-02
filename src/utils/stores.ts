import { readable, writable } from 'svelte/store';
import type { Writable } from 'svelte/store';
import type { Participant, Label, Meeting } from './types';

// Dashboard stores
export const modal = writable(null);

export const participants: Writable<Array<Participant>> = writable([]);

export const labels: Writable<Array<Label>> = writable([]);

export const meetings: Writable<Array<Meeting>> = writable([]);

export const settings = readable({ columnFilter: true });
