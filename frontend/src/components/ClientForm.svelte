<script>
  import { createEventDispatcher } from 'svelte';
  import { api } from '../lib/api.js';

  export let client = null;

  const dispatch = createEventDispatcher();

  let name = client?.name || '';
  let allowed_ips = client?.allowed_ips || '0.0.0.0/0, ::/0';
  let dns = client?.dns || '1.1.1.1, 8.8.8.8';
  let is_active = client?.is_active ?? true;
  let loading = false;
  let error = '';

  async function save() {
    loading = true;
    error = '';
    try {
      if (client) {
        await api.updateClient(client.id, { name, allowed_ips, dns, is_active });
      } else {
        const result = await api.createClient({ name, allowed_ips, dns });
        // Show private key only once
        alert(`Client created!\n\nPrivate Key: ${result.private_key}\nIP: ${result.ip_address}\n\nSave this key - it won't be shown again!`);
      }
      dispatch('close');
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
</script>

<div class="card">
  <h3 class="text-lg font-semibold text-white mb-4">
    {client ? 'Edit Client' : 'New Client'}
  </h3>

  {#if error}
    <div class="bg-red-500/10 border border-red-500/50 rounded-lg p-3 mb-4">
      <p class="text-red-400 text-sm">{error}</p>
    </div>
  {/if}

  <form on:submit|preventDefault={save} class="space-y-4">
    <div>
      <label class="block text-dark-300 text-sm mb-1">Name</label>
      <input class="input w-full" bind:value={name} required placeholder="My Device" />
    </div>

    <div>
      <label class="block text-dark-300 text-sm mb-1">Allowed IPs</label>
      <input class="input w-full" bind:value={allowed_ips} placeholder="0.0.0.0/0, ::/0" />
      <p class="text-dark-400 text-xs mt-1">Traffic routed through VPN. Use 0.0.0.0/0 for full tunnel.</p>
    </div>

    <div>
      <label class="block text-dark-300 text-sm mb-1">DNS</label>
      <input class="input w-full" bind:value={dns} placeholder="1.1.1.1, 8.8.8.8" />
    </div>

    {#if client}
      <div class="flex items-center gap-2">
        <input type="checkbox" bind:checked={is_active} id="active" class="rounded" />
        <label for="active" class="text-dark-300 text-sm">Active</label>
      </div>
    {/if}

    <div class="flex gap-3 pt-2">
      <button type="submit" class="btn-primary" disabled={loading}>
        {loading ? 'Saving...' : 'Save'}
      </button>
      <button type="button" class="btn-secondary" on:click={() => dispatch('close')}>Cancel</button>
    </div>
  </form>
</div>
