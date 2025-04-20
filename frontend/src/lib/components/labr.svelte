<script>
  import { getBaseURL } from "$lib";
  let report = $state("");
  const { request } = $props();
  const handleSubmit = async () => {
    await fetch(`${getBaseURL()}/update-report/${request.ID}`, {
      body: JSON.stringify({ report }),
      credentials: "include",
    });
  };
</script>

<p>Name: {request.Name}</p>
<p>Age: {request.Age}</p>
<p>Status: {request.Status}</p>
<h2>Report</h2>
{#if request.Report}
  <p>{request.report}</p>
{:else}
  <textarea bind:value={report}></textarea>
  <button onclick={handleSubmit}>Submit Report</button>
{/if}
