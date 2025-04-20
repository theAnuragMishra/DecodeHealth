import { getBaseURL } from "$lib";
import { error } from "@sveltejs/kit";

export async function load({ params }) {
  const id = params.id;
  const response = await fetch(`${getBaseURL()}/request/${id}`, {
    credentials: "include",
  });
  if (!response.ok) error(404, { message: "request not found" });
  return { request: await response.json() };
}
