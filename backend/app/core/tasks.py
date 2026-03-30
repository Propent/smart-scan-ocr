import uuid
from typing import Dict, Any

class TaskStore:
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}

    def create_task(self) -> str:
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "status": "pending",
            "progress": 0,
            "result": None,
            "error": None
        }
        return task_id

    def update_task(self, task_id: str, status: str = None, progress: int = None, result: bytes = None, error: str = None, result_data: Any = None):
        if task_id in self.tasks:
            if status:
                self.tasks[task_id]["status"] = status
            if progress is not None:
                self.tasks[task_id]["progress"] = progress
            if result:
                self.tasks[task_id]["result"] = result
            if error:
                self.tasks[task_id]["error"] = error
            if result_data:
                self.tasks[task_id]["result_data"] = result_data

    def get_task(self, task_id: str) -> Dict[str, Any]:
        return self.tasks.get(task_id)

task_store = TaskStore()
