import { describe, expect, it } from "vitest";

// Pure parsing functions extracted from useRecipeFilters for unit testing

type RecipeFilters = {
	categoryItems: string[][];
	tags: string[];
	status: "published" | "draft" | "all";
};

function parseQuery(
	raw: Record<string, string | string[] | undefined>,
): RecipeFilters {
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
		categoryItems: categoryItemsRaw.map((g: string) =>
			g.split(",").filter(Boolean),
		),
		tags: tagsRaw as string[],
		status,
	};
}

describe("useRecipeFilters — filter parsing", () => {
	it("returns empty filters from a clean query", () => {
		const f = parseQuery({});
		expect(f.categoryItems).toEqual([]);
		expect(f.tags).toEqual([]);
		expect(f.status).toBe("all");
	});

	it("parses comma-separated category_items as a single OR group", () => {
		const f = parseQuery({ category_items: "soup,salad" });
		expect(f.categoryItems).toEqual([["soup", "salad"]]);
	});

	it("parses repeated category_items as multiple AND groups", () => {
		const f = parseQuery({ category_items: ["soup,salad", "vegetarian"] });
		expect(f.categoryItems).toEqual([["soup", "salad"], ["vegetarian"]]);
	});

	it("parses tags", () => {
		const f = parseQuery({ tags: ["abc-id", "def-id"] });
		expect(f.tags).toEqual(["abc-id", "def-id"]);
	});

	it("parses status=published", () => {
		const f = parseQuery({ status: "published" });
		expect(f.status).toBe("published");
	});

	it("parses status=draft", () => {
		const f = parseQuery({ status: "draft" });
		expect(f.status).toBe("draft");
	});

	it("defaults unknown status to all", () => {
		const f = parseQuery({ status: "unknown" });
		expect(f.status).toBe("all");
	});
});
