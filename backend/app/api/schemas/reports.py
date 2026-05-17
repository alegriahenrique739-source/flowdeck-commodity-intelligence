from __future__ import annotations

EXCEL_REPORT_RESPONSES = {
    200: {
        "description": "Generated FlowDeck Excel workbook.",
        "content": {
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
                "schema": {"type": "string", "format": "binary"}
            }
        },
    }
}

