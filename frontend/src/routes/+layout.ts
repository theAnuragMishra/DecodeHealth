import { getBaseURL } from "$lib";

export async function load() {
  const response = await fetch(`${getBaseURL()}/me`);
  if (!response.ok) {
    return { user: null };
  }
  return { user: await response.json() };
}
