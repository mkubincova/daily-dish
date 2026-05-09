import { expect, test } from "@playwright/test";

// Smoke spec for the cooking-mode golden path: anonymous → /, log in via the
// test-only shortcut, navigate to a recipe detail, see title + steps.
//
// Requires the backend to be reachable through the Nuxt `/api/**` proxy with
// `ENVIRONMENT != "production"` so /auth/_test/login isn't 404'd. Locally:
// run `uv run uvicorn app.main:app` in apps/api before `npm run e2e`.

const E2E_EMAIL = "playwright-smoke@example.com";
const E2E_NAME = "Playwright Smoke";

test.describe("recipe golden path", () => {
	let createdRecipeId: string | undefined;

	test.afterEach(async ({ request, baseURL }) => {
		if (!createdRecipeId) return;
		// Soft-delete then hard-delete so the smoke recipe doesn't accumulate in
		// the local dev DB across runs. Auth cookie from the test body is still
		// on the `request` context.
		await request.delete(`${baseURL}/api/recipes/${createdRecipeId}`);
		await request.delete(`${baseURL}/api/recipes/${createdRecipeId}/permanent`);
		createdRecipeId = undefined;
	});

	test("anonymous → login → recipe detail renders title and steps", async ({
		page,
		request,
		baseURL,
	}) => {
		// Anonymous landing.
		await page.goto("/");
		await expect(page).toHaveURL(/\/$/);

		// Authenticate via the test-only shortcut and capture the cookie.
		const loginResp = await request.post(`${baseURL}/api/auth/_test/login`, {
			data: { email: E2E_EMAIL, name: E2E_NAME },
		});
		expect(loginResp.ok()).toBeTruthy();

		// Seed: ensure the smoke user has at least one recipe to open. Public so
		// the SSR fetch on `/r/<slug>` resolves it without needing cookies — the
		// Nuxt `$api` client does not forward the auth cookie during SSR, so a
		// private recipe would 404 from the server-rendered request.
		const seedTitle = `Smoke Recipe ${Date.now()}`;
		const seedStep = "Pour boiling water over the pasta and stir.";
		const createResp = await request.post(`${baseURL}/api/recipes`, {
			data: {
				title: seedTitle,
				description: "Created by Playwright smoke test.",
				is_public: true,
				steps: [{ position: 1, text: seedStep }],
				ingredients: [{ position: 1, name: "Pasta" }],
			},
		});
		expect(createResp.status(), await createResp.text()).toBe(201);
		const created = await createResp.json();
		createdRecipeId = created.id;

		// Carry the auth cookie into the browser context.
		const cookies = await request.storageState();
		await page.context().addCookies(cookies.cookies);

		// Open the recipe detail.
		await page.goto(`/r/${created.slug}`);
		await expect(page.getByRole("heading", { name: seedTitle })).toBeVisible();
		await expect(page.getByText(seedStep)).toBeVisible();
	});
});
