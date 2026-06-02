"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { setToken } from "@/lib/auth";

export default function SignIn() {
  const router = useRouter();
  const [token, setTokenInput] = useState("");

  // The real app swaps this for Supabase Auth (email + OAuth). For local dev
  // you can paste a Supabase access token to exercise the API directly.
  function submit() {
    if (!token.trim()) return;
    setToken(token.trim());
    router.push("/app");
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6">
      <h1 className="text-2xl font-semibold">Sign in</h1>
      <p className="mt-2 text-sm text-gray-500">
        Dev mode: paste a Supabase access token to continue.
      </p>
      <input
        value={token}
        onChange={(e) => setTokenInput(e.target.value)}
        placeholder="access token"
        className="mt-6 rounded-lg border px-3 py-2"
      />
      <button
        onClick={submit}
        className="mt-3 rounded-lg bg-black px-4 py-2 text-white"
      >
        Continue
      </button>
    </main>
  );
}
