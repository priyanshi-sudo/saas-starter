"use client";

import { useEffect, useState } from "react";
import { createOrg, listOrgs, Org } from "@/lib/api";
import { setActiveOrg } from "@/lib/auth";

export default function AppDashboard() {
  const [orgs, setOrgs] = useState<Org[]>([]);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setOrgs(await listOrgs());
  }

  useEffect(() => {
    refresh();
  }, []);

  async function create() {
    if (!name.trim() || !slug.trim()) return;
    setError(null);
    try {
      await createOrg(name.trim(), slug.trim());
      setName("");
      setSlug("");
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "failed to create org");
    }
  }

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <h1 className="text-2xl font-semibold">Your organizations</h1>

      <div className="mt-6 flex gap-2">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Org name"
          className="flex-1 rounded-lg border px-3 py-2"
        />
        <input
          value={slug}
          onChange={(e) => setSlug(e.target.value)}
          placeholder="slug"
          className="w-32 rounded-lg border px-3 py-2"
        />
        <button onClick={create} className="rounded-lg bg-black px-4 py-2 text-white">
          Create
        </button>
      </div>
      {error && <p className="mt-2 text-sm text-red-500">{error}</p>}

      <ul className="mt-8 divide-y rounded-xl border">
        {orgs.length === 0 && (
          <li className="p-4 text-gray-400">
            No organizations yet — sign in and create one.
          </li>
        )}
        {orgs.map((o) => (
          <li
            key={o.id}
            className="flex items-center justify-between p-4 hover:bg-gray-50"
            onClick={() => setActiveOrg(o.id)}
          >
            <div>
              <div className="font-medium">{o.name}</div>
              <div className="text-xs text-gray-400">/{o.slug}</div>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <span className="rounded-full bg-gray-100 px-2 py-0.5">{o.plan}</span>
              <span className="text-gray-400">{o.role}</span>
            </div>
          </li>
        ))}
      </ul>
    </main>
  );
}
