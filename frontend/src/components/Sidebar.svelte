<script>
  import { currentPage } from '../lib/stores.js';

  const pages = [
    { id: 'dashboard', label: 'Dashboard', icon: '⚡' },
    { id: 'clients', label: 'Clients', icon: '👤' },
    { id: 'config', label: 'Server Config', icon: '⚙️' },
    { id: 'stats', label: 'Statistics', icon: '📊' },
  ];

  function navigate(page) {
    $currentPage = page;
  }

  function logout() {
    localStorage.removeItem('token');
    window.location.reload();
  }
</script>

<aside class="w-64 bg-dark-800 border-r border-dark-600 h-screen flex flex-col">
  <div class="p-6 border-b border-dark-600">
    <h1 class="text-xl font-bold text-white">⚡ AmneziaWG</h1>
    <p class="text-dark-300 text-sm mt-1">VPN Panel</p>
  </div>

  <nav class="flex-1 p-4 space-y-1">
    {#each pages as page}
      <button
        class="w-full text-left px-4 py-3 rounded-lg flex items-center gap-3 transition-colors
               {$currentPage === page.id ? 'bg-accent text-white' : 'text-dark-300 hover:bg-dark-700 hover:text-white'}"
        onclick={() => navigate(page.id)}
      >
        <span>{page.icon}</span>
        <span>{page.label}</span>
      </button>
    {/each}
  </nav>

  <div class="p-4 border-t border-dark-600">
    <button class="w-full text-left px-4 py-3 rounded-lg text-dark-300 hover:bg-dark-700 hover:text-white transition-colors" onclick={logout}>
      🚪 Logout
    </button>
  </div>
</aside>
