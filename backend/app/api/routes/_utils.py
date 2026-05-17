from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder


PROJECT_ROOT = Path(__file__).resolve().parents[4]
API_TMP_DIR = PROJECT_ROOT / "reports" / "api_tmp"


async def save_upload_to_temp_csv(upload: UploadFile) -> Path:
    filename = upload.filename or ""
    if not filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Only .csv uploads are supported.",
                "error_code": "INVALID_FILE_TYPE",
                "message": "Only .csv uploads are supported.",
                "details": {"filename": filename},
            },
        )

    content = await upload.read()
    if not content or not content.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Uploaded CSV file is empty.",
                "error_code": "EMPTY_UPLOAD",
                "message": "Uploaded CSV file is empty.",
                "details": {"filename": filename},
            },
        )

    API_TMP_DIR.mkdir(parents=True, exist_ok=True)
    path = API_TMP_DIR / f"{uuid4().hex}.csv"
    path.write_bytes(content)
    return path


def cleanup_paths(*paths: Path | None) -> None:
    for path in paths:
        if path is None:
            continue
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


def api_json(value):
    return jsonable_encoder(value)


def validation_error_response(errors, row_count: int = 0) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail={
            "valid": False,
            "row_count": row_count,
            "errors": api_json(errors),
            "error_code": "VALIDATION_ERROR",
            "message": "Validation failed.",
            "details": {"errors": api_json(errors)},
        },
    )


def error_response(
    message: str, status_code: int = 400, error_code: str = "REQUEST_ERROR"
) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={
            "error": message,
            "error_code": error_code,
            "message": message,
            "details": None,
        },
    )
