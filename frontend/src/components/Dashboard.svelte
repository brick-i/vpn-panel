<script>
  import { onMount, onDestroy } from 'svelte';
  import { api } from '../lib/api.js';

  let status = null;
  let sysInfo = null;
  let loading = true;
  let error = '';
  let interval;

  onMount(async () => {
    await load();
    interval = setInterval(load, 5000);
  });

  onDestroy(() => clearInterval(interval));

  async function load() {
    try {
      const data = await api.getStatsOverview();
      status = data.server;
      sysInfo = data.system;
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function toggleServer() {
    if (!status) return;
    try {
      if (status.running) {
        await api.stopServer();
      } else {
        await api.startServer();
      }
      await load();
    } catch (e) {
      error = e.message;
    }
  }

  function formatBytes(b) {
    if (!b) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let i = 0;
    while (b >= 1024 && i < units.length - 1) { b /= 1024; i++; }
    return `${b.toFixed(1)} ${units[i]}`;
  }

  function formatUptime(s) {
    const d = Math.floor(s / 86400);
    const h = Math.floor((s % 86400) / 3600);
    const m = Math.floor((s % 3600) / 60);
    if (d > 0) return `${d}d ${h}h ${m}m`;
    if (h > 0) return `${h}h ${m}m`;
    return `${m}m`;
  }
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <h2 class="text-2xl font-bold text-white">Dashboard</h2>
    {#if status && status.installed}
      <button
        class={status.running ? 'btn-danger' : 'btn-primary'}
        on:click={toggleServer}
      >
        {status.running ? '⏹ Stop VPN' : '▶ Start VPN'}
      </button>
    {/if}
  </div>

  {#if !status?.installed}
    <div class="card border-yellow-500/50 bg-yellow-500/10">
      <div class="flex items-center gap-3">
        <span class="text-yellow-500 text-2xl">⚠️</span>
        <div>
          <h3 class="text-white font-semibold">AmneziaWG not installed</h3>
          <p class="text-dark-300 text-sm">Go to Server Config to install AmneziaWG</p>
        </div>
      </div>
    </div>
  {/if}

  {#if error}
    <div class="card border-red-500/50 bg-red-500/10">
      <p class="text-red-400">{error}</p>
    </div>
  {/if}

  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <div class="card">
      <p class="text-dark-300 text-sm">Status</p>
      <p class="text-2xl font-bold {status?.running ? 'text-green-400' : 'text-red-400'}">
        {status?.running ? 'Running' : 'Stopped'}
      </p>
    </div>
    <div class="card">
      <p class="text-dark-300 text-sm">Connected Clients</p>
      <p class="text-2xl font-bold text-white">{status?.connected_clients || 0}</p>
    </div>
    <div class="card">
      <p class="text-dark-300 text-sm">CPU Usage</p>
      <p class="text-2xl font-bold text-white">{sysInfo?.cpu_percent?.toFixed(1) || 0}%</p>
    </div>
    <div class="card">
      <p class="text-dark-300 text-sm">Uptime</p>
      <p class="text-2xl font-bold text-white">{sysInfo ? formatUptime(sysInfo.uptime) : '--'}</p>
    </div>
  </div>

  {#if sysInfo}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="card">
        <h3 class="text-white font-semibold mb-4">Memory</h3>
        <div class="w-full bg-dark-700 rounded-full h-3">
          <div class="bg-accent h-3 rounded-full transition-all" style="width: {sysInfo.ram_percent}%"></div>
        </div>
        <p class="text-dark-300 text-sm mt-2">
          {formatBytes(sysInfo.ram_used)} / {formatBytes(sysInfo.ram_total)}
          ({sysInfo.ram_percent.toFixed(1)}%)
        </p>
      </div>
      <div class="card">
        <h3 class="text-white font-semibold mb-4">Disk</h3>
        <div class="w-full bg-dark-700 rounded-full h-3">
          <div class="bg-accent h-3 rounded-full transition-all" style="width: {sysInfo.disk_percent}%"></div>
        </div>
        <p class="text-dark-300 text-sm mt-2">
          {formatBytes(sysInfo.disk_used)} / {formatBytes(sysInfo.disk_total)}
          ({sysInfo.disk_percent.toFixed(1)}%)
        </p>
      </div>
    </div>

    <div class="card">
      <h3 class="text-white font-semibold mb-4">System Info</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div>
          <p class="text-dark-300">Hostname</p>
          <p class="text-white">{sysInfo.hostname}</p>
        </div>
        <div>
          <p class="text-dark-300">OS</p>
          <p class="text-white">{sysInfo.os}</p>
        </div>
        <div>
          <p class="text-dark-300">Network RX</p>
          <p class="text-white">{formatBytes(sysInfo.network_rx)}</p>
        </div>
        <div>
          <p class="text-dark-300">Network TX</p>
          <p class="text-white">{formatBytes(sysInfo.network_tx)}</p>
        </div>
      </div>
    </div>
  {/if}
</div>
