import os
from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass(frozen=True)
class DeploymentPolicy:
    mode: str = "local"
    public_max_runs: int = 100

    @property
    def is_public_demo(self) -> bool:
        return self.mode == "public_demo"

    @classmethod
    def from_env(cls, origins: list[str]):
        mode = os.getenv("FLOWDECK_DEPLOYMENT_MODE", "local")
        if mode not in {"local", "public_demo"}:
            raise ValueError("FLOWDECK_DEPLOYMENT_MODE must be local or public_demo.")
        if mode == "local":
            return cls()
        if os.getenv("FLOWDECK_ENABLE_LOCAL_IMPORTS", "false").lower() != "false":
            raise ValueError(
                "Public demo requires FLOWDECK_ENABLE_LOCAL_IMPORTS=false."
            )
        if not os.getenv("FLOWDECK_ALLOWED_ORIGINS") or not origins:
            raise ValueError("Public demo requires explicit HTTPS CORS origins.")
        for origin in origins:
            try:
                parsed = urlsplit(origin)
                valid = (
                    parsed.scheme == "https"
                    and parsed.hostname
                    and parsed.port != 0
                    and not parsed.username
                    and not parsed.password
                    and not parsed.path
                    and not parsed.query
                    and not parsed.fragment
                    and "*" not in origin
                    and not any(ord(c) <= 32 or ord(c) == 127 for c in origin)
                )
            except ValueError:
                valid = False
            if not valid:
                raise ValueError(
                    "Public demo requires exact HTTPS origins without paths, credentials or wildcards."
                )
        try:
            maximum = int(os.getenv("FLOWDECK_PUBLIC_MAX_RUNS", "100"))
        except ValueError as exc:
            raise ValueError(
                "FLOWDECK_PUBLIC_MAX_RUNS must be an integer from 1 to 1000."
            ) from exc
        if not 1 <= maximum <= 1000:
            raise ValueError(
                "FLOWDECK_PUBLIC_MAX_RUNS must be an integer from 1 to 1000."
            )
        return cls(mode=mode, public_max_runs=maximum)
