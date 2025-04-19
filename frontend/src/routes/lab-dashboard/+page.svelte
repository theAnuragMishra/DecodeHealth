<script lang="ts">
    interface Request {
      id: number;
      name: string;
      age: number;
      sequence: string;
      lab: string;
      status: 'pending' | 'accepted' | 'rejected';
    }
  
    let activeTab = 'new';
  
    let requests: Request[] = [
      { id: 1, name: 'John Doe', age: 45, sequence: 'SEQ123', lab: 'Lab A', status: 'pending' },
      { id: 2, name: 'Jane Smith', age: 32, sequence: 'SEQ124', lab: 'Lab B', status: 'pending' }
    ];
  
    const updateStatus = (id: number, status: 'accepted' | 'rejected') => {
      requests = requests.map(req => req.id === id ? { ...req, status } : req);
    };
  </script>
  
  <div class="min-h-screen bg-gray-100 flex">
    <div class="w-64 bg-teal-600 text-white flex flex-col p-6 space-y-4">
      <h2 class="text-2xl font-semibold mb-6"> Lab Dashboard</h2>
      <button class="text-left" on:click={() => activeTab = 'new'}>New Requests</button>
      <button class="text-left" on:click={() => activeTab = 'accepted'}>Accepted Requests</button>
      <button class="text-left" on:click={() => activeTab = 'rejected'}>Rejected Requests</button>
      <button class="text-left" on:click={() => activeTab = 'live'}>Live Requests</button>
    </div>
  
    <div class="flex-1 p-8 bg-gray-50">
      <h1 class="text-3xl  mb-6 text-gray-800">
        {#if activeTab === 'new'}New Requests{/if}
        {#if activeTab === 'accepted'}Accepted Requests{/if}
        {#if activeTab === 'rejected'}Rejected Requests{/if}
        {#if activeTab === 'live'}Live Requests{/if}
      </h1>
  
      <div class="space-y-4">
        {#each requests.filter(r =>
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
            {#if req.status === 'pending'}
              <div class="mt-4 space-x-2">
                <button class="bg-teal-600 text-white px-4 py-1 rounded hover:bg-teal-700" on:click={() => updateStatus(req.id, 'accepted')}>Accept</button>
                <button class="bg-red-500 text-white px-4 py-1 rounded hover:bg-red-600" on:click={() => updateStatus(req.id, 'rejected')}>Reject</button>
              </div>
            {/if}
          </div>
        {:else}
          <p class="text-gray-500">No requests in this tab.</p>
        {/each}
      </div>
    </div>
  </div>
  