import { getBaseURL } from "$lib";
import { redirect } from "@sveltejs/kit";
export const ssr = false;

export async function load({ route }) {
  const response = await fetch(`${getBaseURL()}/me`, {
    credentials: "include",
  });
  if (!response.ok && route.id != "/login" && route.id != "/signup") {
    redirect(303, "/login");
  }
  return { user: await response.json() };
}
