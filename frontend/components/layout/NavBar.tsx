"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import clsx from "clsx";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/championship", label: "Title Fight" },
  { href: "/compare", label: "Head to Head" },
  { href: "/whatif", label: "What If?" },
  { href: "/beat-the-model", label: "Beat the Model" },
  { href: "/drivers", label: "Drivers" },
  { href: "/constructors", label: "Constructors" },
  { href: "/circuits", label: "Circuits" },
  { href: "/model", label: "Under the Hood" },
];

export function NavBar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-apex-dark/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2" onClick={() => setOpen(false)}>
          <span className="h-3 w-3 rounded-full bg-apex-red" aria-hidden />
          <span className="font-display text-xl font-bold tracking-tight text-apex-off-white">
            APEX<span className="text-apex-red">PREDICT</span>
          </span>
        </Link>

        <nav className="hidden gap-1 md:flex">
          {LINKS.map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={clsx(
                  "rounded-sm px-3 py-2 text-sm font-medium uppercase tracking-wide transition-colors",
                  active
                    ? "bg-apex-red text-white"
                    : "text-apex-gray hover:text-apex-off-white",
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        <button
          type="button"
          className="rounded-sm border border-white/20 p-2 text-apex-off-white md:hidden"
          aria-expanded={open}
          aria-label="Toggle navigation"
          onClick={() => setOpen((o) => !o)}
        >
          <span className="block h-0.5 w-5 bg-current" />
          <span className="mt-1 block h-0.5 w-5 bg-current" />
          <span className="mt-1 block h-0.5 w-5 bg-current" />
        </button>
      </div>

      {open && (
        <nav className="flex flex-col border-t border-white/10 bg-apex-dark px-4 py-2 md:hidden">
          {LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setOpen(false)}
              className="rounded-sm px-3 py-3 text-sm font-medium uppercase tracking-wide text-apex-off-white/90 hover:bg-white/5"
            >
              {link.label}
            </Link>
          ))}
        </nav>
      )}
    </header>
  );
}
