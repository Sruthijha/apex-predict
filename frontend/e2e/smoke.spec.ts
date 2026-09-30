import { expect, test } from "@playwright/test";

// Requires the backend API (default http://localhost:8000, seeded DB) running
// alongside the frontend dev server. See DEPLOYMENT.md / README "Local setup".

test("homepage loads and shows the next race", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /apexpredict/i })).toBeVisible();
  await expect(page.getByText("Next Race")).toBeVisible();
});

test("navigating to a driver page shows career stats", async ({ page }) => {
  await page.goto("/drivers/max_verstappen");
  await expect(page.getByRole("heading", { name: "MAX VERSTAPPEN" })).toBeVisible();
  await expect(page.getByText("Career Wins")).toBeVisible();
});

test("model lab shows honest evaluation metrics", async ({ page }) => {
  await page.goto("/model");
  await expect(page.getByRole("heading", { name: "Under the Hood" })).toBeVisible();
  await expect(page.getByText("Finishing Position Model")).toBeVisible();
  await expect(page.getByText("linear_regression").first()).toBeVisible();
});

test("race lab runs a Monte Carlo simulation end to end", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Race Lab" }).click();
  await expect(page.getByRole("heading", { name: "Monte Carlo Simulator" })).toBeVisible();

  await page.getByRole("button", { name: "Simulate Race" }).click();
  await expect(page.getByText("races simulated")).toBeVisible({ timeout: 20_000 });
  await expect(page.getByText("Most Common Podium")).toBeVisible();
});

test("driver comparison shows head-to-head stats once two drivers are picked", async ({ page }) => {
  await page.goto("/compare");
  const [selectA, selectB] = await page.locator("select").all();
  await selectA.selectOption("leclerc");
  await selectB.selectOption("norris");
  await expect(page.getByText("Season Points")).toBeVisible();
  await expect(page.getByText("VS")).toBeVisible();
});
