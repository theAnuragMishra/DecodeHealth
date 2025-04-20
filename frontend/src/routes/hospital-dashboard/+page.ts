import { getBaseURL } from "$lib";
import { error } from "@sveltejs/kit";

export async function load({ parent }) {
  const { user } = await parent();
  const response = await fetch(`${getBaseURL()}/requests-hospital/${user.ID}`, {
    credentials: "include",
  });
  if (!response.ok) {
    error(404, { message: "requests not found" });
  }
  return { requests: await response.json() };
}
