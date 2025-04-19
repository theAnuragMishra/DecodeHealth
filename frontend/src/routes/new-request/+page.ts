import { getBaseURL } from "$lib";
import { redirect } from "@sveltejs/kit";

export async function load({ parent }) {
  const { user } = await parent();
  if (user.role != "hospital") redirect(303, "/");
  const response = await fetch(`${getBaseURL()}/lab-list`);
  if (!response.ok) return { labs: null };
  return { labs: await response.json() };
}
