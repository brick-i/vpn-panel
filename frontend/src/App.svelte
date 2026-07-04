<script>
  import { onMount } from 'svelte';
  import Login from './pages/Login.svelte';
  import Main from './pages/Main.svelte';

  let authenticated = false;
  let checked = false;

  onMount(() => {
    const token = localStorage.getItem('token');
    authenticated = !!token;
    checked = true;
  });
</script>

{#if !checked}
  <div class="min-h-screen bg-dark-900 flex items-center justify-center">
    <p class="text-dark-300">Loading...</p>
  </div>
{:else if authenticated}
  <Main />
{:else}
  <Login />
{/if}

<style>
  @import './app.css';
</style>
