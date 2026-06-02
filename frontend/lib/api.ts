import { getActiveOrg, getToken } from "@/lib/auth";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Org = {
  id: string;
  name: string;
  slug: string;
  plan: string;
  role: string | null;
};

export type Member = { user_id: string; email: string; role: string };

function headers(): HeadersInit {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  const token = getToken();
  const org = getActiveOrg();
  if (token) h["Authorization"] = `Bearer ${token}`;
  if (org) h["x-org-id"] = org;
  return h;
}

export async function listOrgs(): Promise<Org[]> {
  const res = await fetch(`${API_URL}/api/orgs`, { headers: headers() });
  if (!res.ok) return [];
  return res.json();
}

export async function createOrg(name: string, slug: string): Promise<Org> {
  const res = await fetch(`${API_URL}/api/orgs`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({ name, slug }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function listMembers(orgId: string): Promise<Member[]> {
  const res = await fetch(`${API_URL}/api/members/${orgId}`, {
    headers: headers(),
  });
  if (!res.ok) return [];
  return res.json();
}

export async function openBillingPortal(orgId: string): Promise<string | null> {
  const res = await fetch(`${API_URL}/api/billing/portal?org_id=${orgId}`, {
    method: "POST",
    headers: headers(),
  });
  if (!res.ok) return null;
  return (await res.json()).url ?? null;
}
