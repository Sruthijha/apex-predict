# Apex Predict — Frontend

Next.js frontend for [Apex Predict](../README.md). See the repo root
README for the full project overview, architecture, and setup — the
short version:

```bash
npm install
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local
npm run dev
```

- `npm run lint` / `npx tsc --noEmit` / `npm run build` — checks CI also runs
- `npm run test:e2e` — Playwright smoke tests (needs the backend running with seeded data)
