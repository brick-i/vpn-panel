<script>
  import Sidebar from '../components/Sidebar.svelte';
  import Dashboard from '../components/Dashboard.svelte';
  import ClientList from '../components/ClientList.svelte';
  import ServerConfig from '../components/ServerConfig.svelte';
  import Stats from '../components/Stats.svelte';
  import { currentPage } from '../lib/stores.js';
</script>

<div class="flex h-screen">
  <Sidebar />
  <main class="flex-1 overflow-y-auto p-8">
    {#if $currentPage === 'dashboard'}
      <Dashboard />
    {:else if $currentPage === 'clients'}
      <ClientList />
    {:else if $currentPage === 'config'}
      <ServerConfig />
    {:else if $currentPage === 'stats'}
      <Stats />
    {/if}
  </main>
</div>
