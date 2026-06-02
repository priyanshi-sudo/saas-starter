"use client";

// In production this token comes from the Supabase client SDK after sign-in.
// For local development we stash a token in localStorage so the typed API
// client can attach it as a Bearer header.
const TOKEN_KEY = "sb_access_token";
const ORG_KEY = "active_org_id";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getActiveOrg(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ORG_KEY);
}

export function setActiveOrg(orgId: string): void {
  localStorage.setItem(ORG_KEY, orgId);
}
