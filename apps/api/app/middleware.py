from starlette.types import ASGIApp, Receive, Scope, Send


class ForwardedHostMiddleware:
    """Rewrite the scope's `host` header from `X-Forwarded-Host` so
    `request.url_for()` yields URLs against the original frontend origin
    when traffic arrives via the Vercel proxy. Uvicorn's --proxy-headers
    handles scheme/client but not host."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            forwarded_host: bytes | None = None
            for name, value in scope["headers"]:
                if name == b"x-forwarded-host":
                    forwarded_host = value
                    break
            if forwarded_host:
                scope = {
                    **scope,
                    "headers": [
                        *((name, value) for name, value in scope["headers"] if name != b"host"),
                        (b"host", forwarded_host),
                    ],
                }
        await self.app(scope, receive, send)
