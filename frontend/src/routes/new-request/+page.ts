import { getBaseURL } from "$lib";
import { redirect } from "@sveltejs/kit";

export async function load({ parent }) {
  const { user } = await parent();
  console.log(user);
  if (user.Role != "hospital") redirect(303, "/");
  const response = await fetch(`${getBaseURL()}/lab-list`, {
    credentials: "include",
  });
  if (!response.ok) return { labs: null };
  return { labs: await response.json() };
}
