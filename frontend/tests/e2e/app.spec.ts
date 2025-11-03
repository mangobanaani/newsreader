import { expect, test } from '@playwright/test';
import { setupApiMocks } from './fixtures/mockApi';

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'test-token');
  });

  await setupApiMocks(page);
});

test('home feed renders articles and allows toggling bookmarks', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { name: 'Your Feed' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'AI Breakthrough in Helsinki' })).toBeVisible();

  const bookmarkedArticle = page
    .locator('article')
    .filter({ has: page.getByRole('link', { name: 'AI Breakthrough in Helsinki' }) });

  await expect(bookmarkedArticle.getByRole('button', { name: 'Bookmarked' })).toBeVisible();
  await bookmarkedArticle.getByRole('button', { name: 'Bookmarked' }).click();
  await expect(bookmarkedArticle.getByRole('button', { name: 'Bookmark' })).toBeVisible();

  const secondArticle = page
    .locator('article')
    .filter({ has: page.getByRole('link', { name: 'Nordic Climate Summit Highlights' }) });
  await expect(secondArticle.getByRole('button', { name: 'Bookmark' })).toBeVisible();
});

test('bookmarks page lists saved articles', async ({ page }) => {
  await page.goto('/bookmarks');

  await expect(page.getByRole('heading', { name: 'Bookmarked Articles' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'AI Breakthrough in Helsinki' })).toBeVisible();
  await expect(page.getByText('Nordic Climate Summit Highlights')).toHaveCount(0);
});

test('recommendations surface personalized articles', async ({ page }) => {
  await page.goto('/recommendations');

  await expect(page.getByRole('heading', { name: 'AI Recommendations' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'AI Ethics Panel Releases New Guidelines' })).toBeVisible();
  await expect(page.getByText('92% match')).toBeVisible();
});

test('analytics dashboard renders sentiment and feed insights', async ({ page }) => {
  await page.goto('/analytics');

  await expect(page.getByRole('heading', { name: 'Analytics' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Reading activity' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Sentiment overview' })).toBeVisible();
  await expect(page.getByText('Feed performance')).toBeVisible();
  await expect(page.getByText('Top topics')).toBeVisible();
});

test('feed management allows refreshing sources', async ({ page }) => {
  await page.goto('/feeds');

  await expect(page.getByRole('heading', { name: 'Feed Library' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'My Feeds (1)' })).toBeVisible();

  const refreshAll = page.getByRole('button', { name: 'Refresh All' });
  const refreshCall = page.waitForRequest('**/api/v1/feeds/refresh-all');
  await refreshAll.click();
  await refreshCall;
  await expect(page.getByRole('button', { name: 'Refresh All' })).toBeVisible();
});

test('preferences can be updated and saved', async ({ page }) => {
  await page.goto('/preferences');

  await expect(page.getByRole('heading', { name: 'Preferences & Settings' })).toBeVisible();

  const preferredTopicsCard = page
    .locator('.card')
    .filter({ has: page.getByRole('heading', { name: 'Preferred Topics' }) });
  await preferredTopicsCard.getByPlaceholder('Add a topic...').fill('Renewable Energy');
  await preferredTopicsCard.getByRole('button', { name: 'Add' }).click();
  await expect(preferredTopicsCard.getByText('Renewable Energy')).toBeVisible();

  await page.getByRole('button', { name: 'Save Changes' }).click();
  await expect(page.getByText('Preferences saved successfully!')).toBeVisible();
});

test('login form authenticates the user', async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.removeItem('access_token');
  });
  await page.goto('/login');

  await page.getByLabel('Email').fill('test@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign In' }).click();

  await expect(page.getByRole('heading', { name: 'Your Feed' })).toBeVisible();
});
