import type { Config } from "tailwindcss";

export default {
	content: ["./app/**/*.{vue,ts,tsx}"],
	theme: {
		extend: {
			colors: {
				dish: {
					bg: "#E8DEC8",
					surface: "#F5EFE3",
					fg: "#1C1A18",
					primary: "#1E7888",
					"primary-l": "#2898A8",
					"primary-d": "#145A68",
					secondary: "#C85420",
					"secondary-l": "#D97240",
					"secondary-d": "#A03C18",
					success: "#2A6838",
					"success-l": "#389050",
					"success-d": "#1A4828",
					error: "#C02828",
					muted: "#BEB09A",
				},
			},
			fontFamily: {
				display: ['"Playfair Display"', "Georgia", "serif"],
				sans: ["Jost", "system-ui", "sans-serif"],
				mono: ['"DM Mono"', "ui-monospace", "monospace"],
			},
		},
	},
	plugins: [],
} satisfies Config;
