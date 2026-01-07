import {expect, test} from '@playwright/test';

test('Broken Login Example', async ({page}) => {
    // Navigate to the login page
    await page.goto('https://the-internet.herokuapp.com/login');

    // BUG: Incorrect selector for the username field (shoud be '#username')
    await page.locator('#user-input-field-wrong').fill('tomsmith');

    // Correct password field
    await page.locator('#password').fill('SuperSecretPassword!');

    // BUG: Looking for a button with text "Submit" instead of "Login"
    await page.getByRole('button', {name: 'Submit'}).click();

    // Verification
    await expect(page.locator('#flash')).toContainText('You logged into a secure area!');
});
