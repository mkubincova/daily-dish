export type RecipeFilters = {
	categoryItems: string[][];
	tags: string[];
	status: "published" | "draft" | "all";
};

export function useRecipeFilters() {
	const route = useRoute();
	const router = useRouter();

	function readFromQuery(): RecipeFilters {
		const raw = route.query;

		const categoryItemsRaw = Array.isArray(raw.category_items)
			? (raw.category_items as string[])
			: raw.category_items
				? [raw.category_items as string]
				: [];

		const tagsRaw = Array.isArray(raw.tags)
			? (raw.tags as string[])
			: raw.tags
				? [raw.tags as string]
				: [];

		const statusRaw = raw.status as string | undefined;
		const status: RecipeFilters["status"] =
			statusRaw === "published" || statusRaw === "draft" ? statusRaw : "all";

		return {
			categoryItems: categoryItemsRaw.map((g) => g.split(",").filter(Boolean)),
			tags: tagsRaw,
			status,
		};
	}

	const filters = computed(() => readFromQuery());

	function toggleCategoryItem(itemId: string) {
		const current = readFromQuery();
		const flat = current.categoryItems.flat();
		const next = flat.includes(itemId)
			? flat.filter((id) => id !== itemId)
			: [...flat, itemId];

		const query = { ...route.query };
		if (next.length === 0) {
			delete query.category_items;
		} else {
			query.category_items = next.join(",");
		}
		router.push({ query });
	}

	function toggleTag(tagId: string) {
		const current = readFromQuery();
		const next = current.tags.includes(tagId)
			? current.tags.filter((id) => id !== tagId)
			: [...current.tags, tagId];

		const query = { ...route.query };
		if (next.length === 0) {
			delete query.tags;
		} else {
			query.tags = next;
		}
		router.push({ query });
	}

	function setStatus(s: RecipeFilters["status"]) {
		const query = { ...route.query };
		if (s === "all") {
			delete query.status;
		} else {
			query.status = s;
		}
		router.push({ query });
	}

	function clearFilters() {
		const query = { ...route.query };
		delete query.category_items;
		delete query.tags;
		delete query.status;
		router.push({ query });
	}

	return {
		filters,
		toggleCategoryItem,
		toggleTag,
		setStatus,
		clearFilters,
	};
}
