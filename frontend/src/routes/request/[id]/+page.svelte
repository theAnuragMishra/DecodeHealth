<script lang="ts">
  import Hosr from "$lib/components/hosr.svelte";
  import Labr from "$lib/components/labr.svelte";
  const { data } = $props();
</script>

{#if data.user.Role == "hospital"}
  <Hosr request={data.request} />
{:else}
  <Labr request={data.request} />
{/if}
