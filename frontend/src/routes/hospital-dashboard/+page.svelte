<script lang="ts">
  interface Request {
    id: number;
    name: string;
    age: number;
    sequence: string;
    lab: string;
    status: 'pending' | 'accepted' | 'rejected';
  }

  let activeTab: 'new' | 'accepted' | 'rejected' | 'live' | 'all' = 'new';

  let requests: Request[] = [
    { id: 1, name: 'John Doe', age: 45, sequence: 'SEQ123', lab: 'Lab A', status: 'pending' },
    { id: 2, name: 'Jane Smith', age: 32, sequence: 'SEQ124', lab: 'Lab B', status: 'accepted' },
    { id: 3, name: 'Alex Lee', age: 29, sequence: 'SEQ125', lab: 'Lab C', status: 'rejected' },
    { id: 4, name: 'Emily Davis', age: 38, sequence: 'SEQ126', lab: 'Lab D', status: 'accepted' },
    { id: 5, name: 'Michael Brown', age: 50, sequence: 'SEQ127', lab: 'Lab E', status: 'pending' }
  ];
</script>

<div class="min-h-screen bg-gray-100 flex">
  <!-- Sidebar -->
  <div class="w-64 bg-teal-600 text-white flex flex-col p-6 space-y-4">
    <h2 class="text-2xl font-semibold mb-6">Hospital Dashboard</h2>
    <button class="text-left hover:underline" on:click={() => activeTab = 'new'}>New Requests</button>
    <button class="text-left hover:underline" on:click={() => activeTab = 'accepted'}>Accepted Requests</button>
    <button class="text-left hover:underline" on:click={() => activeTab = 'rejected'}>Rejected Requests</button>
    <button class="text-left hover:underline" on:click={() => activeTab = 'live'}>Live Requests</button>
    <button class="text-left hover:underline" on:click={() => activeTab = 'all'}>All Requests</button>
  </div>

  <!-- Main Content -->
  <div class="flex-1 p-8 bg-gray-50">
    <h1 class="text-3xl mb-6 text-gray-800 font-semibold">
      {#if activeTab === 'new'}New Requests{/if}
      {#if activeTab === 'accepted'}Accepted Requests{/if}
      {#if activeTab === 'rejected'}Rejected Requests{/if}
      {#if activeTab === 'live'}Live Requests{/if}
      {#if activeTab === 'all'}All Requests{/if}
    </h1>

    <div class="space-y-4">
      {#each requests.filter(r =>
        activeTab === 'all' ||
        (activeTab === 'new' && r.status === 'pending') ||
        (activeTab === 'accepted' && r.status === 'accepted') ||
        (activeTab === 'rejected' && r.status === 'rejected') ||
        (activeTab === 'live' && r.status === 'accepted')
      ) as req}
        <div class="bg-white shadow-md rounded-lg p-4 border border-gray-200">
          <p><strong>Name:</strong> {req.name}</p>
          <p><strong>Age:</strong> {req.age}</p>
          <p><strong>Sequence:</strong> {req.sequence}</p>
          <p><strong>Lab:</strong> {req.lab}</p>
          <div class="mt-4">
            <span
              class={`px-3 py-1 rounded-full text-sm font-semibold 
                ${req.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : ''} 
                ${req.status === 'accepted' ? 'bg-green-100 text-green-800' : ''} 
                ${req.status === 'rejected' ? 'bg-red-100 text-red-800' : ''}`}>
              {req.status === 'pending' ? 'Pending' : req.status === 'accepted' ? 'Approved' : 'Rejected'}
            </span>
          </div>
        </div>
      {:else}
        <p class="text-gray-500">No requests in this tab.</p>
      {/each}
    </div>
  </div>
</div>
