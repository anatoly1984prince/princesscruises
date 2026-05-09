import { Page, expect } from '@playwright/test';

export class RegistrationPage {
  constructor(private readonly page: Page) {}

  // ── Setup ─────────────────────────────────────────────────────────────────────

  /**
   * OwnID SDK (cdn.ownid.com) intercepts the form's submit event and crashes when its
   * CDN is unreachable from automation, silently blocking account creation.
   * Stub it before navigation so the form's native submit handler fires normally.
   */
  async stubOwnId(): Promise<void> {
    await this.page.route('**/cdn.ownid.com/**', (route) =>
      route.fulfill({ status: 200, contentType: 'application/javascript', body: 'window.ownid=()=>({}); ' })
    );
  }

  // ── Navigation ────────────────────────────────────────────────────────────────

  async goto(): Promise<void> {
    await this.page.goto('/my-princess/create-account/');
    await this.page.waitForLoadState('domcontentloaded');
    await this.page.waitForTimeout(3000); // wait for React hydration
  }

  async dismissPrivacyBanner(): Promise<void> {
    const close = this.page.locator('[aria-label="Close privacy notice "], .onetrust-close-btn-handler').first();
    if (await close.isVisible({ timeout: 5000 }).catch(() => false)) await close.click();
  }

  // ── Form helpers ──────────────────────────────────────────────────────────────

  /** Type character-by-character to trigger React synthetic events. */
  private async type(selector: string, value: string): Promise<void> {
    const el = this.page.locator(selector);
    await el.click();
    await el.pressSequentially(value, { delay: 50 });
  }

  // ── Field setters ─────────────────────────────────────────────────────────────

  async selectTitle(value: string): Promise<void> {
    await this.page.locator('select[aria-label="Title"]').selectOption(value);
  }

  async fillFirstName(value: string): Promise<void> {
    await this.type('#firstName', value);
  }

  async fillLastName(value: string): Promise<void> {
    await this.type('#lastName', value);
  }

  async fillEmail(value: string): Promise<void> {
    await this.type('#contactEmail', value);
  }

  async fillPassword(value: string): Promise<void> {
    await this.type('#password', value);
  }

  async fillDateOfBirth(month: string, day: string, year: string): Promise<void> {
    await this.page.locator('select[aria-label="Birthday Month selection"]').selectOption(month);
    await this.page.locator('select[aria-label="Birthday Day selection"]').selectOption(day);
    await this.page.locator('select[aria-label="Birthday Year selection"]').selectOption(year);
  }

  async fillAddress(value: string): Promise<void> {
    await this.type('#address1', value);
  }

  async fillCity(value: string): Promise<void> {
    await this.type('#city', value);
  }

  async selectState(value: string): Promise<void> {
    await this.page.locator('select[aria-label="State/Province"]').selectOption(value);
  }

  async fillZip(value: string): Promise<void> {
    await this.type('#zip', value);
  }

  async fillPhone(value: string): Promise<void> {
    await this.type('#cellPhone', value);
  }

  async selectCruisedBefore(answer: 'Yes, with Princess' | 'Yes, only with cruise lines other than Princess' | 'No'): Promise<void> {
    await this.page.locator(`input[aria-label="${answer}"]`).check();
  }

  // ── Submit & verify ───────────────────────────────────────────────────────────

  async submitForm(): Promise<void> {
    const btn = this.page.locator('button[type="submit"]');
    await btn.scrollIntoViewIfNeeded();
    await btn.click();
  }

  async verifySuccess(): Promise<void> {
    // Successful registration redirects to book.princess.com/captaincircle/myPrincess.page
    await expect(this.page).toHaveURL(/myPrincess\.page|my-princess\/home|dashboard/i, { timeout: 30000 });
    console.log(`Registration confirmed. URL: ${this.page.url()}`);
  }
}
