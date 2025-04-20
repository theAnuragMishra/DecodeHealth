<script>
  import { getBaseURL } from "$lib";
  let { children } = $props();
  import "../app.css";
  const handleLogout = async () => {
    await fetch(`${getBaseURL()}/logout`, {
      method: "POST",
      credentials: "include",
    });
  };
</script>

<main class="flex min-h-screen flex-col items-center">
  <nav class="flex mb-10 justify-right w-full">
    <ul>
      <li><button onclick={handleLogout}>Logout</button></li>
    </ul>
  </nav>
  {@render children()}
</main>
