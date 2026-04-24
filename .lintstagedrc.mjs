// Staged files arrive as absolute paths. Run each tool from its app dir so
// biome/ruff discover their configs without monorepo-root confusion.

const WEB_PREFIX = "apps/web/";
const API_PREFIX = "apps/api/";

const stripPrefix = (files, prefix) =>
	files
		.map((f) => f.replace(new RegExp(`^.*/${prefix}`), ""))
		.map((f) => JSON.stringify(f))
		.join(" ");

export default {
	"apps/web/**/*.{ts,tsx,vue,js,mjs,mts,cts,json,jsonc}": (files) => {
		const rel = stripPrefix(files, WEB_PREFIX);
		return `bash -c 'cd apps/web && node_modules/.bin/biome check --write --no-errors-on-unmatched ${rel}'`;
	},
	"apps/api/**/*.py": (files) => {
		const rel = stripPrefix(files, API_PREFIX);
		return [
			`bash -c 'cd apps/api && uv run --quiet ruff check --fix ${rel}'`,
			`bash -c 'cd apps/api && uv run --quiet ruff format ${rel}'`,
		];
	},
};
