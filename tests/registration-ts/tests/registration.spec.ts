import { test } from '@playwright/test';
import { RegistrationPage } from '../src/pages/RegistrationPage';
import { generateDynamicEmail, printRegistrationSummary } from '../src/utils/emailHelper';
import { USER } from '../src/data/testData';

test('User Registration – create new princess.com account', async ({ page }) => {
  const email = generateDynamicEmail();
  const reg = new RegistrationPage(page);

  // Stub OwnID SDK before navigation (prevents silent submit block)
  await reg.stubOwnId();

  await reg.goto();
  await reg.dismissPrivacyBanner();

  await reg.selectTitle(USER.title);
  await reg.fillFirstName(USER.firstName);
  await reg.fillLastName(USER.lastName);
  await reg.fillEmail(email);
  await reg.fillPassword(USER.password);
  await reg.fillDateOfBirth(USER.dobMonth, USER.dobDay, USER.dobYear);
  await reg.fillAddress(USER.address);
  await reg.fillCity(USER.city);
  await reg.selectState(USER.state);
  await reg.fillZip(USER.zipCode);
  await reg.fillPhone(USER.phone);
  await reg.selectCruisedBefore('No');

  await reg.submitForm();
  await reg.verifySuccess();

  printRegistrationSummary(`${USER.firstName} ${USER.lastName}`, email, USER.password);
});
