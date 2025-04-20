<script lang="ts">
  const { data } = $props();
</script>

<h1>DecodeHealth</h1>
{#if data.user}
  <div>
    Hi {data.user.username}
    Welcome to DecodeHealth
  </div>
{:else}
  <a href="/login">Login</a>
{/if}
