<script lang="ts">
  let activeTab = $state("new");
  let { data } = $props();
</script>

<div class="min-h-screen bg-gray-100 flex">
  <div class="w-64 bg-teal-600 text-white flex flex-col p-6 space-y-4">
    <h2 class="text-2xl font-semibold mb-6">Lab Dashboard</h2>
    <button class="text-left" onclick={() => (activeTab = "new")}
      >New Requests</button
    >
    <button class="text-left" onclick={() => (activeTab = "accepted")}
      >Accepted Requests</button
    >
    <button class="text-left" onclick={() => (activeTab = "rejected")}
      >Rejected Requests</button
    >
    <button class="text-left" onclick={() => (activeTab = "live")}
      >Live Requests</button
    >
  </div>

  <div class="flex-1 p-8 bg-gray-50">
    <h1 class="text-3xl mb-6 text-gray-800">
      {#if activeTab === "new"}New Requests{/if}
      {#if activeTab === "accepted"}Accepted Requests{/if}
      {#if activeTab === "rejected"}Rejected Requests{/if}
      {#if activeTab === "live"}Live Requests{/if}
    </h1>

    <div class="space-y-4">
      {#each data.requests.filter((r: any) => (activeTab === "new" && r.status === "pending") || (activeTab === "accepted" && r.status === "accepted") || (activeTab === "rejected" && r.status === "rejected") || (activeTab === "live" && r.status === "accepted")) as req, index (index)}
        <div class="bg-white shadow-md rounded-lg p-4 border border-gray-200">
          <a href={`/request/${req.id}`}><strong>Name:</strong> {req.name}</a>
          <span><strong>Age:</strong> {req.age}</span>
          <span><strong>Sequence:</strong> {req.sequence}</span>
          <span><strong>Lab:</strong> {req.lab}</span>
        </div>
      {:else}
        <p class="text-gray-500">No requests in this tab.</p>
      {/each}
    </div>
  </div>
</div>

