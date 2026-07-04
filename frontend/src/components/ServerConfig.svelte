<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/api.js';

  let config = {};
  let loading = true;
  let saving = false;
  let installing = false;
  let installProgress = null;
  let installLog = '';
  let error = '';
  let success = '';
  let status = null;

  let form = {
    listen_port: 51820,
    dns: '1.1.1.1, 8.8.8.8',
    jc: 0, jmin: 0, jmax: 0,
    s1: 0, s2: 0,
    h1: 0, h2: 0, h3: 0, h4: 0,
  };

  let installInterval;

  onMount(async () => {
    try {
      [config, status] = await Promise.all([
        api.getServerConfig(),
        api.getServerStatus(),
      ]);
      form = { ...form, ...config };
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  async function saveConfig() {
    saving = true;
    error = '';
    success = '';
    try {
      await api.updateServerConfig(form);
      success = 'Configuration saved!';
    } catch (e) {
      error = e.message;
    } finally {
      saving = false;
    }
  }

  async function startInstall() {
    installing = true;
    error = '';
    try {
      await api.installServer();
      installInterval = setInterval(checkProgress, 1000);
    } catch (e) {
      error = e.message;
      installing = false;
    }
  }

  async function checkProgress() {
    try {
      installProgress = await api.getInstallProgress();
      installLog = installProgress.message || '';
      if (!installProgress.running && installProgress.current >= installProgress.total) {
        clearInterval(installInterval);
        installing = false;
        status = await api.getServerStatus();
        if (installProgress.error) {
          error = installProgress.error;
        } else {
          success = 'AmneziaWG installed successfully!';
        }
      }
    } catch (e) {
      clearInterval(installInterval);
      installing = false;
    }
  }

  function formatBytes(b) {
    if (!b) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let i = 0;
    while (b >= 1024 && i < units.length - 1) { b /= 1024; i++; }
    return `${b.toFixed(1)} ${units[i]}`;
  }
</script>

<div class="space-y-6">
  <h2 class="text-2xl font-bold text-white">Server Configuration</h2>

  {#if error}
    <div class="card border-red-500/50 bg-red-500/10">
      <p class="text-red-400">{error}</p>
    </div>
  {/if}

  {#if success}
    <div class="card border-green-500/50 bg-green-500/10">
      <p class="text-green-400">{success}</p>
    </div>
  {/if}

  {#if !status?.installed}
    <div class="card">
      <h3 class="text-lg font-semibold text-white mb-4">Install AmneziaWG</h3>
      <p class="text-dark-300 mb-4">AmneziaWG is not installed on this server. Click below to install.</p>
      {#if installing}
        <div class="space-y-3">
          <div class="w-full bg-dark-700 rounded-full h-3">
            <div
              class="bg-accent h-3 rounded-full transition-all"
              style="width: {installProgress ? (installProgress.current / installProgress.total * 100) : 0}%"
            ></div>
          </div>
          <p class="text-dark-300 text-sm">{installLog}</p>
        </div>
      {:else}
        <button class="btn-primary" on:click={startInstall}>Install AmneziaWG</button>
      {/if}
    </div>
  {/if}

  {#if status?.installed}
    <div class="card">
      <h3 class="text-lg font-semibold text-white mb-4">Network Settings</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-dark-300 text-sm mb-1">Listen Port</label>
          <input class="input w-full" type="number" bind:value={form.listen_port} min="1" max="65535" />
        </div>
        <div>
          <label class="block text-dark-300 text-sm mb-1">DNS Servers</label>
          <input class="input w-full" bind:value={form.dns} placeholder="1.1.1.1, 8.8.8.8" />
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="text-lg font-semibold text-white mb-4">Obfuscation (AmneziaWG)</h3>
      <p class="text-dark-400 text-sm mb-4">Set non-zero values to enable obfuscation. Higher values = stronger obfuscation but more overhead.</p>
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-dark-300 text-sm mb-1">Jc</label>
          <input class="input w-full" type="number" bind:value={form.jc} min="0" max="128" />
        </div>
        <div>
          <label class="block text-dark-300 text-sm mb-1">Jmin</label>
          <input class="input w-full" type="number" bind:value={form.jmin} min="0" max="128" />
        </div>
        <div>
          <label class="block text-dark-300 text-sm mb-1">Jmax</label>
          <input class="input w-full" type="number" bind:value={form.jmax} min="0" max="128" />
        </div>
        <div>
          <label class="block text-dark-300 text-sm mb-1">S1</label>
          <input class="input w-full" type="number" bind:value={form.s1} min="0" max="128" />
        </div>
        <div>
          <label class="block text-dark-300 text-sm mb-1">S2</label>
          <input class="input w-full" type="number" bind:value={form.s2} min="0" max="128" />
        </div>
        <div>
          <label class="block text-dark-300 text-sm mb-1">H1</label>
          <input class="input w-full" type="number" bind:value={form.h1} min="0" max="255" />
        </div>
        <div>
          <label class="block text-dark-300 text-sm mb-1">H2</label>
          <input class="input w-full" type="number" bind:value={form.h2} min="0" max="255" />
        </div>
        <div>
          <label class="block text-dark-300 text-sm mb-1">H3</label>
          <input class="input w-full" type="number" bind:value={form.h3} min="0" max="255" />
        </div>
        <div>
          <label class="block text-dark-300 text-sm mb-1">H4</label>
          <input class="input w-full" type="number" bind:value={form.h4} min="0" max="255" />
        </div>
      </div>
    </div>

    <div class="flex gap-3">
      <button class="btn-primary" on:click={saveConfig} disabled={saving}>
        {saving ? 'Saving...' : 'Save Configuration'}
      </button>
    </div>
  {/if}
</div>
