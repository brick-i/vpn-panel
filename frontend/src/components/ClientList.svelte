<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/api.js';
  import ClientForm from './ClientForm.svelte';

  let clients = $state([]);
  let loading = $state(true);
  let showForm = $state(false);
  let editingClient = $state(null);

  onMount(loadClients);

  async function loadClients() {
    loading = true;
    try {
      clients = await api.getClients();
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  }

  async function deleteClient(id) {
    if (!confirm('Delete this client?')) return;
    try {
      await api.deleteClient(id);
      await loadClients();
    } catch (e) {
      alert(e.message);
    }
  }

  function editClient(client) {
    editingClient = client;
    showForm = true;
  }

  function closeForm() {
    showForm = false;
    editingClient = null;
    loadClients();
  }

  function formatBytes(b) {
    if (!b) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let i = 0;
    while (b >= 1024 && i < units.length - 1) { b /= 1024; i++; }
    return `${b.toFixed(1)} ${units[i]}`;
  }

  function timeSince(ts) {
    if (!ts) return 'Never';
    const d = Math.floor(ts / 86400);
    const h = Math.floor((ts % 86400) / 3600);
    const m = Math.floor((ts % 3600) / 60);
    if (d > 0) return `${d}d ${h}h ago`;
    if (h > 0) return `${h}h ${m}m ago`;
    return `${m}m ago`;
  }

  async function downloadConfig(id, name) {
    const res = await fetch(`/api/clients/${id}/config`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${name}.conf`;
    a.click();
    URL.revokeObjectURL(url);
  }
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <h2 class="text-2xl font-bold text-white">Clients</h2>
    <button class="btn-primary" onclick={() => { editingClient = null; showForm = true; }}>
      + Add Client
    </button>
  </div>

  {#if showForm}
    <ClientForm client={editingClient} onClose={closeForm} />
  {/if}

  {#if loading}
    <div class="card text-center text-dark-300">Loading...</div>
  {:else if clients.length === 0}
    <div class="card text-center text-dark-300">No clients yet. Add your first client.</div>
  {:else}
    <div class="card overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-dark-600 text-dark-300">
            <th class="text-left py-3 px-4">Name</th>
            <th class="text-left py-3 px-4">IP Address</th>
            <th class="text-left py-3 px-4">Status</th>
            <th class="text-left py-3 px-4">Last Handshake</th>
            <th class="text-right py-3 px-4">RX / TX</th>
            <th class="text-right py-3 px-4">Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each clients as client}
            <tr class="border-b border-dark-700 hover:bg-dark-700/50">
              <td class="py-3 px-4 text-white font-medium">{client.name}</td>
              <td class="py-3 px-4 text-dark-200 font-mono">{client.ip_address}</td>
              <td class="py-3 px-4">
                {#if client.last_handshake !== null && client.last_handshake < 180}
                  <span class="text-green-400">Active</span>
                {:else}
                  <span class="text-dark-400">Inactive</span>
                {/if}
              </td>
              <td class="py-3 px-4 text-dark-300">{timeSince(client.last_handshake)}</td>
              <td class="py-3 px-4 text-right text-dark-200">
                {formatBytes(client.rx_bytes)} / {formatBytes(client.tx_bytes)}
              </td>
              <td class="py-3 px-4 text-right space-x-2">
                <button class="text-accent hover:text-accent-hover text-sm" onclick={() => editClient(client)}>Edit</button>
                <button class="text-accent hover:text-accent-hover text-sm" onclick={() => downloadConfig(client.id, client.name)}>Download</button>
                <button class="text-red-400 hover:text-red-300 text-sm" onclick={() => deleteClient(client.id)}>Delete</button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>
