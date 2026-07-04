import { writable } from 'svelte/store';

export const currentPage = writable('dashboard');
export const serverStatus = writable(null);
export const user = writable(null);
