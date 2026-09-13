import re
import threading
from datetime import UTC
from pathlib import Path

from backend.app.services.workflows import (
    LocalRunRegistry,
    RunInputFiles,
    RunMetadata,
    RunOutputFiles,
)

RUN_ID = re.compile(r"FD-RUN-[0-9]{8}-[0-9]{6}-[A-F0-9]{6}")


class PublicDemoStorageFull(ValueError):
    pass


class PublicDemoRegistry(LocalRunRegistry):
    """Separate synthetic-demo directory, never a tenant/customer store."""

    def __init__(self, project_root: Path, max_runs: int):
        super().__init__(
            runs_root=project_root / "runs" / "public-demo", project_root=project_root
        )
        self.max_runs = max_runs
        self.lock = threading.RLock()
        self._check_root()

    def _check_root(self):
        if self.runs_root.resolve() != self.runs_root.absolute():
            raise ValueError("Public demo storage must not use linked directories.")

    def run_dir(self, run_id: str) -> Path:
        self._check_root()
        if not RUN_ID.fullmatch(run_id):
            raise ValueError("Invalid public run ID.")
        path = self.runs_root / run_id
        if path.resolve() != path.absolute():
            raise ValueError("Linked public run directories are not allowed.")
        return path

    def create_run_dir(self, run_id: str) -> Path:
        with self.lock:
            self._check_root()
            self.runs_root.mkdir(parents=True, exist_ok=True)
            # Count even invalid entries; failed/partial runs must not bypass the cap.
            if sum(1 for _ in self.runs_root.iterdir()) >= self.max_runs:
                raise PublicDemoStorageFull(
                    "Public demo storage is full. Operator review is required; no files were deleted."
                )
            return super().create_run_dir(run_id)

    def _metadata_file(self, run_id: str) -> Path:
        path = self.metadata_path(run_id)
        if path.resolve() != path.absolute():
            raise ValueError("Linked metadata files are not allowed.")
        return path

    def write_metadata(self, metadata: RunMetadata) -> Path:
        with self.lock:
            path = self._metadata_file(metadata.run_id)
            # Failed workflow diagnostics stay private to server handling, not public runs.
            safe = self._public_metadata(metadata)
            path.write_text(safe.model_dump_json(indent=2), encoding="utf-8")
            return path

    def read_metadata(self, run_id: str) -> RunMetadata:
        with self.lock:
            path = self._metadata_file(run_id)
            with path.open("rb") as file:
                data = file.read(65537)
            if len(data) > 65536:
                raise ValueError("Public metadata is too large.")
            record = RunMetadata.model_validate_json(data)
            if record.run_id != run_id:
                raise ValueError("Public metadata ID does not match its directory.")
            return self._public_metadata(record)

    def _public_metadata(self, record: RunMetadata) -> RunMetadata:
        return record.model_copy(
            update={
                "input_files": RunInputFiles(
                    market_data_file="data/sample/market_data/valid_brent_wti_futures.csv",
                    futures_positions_file="data/sample/positions/valid_futures_positions.csv",
                    physical_cargoes_file="data/sample/positions/valid_physical_cargoes.csv",
                ),
                "output_files": RunOutputFiles(
                    excel_report_path=f"runs/public-demo/{record.run_id}/flowdeck_report.xlsx"
                    if record.output_files.excel_report_path
                    else None
                ),
                "errors": ("Synthetic demo workflow failed. Contact the operator.",)
                if record.errors
                else (),
                "notes": "Backend-owned synthetic public demo. Shared demonstration output; not a private portfolio.",
            }
        )

    def list_metadata(self, limit: int | None = None) -> list[RunMetadata]:
        self._check_root()
        if not self.runs_root.exists():
            return []
        records = []
        for path in self.runs_root.iterdir():
            try:
                records.append(self.read_metadata(path.name))
            except (OSError, ValueError):
                continue
        records.sort(
            key=lambda r: (
                r.created_at.replace(tzinfo=UTC)
                if r.created_at.tzinfo is None
                else r.created_at
            ),
            reverse=True,
        )
        return records[:limit] if limit is not None else records

    def validate_report_path_for_run(
        self, run_id: str, report_path: str | Path
    ) -> Path:
        path = self.report_path(run_id)
        if path.resolve() != path.absolute():
            raise ValueError("Linked public reports are not allowed.")
        # Only this filename is downloadable, never an arbitrary metadata path.
        return super().validate_report_path_for_run(run_id, path)
