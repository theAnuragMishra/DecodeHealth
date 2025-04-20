<script>
  const { request } = $props();
</script>

<p>Name: {request.Name}</p>
<p>Age: {request.Age}</p>
<p>Status: {request.Status}</p>
<h2>Report</h2>
<p>{request.report}</p>
