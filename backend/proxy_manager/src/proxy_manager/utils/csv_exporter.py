"""CSV export utilities for activity logs."""

import csv
import io
from typing import List
from fastapi.responses import StreamingResponse
from datetime import datetime

from ..models import ActivityLog


def export_logs_to_csv(
    logs: List[ActivityLog], filename: str | None = None
) -> StreamingResponse:
    """
    Export activity logs to CSV format.

    Args:
        logs: List of ActivityLog objects
        filename: Optional filename for download

    Returns:
        StreamingResponse with CSV data
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"activity_logs_{timestamp}.csv"

    # Create in-memory CSV
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "id",
            "timestamp",
            "user_id",
            "endpoint",
            "method",
            "status_code",
            "target_url",
            "ip_address",
        ],
    )

    writer.writeheader()

    for log in logs:
        writer.writerow(
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat() if log.timestamp else "",
                "user_id": log.user_id,
                "endpoint": log.endpoint,
                "method": log.method,
                "status_code": log.status_code,
                "target_url": log.target_url or "",
                "ip_address": log.ip_address or "",
            }
        )

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
