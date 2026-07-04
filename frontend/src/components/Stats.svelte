<script>
  import { onMount, onDestroy } from 'svelte';
  import { api } from '../lib/api.js';

  let clientStats = $state([]);
  let sysInfo = $state(null);
  let loading = $state(true);
  let interval;

  onMount(async () => {
    await load();
    interval = setInterval(load, 5000);
  });

  onDestroy(() => clearInterval(interval));

  async function load() {
    try {
      const [cs, si] = await Promise.all([
        api.getClientStats(),
        api.getSystemInfo(),
      ]);
      clientStats = cs;
      sysInfo = si;
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  }

  function formatBytes(b) {
    if (!b) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let i = 0;
    while (b >= 1024 && i < units.length - 1) { b /= 1024; i++; }
    return `${b.toFixed(1)} ${units[i]}`;
  }

  let maxTraffic = $derived(
    clientStats.length > 0
      ? Math.max(...clientStats.map(c => c.rx_bytes + c.tx_bytes))
      : 1
  );
</script>

<div class="space-y-6">
  <h2 class="text-2xl font-bold text-white">Statistics</h2>

  {#if loading}
    <div class="card text-center text-dark-300">Loading...</div>
  {:else}
    {#if sysInfo}
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="card text-center">
          <p class="text-dark-300 text-sm">Network RX</p>
          <p class="text-xl font-bold text-white">{formatBytes(sysInfo.network_rx)}</p>
        </div>
        <div class="card text-center">
          <p class="text-dark-300 text-sm">Network TX</p>
          <p class="text-xl font-bold text-white">{formatBytes(sysInfo.network_tx)}</p>
        </div>
        <div class="card text-center">
          <p class="text-dark-300 text-sm">Uptime</p>
          <p class="text-xl font-bold text-white">{sysInfo.uptime_fmt}</p>
        </div>
      </div>
    {/if}

    <div class="card">
      <h3 class="text-lg font-semibold text-white mb-4">Client Traffic</h3>
      {#if clientStats.length === 0}
        <p class="text-dark-300">No active clients with traffic data.</p>
      {:else}
        <div class="space-y-3">
          {#each clientStats as stat}
            <div class="space-y-1">
              <div class="flex justify-between text-sm">
                <span class="text-white font-medium">{stat.name}</span>
                <span class="text-dark-300">
                  ↓ {stat.rx_fmt} / ↑ {stat.tx_fmt}
                  {#if stat.is_active}
                    <span class="text-green-400 ml-2">●</span>
                  {/if}
                </span>
              </div>
              <div class="w-full bg-dark-700 rounded-full h-2">
                <div
                  class="bg-accent h-2 rounded-full transition-all"
                  style="width: {((stat.rx_bytes + stat.tx_bytes) / maxTraffic * 100)}%"
                ></div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    {#if sysInfo}
      <div class="card">
        <h3 class="text-lg font-semibold text-white mb-4">System Resources</h3>
        <div class="space-y-4">
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-dark-300">CPU</span>
              <span class="text-white">{sysInfo.cpu_percent.toFixed(1)}%</span>
            </div>
            <div class="w-full bg-dark-700 rounded-full h-3">
              <div class="bg-accent h-3 rounded-full transition-all" style="width: {sysInfo.cpu_percent}%"></div>
            </div>
          </div>
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-dark-300">RAM</span>
              <span class="text-white">{sysInfo.ram_percent.toFixed(1)}%</span>
            </div>
            <div class="w-full bg-dark-700 rounded-full h-3">
              <div class="bg-accent h-3 rounded-full transition-all" style="width: {sysInfo.ram_percent}%"></div>
            </div>
          </div>
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-dark-300">Disk</span>
              <span class="text-white">{sysInfo.disk_percent.toFixed(1)}%</span>
            </div>
            <div class="w-full bg-dark-700 rounded-full h-3">
              <div class="bg-accent h-3 rounded-full transition-all" style="width: {sysInfo.disk_percent}%"></div>
            </div>
          </div>
        </div>
      </div>
    {/if}
  {/if}
</div>
