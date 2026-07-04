<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/api.js';

  let isSetup = false;
  let setupChecked = false;
  let username = '';
  let password = '';
  let loading = false;
  let error = '';

  onMount(async () => {
    try {
      const res = await api.getSetupStatus();
      isSetup = res.configured;
    } catch (e) {
      // Server might not be running
    } finally {
      setupChecked = true;
    }
  });

  async function handleSubmit() {
    loading = true;
    error = '';
    try {
      if (isSetup) {
        const res = await api.login(username, password);
        localStorage.setItem('token', res.access_token);
      } else {
        await api.setup(username, password);
        const res = await api.login(username, password);
        localStorage.setItem('token', res.access_token);
      }
      window.location.hash = '#/';
      window.location.reload();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center bg-dark-900">
  <div class="card w-full max-w-md">
    <div class="text-center mb-8">
      <h1 class="text-3xl font-bold text-white">⚡ AmneziaWG Panel</h1>
      <p class="text-dark-300 mt-2">VPN Server Management</p>
    </div>

    {#if !setupChecked}
      <p class="text-center text-dark-300">Loading...</p>
    {:else}
      {#if error}
        <div class="bg-red-500/10 border border-red-500/50 rounded-lg p-3 mb-4">
          <p class="text-red-400 text-sm">{error}</p>
        </div>
      {/if}

      {#if !isSetup}
        <div class="bg-blue-500/10 border border-blue-500/50 rounded-lg p-3 mb-4">
          <p class="text-blue-400 text-sm">First run: create an admin account.</p>
        </div>
      {/if}

      <form on:submit|preventDefault={handleSubmit} class="space-y-4">
        <div>
          <label class="block text-dark-300 text-sm mb-1">Username</label>
          <input class="input w-full" bind:value={username} required placeholder="admin" autofocus />
        </div>
        <div>
          <label class="block text-dark-300 text-sm mb-1">Password</label>
          <input class="input w-full" type="password" bind:value={password} required placeholder="••••••••" />
        </div>
        <button type="submit" class="btn-primary w-full" disabled={loading}>
          {loading ? 'Please wait...' : (isSetup ? 'Sign In' : 'Create Account')}
        </button>
      </form>
    {/if}
  </div>
</div>
