import { expect, test } from "@playwright/test";

test("landing page loads and reaches the workspace preview", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Explore biology with evidence in view." })).toBeVisible();
  await page.getByRole("link", { name: "Open workspace preview" }).click();
  await expect(page).toHaveURL(/\/explore$/);
  await expect(page.getByRole("heading", { name: "Waiting for verified evidence" })).toBeVisible();
});
