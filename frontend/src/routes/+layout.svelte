<script>
  let { children } = $props();
  import "../app.css";
</script>

<main class="flex min-h-screen flex-col items-center justify-center">
  {@render children()}
</main>
