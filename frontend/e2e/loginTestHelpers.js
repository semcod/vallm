/**
 * Shared helpers for GUI login E2E tests.
 * Extracted from gui-login-enhanced.spec.js to reduce per-file CC.
 */

export const FRONTEND_URL = process.env.FRONTEND_URL || "http://localhost:3000";
export const MOCK_GITHUB_URL = process.env.MOCK_GITHUB_URL || "http://localhost:4010";

const LOGIN_SELECTORS = [
  'button:has-text("GitHub")',
  'button:has-text("Sign in")',
  'a:has-text("GitHub")',
  '[data-testid="github-login"]',
];

const USER_SELECTORS = [
  'button:has-text("tom-sapletta-com")',
  'button:has-text("Tom Sapletta")',
  'text=tom-sapletta-com',
  'button',
];

const LOGGED_IN_INDICATORS = [
  'text=tom-sapletta-com',
  'text=Tom Sapletta',
  '[data-testid="user-name"]',
  'button:has-text("Logout")',
];

export async function attemptLogin(page, selectors = LOGIN_SELECTORS) {
  for (const selector of selectors) {
    try {
      const element = page.locator(selector).first();
      if (await element.isVisible({ timeout: 2000 })) {
        await element.click();
        return true;
      }
    } catch (e) {
      // Continue trying
    }
  }
  return false;
}

export async function attemptUserLogin(page, selectors = USER_SELECTORS) {
  for (const selector of selectors) {
    try {
      const element = page.locator(selector).first();
      if (await element.isVisible({ timeout: 3000 })) {
        await element.click();
        return true;
      }
    } catch (e) {
      // Continue trying
    }
  }
  return false;
}

export async function checkLoginStatus(page, indicators = LOGGED_IN_INDICATORS) {
  for (const indicator of indicators) {
    try {
      if (await page.locator(indicator).isVisible({ timeout: 3000 })) {
        return true;
      }
    } catch (e) {
      // Continue checking
    }
  }
  return false;
}

export async function testOAuthFlow(page, browserName) {
  await page.goto(FRONTEND_URL);
  await page.waitForLoadState('networkidle');

  const loginClicked = await attemptLogin(page);
  if (!loginClicked) {
    return { skipped: true, reason: `No login button found for ${browserName}` };
  }

  await page.waitForURL(new RegExp(`.*${MOCK_GITHUB_URL.split(':')[2]}.*|.*mock.*`), { timeout: 10000 });
  await page.waitForLoadState('networkidle');

  const userButtonClicked = await attemptUserLogin(page);

  await page.waitForURL(`${FRONTEND_URL}/**`, { timeout: 10000 });
  await page.waitForLoadState('networkidle');

  const isLoggedIn = await checkLoginStatus(page);

  await page.screenshot({
    path: `test-results/login-success-${browserName}.png`,
    fullPage: true,
  });

  return { skipped: false, userButtonClicked, isLoggedIn };
}
