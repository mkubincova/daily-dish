from starlette.types import ASGIApp, Receive, Scope, Send


class ForwardedHostMiddleware:
    """Rewrite the scope's `host` (and `scheme`) from custom forwarding
    headers set by the Vercel proxy so `request.url_for()` yields URLs
    against the original frontend origin.

    We use bespoke header names (`x-original-host` / `x-original-proto`)
    rather than the standard `x-forwarded-*` set because Railway's
    Fastly-based edge normalizes the standard headers and rewrites them
    to its own origin before the request reaches the container."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            original_host: bytes | None = None
            original_proto: bytes | None = None
            for name, value in scope["headers"]:
                if name == b"x-original-host":
                    original_host = value
                elif name == b"x-original-proto":
                    original_proto = value
            if original_host:
                scope = {
                    **scope,
                    "headers": [
                        *((name, value) for name, value in scope["headers"] if name != b"host"),
                        (b"host", original_host),
                    ],
                }
            if original_proto:
                scope = {**scope, "scheme": original_proto.decode("latin-1")}
        await self.app(scope, receive, send)
