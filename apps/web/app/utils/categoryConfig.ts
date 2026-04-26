// Shared per-item display config — auto-imported by Nuxt across all components

export const ITEM_ICONS: Record<string, string> = {
	// Dish type
	soup: "🍲",
	salad: "🥗",
	main: "🥘",
	side: "🥯",
	dessert: "🍰",
	snack: "🥨",
	// Mood
	light: "🥬",
	vegetarian: "🌱",
	spicy: "🌶️",
	hearty: "💪",
	fried: "🍳",
	// Protein
	beef: "🥩",
	chicken: "🍗",
	pork: "🐷",
	fish: "🐟",
	rabbit: "🐰",
	duck: "🦆",
	turkey: "🦃",
	plant_based: "🌿",
};

// Full labels — used in sidebar filters and recipe detail page
export const ITEM_LABELS: Record<string, string> = {
	soup: "Soup",
	salad: "Salad",
	main: "Main Course",
	side: "Side Dish",
	dessert: "Dessert",
	snack: "Snack",
	light: "Light",
	vegetarian: "Vegetarian",
	spicy: "Spicy",
	hearty: "Hearty",
	fried: "Fried",
	beef: "Beef",
	chicken: "Chicken",
	pork: "Pork",
	fish: "Fish",
	rabbit: "Rabbit",
	duck: "Duck",
	turkey: "Turkey",
	plant_based: "Plant-Based",
};

// Compact labels for recipe card badges (must stay short at 9px)
export const DISH_TYPE_LABELS: Record<string, string> = {
	soup: "Soup",
	salad: "Salad",
	main: "Main",
	side: "Side",
	dessert: "Dessert",
	snack: "Snack",
};

// Accent hex colors for dish-type badges — source of truth for the whole app.
// Tailwind cat-* tokens in tailwind.config.ts mirror these values.
export const DISH_TYPE_COLORS: Record<string, string> = {
	main: "#1E7888",
	snack: "#C85420",
	salad: "#2E9048",
	soup: "#C02828",
	side: "#e5a800",
	dessert: "#c13476",
};

// Fallback palette for recipes that have no dish-type category
export const ACCENT_FALLBACK = ["#C85420", "#1E7888", "#2A6838"];

export function accentColorForRecipe(
	categoryItemIds: string[],
	index: number,
): string {
	for (const id of categoryItemIds) {
		if (DISH_TYPE_COLORS[id]) return DISH_TYPE_COLORS[id];
	}
	return ACCENT_FALLBACK[index % ACCENT_FALLBACK.length]!;
}

export function itemIcon(id: string): string {
	return ITEM_ICONS[id] ?? "";
}

export function itemLabel(id: string): string {
	return ITEM_LABELS[id] ?? id.replace(/_/g, " ");
}
