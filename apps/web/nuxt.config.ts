// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
	compatibilityDate: "2025-07-15",
	devtools: { enabled: true },
	modules: ["@pinia/nuxt", "@nuxtjs/tailwindcss"],
	css: ["~/assets/css/main.css"],
	app: {
		head: {
			htmlAttrs: { lang: "en" },
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
				{ rel: "icon", href: "/favicon.ico" },
				{
					rel: "icon",
					type: "image/png",
					sizes: "16x16",
					href: "/favicon-16x16.png",
				},
				{
					rel: "icon",
					type: "image/png",
					sizes: "32x32",
					href: "/favicon-32x32.png",
				},
				{ rel: "apple-touch-icon", href: "/apple-touch-icon.png" },
				{ rel: "manifest", href: "/site.webmanifest" },
			],
			meta: [{ name: "theme-color", content: "#E8DEC8" }],
		},
	},
	runtimeConfig: {
		public: {
			siteUrl: process.env.NUXT_PUBLIC_SITE_URL || "http://localhost:3000",
		},
	},
	vite: {
		optimizeDeps: {
			include: [
				"@vue/devtools-core",
				"@vue/devtools-kit",
				"openapi-fetch",
				"@phosphor-icons/vue",
			],
		},
	},
});
