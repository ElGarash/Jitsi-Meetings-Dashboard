import { writable } from 'svelte/store';
import type { Writable } from 'svelte/store';
import type { Participant, Label } from './types';

export const modal = writable(null);

export let participants: Writable<Array<Participant>> = writable([]);

export let labels: Writable<Array<Label>> = writable([]);

export let settings = writable({ columnFilter: true });

export let selected = writable(null);
