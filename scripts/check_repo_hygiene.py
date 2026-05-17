"""Read-only repository hygiene check for FlowDeck public demo prep."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

RISKY_PATHS = [
    ".env",
    "frontend/.env.local",
    "frontend/node_modules",
    "frontend/.next",
    "frontend/test-results",
    "frontend/playwright-report",
    "frontend/blob-report",
    ".pytest_cache",
    ".uv-cache",
]

SKIP_DIRS = {
    ".git",
    "frontend/node_modules",
    "frontend/.next",
    "frontend/test-results",
    ".pytest_cache",
    ".uv-cache",
    "__pycache__",
}

SUSPICIOUS_NAME_PARTS = (
    "secret",
    "token",
    "credential",
    "credentials",
    "apikey",
    "api_key",
    "private_key",
)


def warn(message: str, warnings: list[str]) -> None:
    warnings.append(message)


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    warnings: list[str] = []

    for item in RISKY_PATHS:
        path = ROOT / item
        if path.exists():
            warn(f"Found local/generated path: {item}", warnings)

    runs_dir = ROOT / "runs"
    if runs_dir.exists():
        generated_runs = [
            path
            for path in runs_dir.iterdir()
            if path.name != ".gitkeep" and path.exists()
        ]
        if generated_runs:
            warn(
                f"Found {len(generated_runs)} generated run item(s) under runs/.",
                warnings,
            )

    reports_dir = ROOT / "reports"
    if reports_dir.exists():
        generated_reports = [
            path
            for path in reports_dir.rglob("*")
            if path.is_file() and path.name != ".gitkeep"
        ]
        if generated_reports:
            warn(
                f"Found {len(generated_reports)} generated report/test output file(s) under reports/.",
                warnings,
            )

    for path in ROOT.rglob("*"):
        rel = relative(path)
        if any(rel == skip or rel.startswith(f"{skip}/") for skip in SKIP_DIRS):
            continue
        lower_name = path.name.lower()
        if any(part in lower_name for part in SUSPICIOUS_NAME_PARTS):
            warn(f"Suspicious file or folder name: {rel}", warnings)

    if warnings:
        print("FlowDeck repository hygiene warnings:")
        for item in warnings:
            print(f"- {item}")
        print(
            "\nReview warnings before GitHub/public demo release. "
            "See docs/GITHUB_READINESS_CHECKLIST.md."
        )
    else:
        print("FlowDeck repository hygiene check passed with no warnings.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
