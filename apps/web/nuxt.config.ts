// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
	compatibilityDate: "2025-07-15",
	devtools: { enabled: true },
	modules: ["@pinia/nuxt", "@nuxtjs/tailwindcss"],
	css: ["~/assets/css/main.css"],
	app: {
		head: {
			link: [
				{ rel: "preconnect", href: "https://fonts.googleapis.com" },
				{
					rel: "preconnect",
					href: "https://fonts.gstatic.com",
					crossorigin: "",
				},
				{
					rel: "stylesheet",
					href: "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400;1,700&family=Jost:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap",
				},
			],
		},
	},
	runtimeConfig: {
		public: {
			apiUrl: process.env.NUXT_PUBLIC_API_URL || "http://localhost:8000",
		},
	},
});
