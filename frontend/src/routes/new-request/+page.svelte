<script lang="ts">
  import { goto } from "$app/navigation";
  import { getBaseURL } from "$lib";

  let { data } = $props();
  if (data.user.role != "hospital") goto("/");
  let name = $state("");
  let age = $state("");
  let sequence = $state("");
  let labID = $state("");

  const handleSubmit = async (e: SubmitEvent) => {
    e.preventDefault();

    await fetch(`${getBaseURL()}/create-request`, {
      method: "POST",
      body: JSON.stringify({
        name,
        age,
        sequence,
        labID,
        hospitalID: data.user.id,
      }),
      credentials: "include",
    });
  };
</script>

<div
  class="min-h-screen bg-gray-100 flex items-center justify-center px-4 py-10"
>
  <div
    class="flex flex-col md:flex-row w-full max-w-5xl rounded-2xl overflow-hidden shadow-2xl bg-white"
  >
    <div
      class="bg-teal-600 text-white w-full md:w-1/2 flex items-center justify-center p-10"
    >
      <div class="text-center space-y-4">
        <h1 class="text-5xl font-sans">Welcome</h1>
        <p class="text-lg text-teal-100">
          Please fill in your details carefully
        </p>
      </div>
    </div>

    <div class="w-full md:w-1/2 p-8 md:p-12 bg-gray-50">
      <form onsubmit={handleSubmit} class="space-y-6">
        <h2 class="text-2xl text-center text-gray-800">
          Enter Request Details
        </h2>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1"
            >Name
            <input
              type="text"
              bind:value={name}
              class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              required
            />
          </label>
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1"
            >Age
            <input
              type="number"
              bind:value={age}
              class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              required
            />
          </label>
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1"
            >Sequence
            <input
              type="text"
              bind:value={sequence}
              class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              required
            />
          </label>
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1"
            >Select Lab
            <select
              bind:value={labID}
              class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              required
            >
              <option value="" disabled selected>Select a lab</option>
              {#each data.labs as l, i (i)}
                <option value={l}>{l}</option>
              {/each}
            </select>
          </label>
        </div>

        <button
          type="submit"
          class="w-full bg-teal-600 text-white py-2 px-4 rounded-md hover:bg-teal-700 transition duration-200"
        >
          Submit
        </button>
      </form>
    </div>
  </div>
</div>

