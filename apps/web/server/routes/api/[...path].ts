import { getRequestHost, getRequestProtocol, proxyRequest } from "h3";

export default defineEventHandler((event) => {
	const target = process.env.NUXT_API_PROXY_TARGET ?? "http://localhost:8000";
	// Forward the frontend host/proto so FastAPI's url_for() generates callback
	// URLs that point back through this proxy, not directly to the backend port.
	const host = getRequestHost(event, { xForwardedHost: true });
	const proto = getRequestProtocol(event, { xForwardedProto: true });
	return proxyRequest(event, `${target}${event.path}`, {
		fetchOptions: { redirect: "manual" },
		headers: {
			"x-forwarded-host": host,
			"x-forwarded-proto": proto,
		},
	});
});
