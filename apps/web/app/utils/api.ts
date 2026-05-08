import createClient from "openapi-fetch";
import type { paths } from "~~/types/api";

type Client = ReturnType<typeof createClient<paths>>;

// openapi-fetch builds a `new Request(baseUrl + path)` before invoking fetch.
// In Node SSR that constructor requires an absolute URL — relative paths throw
// — so on the server we need a real origin. In the browser an empty baseUrl is
// fine because the URL resolves against window.location.
//
// We lazy-build the client and cache only on the client side: each SSR pass
// needs the *current* request's origin, which we read via useRequestURL().
let clientCache: Client | null = null;

function getClient(): Client {
	if (import.meta.server) {
		const origin = useRequestURL().origin;
		return createClient<paths>({
			baseUrl: origin,
			credentials: "include",
		});
	}
	if (!clientCache) {
		clientCache = createClient<paths>({
			baseUrl: "",
			credentials: "include",
		});
	}
	return clientCache;
}

// Proxy keeps the singleton call style (`$api.GET("/api/recipes")`) without
// forcing every call site to invoke a composable.
export const $api = new Proxy({} as Client, {
	get(_target, prop: keyof Client) {
		return getClient()[prop];
	},
});
