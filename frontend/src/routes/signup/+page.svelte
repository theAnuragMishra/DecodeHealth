<script lang="ts">
  import { getBaseURL } from "$lib";

  let name = $state("");
  let password = $state("");
  let role: "lab" | "hospital" = $state("lab");

  const handleSignup = async (e: SubmitEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${getBaseURL()}/new-org`, {
        method: "POST",
        body: JSON.stringify({ name, password, role }),
        credentials: "include",
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) console.log("error");
    } catch (e) {
      console.log(e);
    }
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
        <h1 class="text-5xl font-sans">Welcome Back</h1>
        <p class="text-lg text-teal-100">Please Signup</p>
      </div>
    </div>

    <div class="w-full md:w-1/2 p-8 md:p-12 bg-gray-50">
      <form onsubmit={handleSignup} class="space-y-6">
        <h2 class="text-2xl text-center text-gray-800">Signup</h2>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">
            Fullname
            <input
              type="text"
              bind:value={name}
              class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              required
            />
          </label>
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1">
            Password
            <input
              type="password"
              bind:value={password}
              class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              required
            />
          </label>
        </div>
        <div>
          <label><input type="radio" bind:group={role} value="lab" />Lab</label>
          <label
            ><input
              type="radio"
              bind:group={role}
              value="hospital"
            />Hospital</label
          >
        </div>

        <button
          type="submit"
          class="w-full bg-teal-600 text-white py-2 px-4 rounded-md hover:bg-teal-700 transition duration-200"
        >
          Signup
        </button>
      </form>
    </div>
  </div>
</div>

