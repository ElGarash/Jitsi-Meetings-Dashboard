import { readable, writable } from 'svelte/store';
import type { Writable } from 'svelte/store';
import type { Participant, Label, Meeting } from './types';

export const modal = writable(null);

export let participants: Writable<Array<Participant>> = writable([]);

export let labels: Writable<Array<Label>> = writable([]);

export let meetings: Writable<Array<Meeting>> = writable([]);

export const settings = readable({ columnFilter: true });
