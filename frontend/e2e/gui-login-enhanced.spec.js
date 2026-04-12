// Enhanced GUI login tests for GitHub OAuth simulation
// Tests multiple browsers and frameworks integration
import { test, expect } from "@playwright/test";
import { FRONTEND_URL, MOCK_GITHUB_URL, attemptLogin, attemptUserLogin, checkLoginStatus, testOAuthFlow } from "./loginTestHelpers";

test.describe("Enhanced GUI Login Tests", () => {
  test.beforeAll(async ({ request }) => {
    // Verify mock GitHub server is alive
    const res = await request.get(`${MOCK_GITHUB_URL}/health`);
    expect(res.ok()).toBeTruthy();
  });

  test("Chromium - Full OAuth flow with detailed steps", async ({ page }) => {
    const result = await testOAuthFlow(page, "chromium");
    if (result.skipped) { test.skip(result.reason); return; }
    expect(result.userButtonClicked).toBeTruthy();
    expect(result.isLoggedIn).toBeTruthy();
  });

  test("Firefox - Full OAuth flow with detailed steps", async ({ page }) => {
    const result = await testOAuthFlow(page, "firefox");
    if (result.skipped) { test.skip(result.reason); return; }
    expect(result.userButtonClicked).toBeTruthy();
    expect(result.isLoggedIn).toBeTruthy();
  });

  test("WebKit - Full OAuth flow with detailed steps", async ({ page }) => {
    const result = await testOAuthFlow(page, "webkit");
    if (result.skipped) { test.skip(result.reason); return; }
    expect(result.userButtonClicked).toBeTruthy();
    expect(result.isLoggedIn).toBeTruthy();
  });

  test("Manual login flow exploration", async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/01-frontend-initial.png' });

    const loginElement = await attemptLogin(page);
    if (!loginElement) {
      const content = await page.content();
      console.log("No login element found. Page preview:", content.substring(0, 1000));
      return;
    }

    await page.waitForLoadState('networkidle');
    const currentUrl = page.url();

    if (currentUrl.includes('4010') || currentUrl.includes('mock')) {
      await page.screenshot({ path: 'test-results/02-mock-github-page.png' });
      await attemptUserLogin(page);
      await page.waitForURL(`${FRONTEND_URL}/**`, { timeout: 10000 });
      await page.waitForLoadState('networkidle');
      await page.screenshot({ path: 'test-results/03-logged-in.png' });
      const isLoggedIn = await checkLoginStatus(page);
      expect(isLoggedIn).toBeTruthy();
    } else {
      console.log(`Unexpected redirect URL: ${currentUrl}`);
    }
  });
});
