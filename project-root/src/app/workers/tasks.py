"""
Background tasks (for Celery / RQ).

Task:
- Defines tasks to perform long-running tasks (ML predict, LLM call, active verification) asynchronously.
- For example: `process_report(report_id)` or `active_verify(finding_id)`.

Linkage:
- These tasks are enqueued when endpoints/analyze.py chooses to run asynchronously.
- worker.py executes these tasks.

Note:
- If using Celery, Redis or another broker and result backend are required.
"""

# not used yet