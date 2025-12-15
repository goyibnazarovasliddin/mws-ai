"""
Background worker entrypoint.

Task:
- Script that prepares a Celery worker or RQ worker.
- Processes functions in tasks.py.

Binding:
- Used as `worker` service in docker-compose.yml (if asynchronous architecture).
"""

# not used yet