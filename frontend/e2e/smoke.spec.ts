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

test("what-if scenario tool re-runs predictions with a forced DNF", async ({ page }) => {
  await page.goto("/whatif");
  await expect(page.getByRole("heading", { name: "What If?" })).toBeVisible();

  const selects = await page.locator("select").all();
  await selects[0].selectOption({ label: "2024 Italian Grand Prix" });
  await page.waitForTimeout(500); // driver options repopulate once the prediction loads
  const refreshedSelects = await page.locator("select").all();
  await refreshedSelects[2].selectOption("leclerc"); // race, grid-driver, dnf-driver

  await page.getByRole("button", { name: "Run Scenario" }).click();
  await expect(page.getByText("Simulated scenario")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText("DNF probability manually set to 100%")).toBeVisible();
});

test("championship page projects the title fight with probabilities", async ({ page }) => {
  await page.goto("/championship");
  await expect(page.getByRole("heading", { name: "Title Fight" })).toBeVisible();
  await expect(page.getByText("Stated assumption:")).toBeVisible();
  await expect(page.getByText("Full Driver Standings Projection")).toBeVisible();
});

test("beat the model lets you reorder a grid and lock in a comparison", async ({ page }) => {
  await page.goto("/beat-the-model");
  await expect(page.getByRole("heading", { name: "Beat the Model" })).toBeVisible();
  await expect(page.getByText("Your Grid")).toBeVisible();

  const firstDownButton = page.getByRole("button", { name: /Move .* down/ }).first();
  await firstDownButton.click();

  await page.getByRole("button", { name: "Lock In My Grid" }).click();
  await expect(page.getByText("You vs Model")).toBeVisible();
  await expect(page.getByText("Exact position matches")).toBeVisible();
});
