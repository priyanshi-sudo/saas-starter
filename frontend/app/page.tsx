import Link from "next/link";

const TIERS = [
  { name: "Free", price: "$0", features: ["1 org", "3 members", "Community support"] },
  { name: "Pro", price: "$29", features: ["Unlimited orgs", "Seat billing", "Email support"] },
  { name: "Enterprise", price: "Custom", features: ["SSO / SCIM", "Audit log", "SLA"] },
];

export default function Landing() {
  return (
    <main>
      <header className="border-b">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <span className="font-semibold">SaaS Starter</span>
          <Link
            href="/sign-in"
            className="rounded-lg bg-black px-4 py-2 text-sm text-white"
          >
            Sign in
          </Link>
        </div>
      </header>

      <section className="mx-auto max-w-5xl px-6 py-20 text-center">
        <h1 className="text-4xl font-bold sm:text-5xl">
          Ship your SaaS, not your boilerplate.
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-500">
          Multi-tenant orgs, RBAC, Stripe seat-based billing, transactional
          email, and a typed end-to-end API — wired up and ready.
        </p>
        <Link
          href="/app"
          className="mt-8 inline-block rounded-lg bg-black px-6 py-3 text-white"
        >
          Open the app
        </Link>
      </section>

      <section className="mx-auto max-w-5xl px-6 pb-24">
        <div className="grid gap-6 sm:grid-cols-3">
          {TIERS.map((t) => (
            <div key={t.name} className="rounded-2xl border p-6">
              <h3 className="text-lg font-semibold">{t.name}</h3>
              <p className="mt-2 text-3xl font-bold">{t.price}</p>
              <ul className="mt-4 space-y-2 text-sm text-gray-600">
                {t.features.map((f) => (
                  <li key={f}>✓ {f}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
