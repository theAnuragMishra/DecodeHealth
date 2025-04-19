import { getBaseURL } from "$lib";
import { error } from "@sveltejs/kit";

export async function load({ parent }) {
  const { user } = await parent();
  const response = await fetch(`${getBaseURL()}/requests-lab/${user.id}`);
  if (!response.ok) {
    error(404, { message: "requests not found" });
  }
  return { requests: await response.json() };
}
