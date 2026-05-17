from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from backend.app.services.workflows.run_metadata import RunMetadata


PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_RUNS_ROOT = PROJECT_ROOT / "runs"


class LocalRunRegistry:
    def __init__(
        self,
        runs_root: str | Path | None = None,
        project_root: str | Path = PROJECT_ROOT,
    ) -> None:
        self.project_root = Path(project_root)
        self.runs_root = Path(runs_root) if runs_root is not None else DEFAULT_RUNS_ROOT

    def run_dir(self, run_id: str) -> Path:
        return self.runs_root / run_id

    def metadata_path(self, run_id: str) -> Path:
        return self.run_dir(run_id) / "run_metadata.json"

    def report_path(self, run_id: str) -> Path:
        return self.run_dir(run_id) / "flowdeck_report.xlsx"

    def create_run_dir(self, run_id: str) -> Path:
        path = self.run_dir(run_id)
        path.mkdir(parents=True, exist_ok=False)
        return path

    def write_metadata(self, metadata: RunMetadata) -> Path:
        path = self.metadata_path(metadata.run_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(metadata.model_dump_json(indent=2), encoding="utf-8")
        return path

    def read_metadata(self, run_id: str) -> RunMetadata:
        return RunMetadata.model_validate_json(
            self.metadata_path(run_id).read_text(encoding="utf-8")
        )

    def get_run_report_path(self, run_id: str) -> Path:
        metadata = self.read_metadata(run_id)
        report_path = metadata.output_files.excel_report_path
        if not report_path:
            raise FileNotFoundError("Run metadata does not include an Excel report path.")

        return self.validate_report_path_for_run(run_id, report_path)

    def validate_report_path_for_run(self, run_id: str, report_path: str | Path) -> Path:
        path = Path(report_path)
        if not path.is_absolute():
            path = self.project_root / path

        resolved_path = path.resolve()
        expected_dir = self.run_dir(run_id).resolve()
        try:
            resolved_path.relative_to(expected_dir)
        except ValueError as exc:
            raise ValueError("Report path is outside the expected run folder.") from exc

        if not resolved_path.exists() or not resolved_path.is_file():
            raise FileNotFoundError("Run report file was not found.")

        return resolved_path

    def list_metadata(self, limit: int | None = None) -> list[RunMetadata]:
        if not self.runs_root.exists():
            return []

        records = []
        for path in self.runs_root.glob("*/run_metadata.json"):
            try:
                records.append(
                    RunMetadata.model_validate_json(path.read_text(encoding="utf-8"))
                )
            except (OSError, ValueError, ValidationError):
                continue

        records.sort(key=lambda record: record.created_at, reverse=True)
        return records[:limit] if limit is not None else records

    def project_relative_path(self, path: str | Path) -> str:
        resolved = Path(path).resolve()
        try:
            return resolved.relative_to(self.project_root.resolve()).as_posix()
        except ValueError:
            return str(path)
