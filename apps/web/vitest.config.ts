import { defineVitestConfig } from "@nuxt/test-utils/config";

export default defineVitestConfig({
	test: {
		environment: "happy-dom",
		exclude: ["**/node_modules/**", "**/dist/**", "e2e/**"],
	},
});
