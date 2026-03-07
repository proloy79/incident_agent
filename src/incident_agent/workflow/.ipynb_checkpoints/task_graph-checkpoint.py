import time
import logging
from typing import Any, Dict, List, Optional, Set, Callable

class Task:
    def __init__(
        self,
        tool_name: str,        
        fn: Callable,          # Already includes retries/backoff/CB inside tool executor
        deps: List[str],
        skip_on_error: bool = False,
    ):
        self.tool_name = tool_name
        self.fn = fn
        self.deps = deps
        self.skip_on_error = skip_on_error


class TaskResult:
    def __init__(self, status: str, latency_ms: int, message: str, value: Any = None):
        self.status = status
        self.latency_ms = latency_ms
        self.message = message
        self.value = value


class TaskGraph:
    def __init__(self, tasks: Dict[str, Task]):
        self.logger = logging.getLogger(__name__)
        self.tasks = tasks
        self.results: Dict[int, TaskResult] = {}        

    def _check_acyclic(self) -> None:
        seen: Set[str] = set()
        stack: Set[str] = set()

        def dfs(n: str) -> None:
            if n in stack:
                raise ValueError(f"cycle detected at {n}")
            if n in seen:
                return

            stack.add(n)
            for d in self.tasks[n].deps:
                if d not in self.tasks:
                    raise KeyError(f"unknown dependency: {d}")
                dfs(d)
            stack.remove(n)
            seen.add(n)

        for name in self.tasks:
            dfs(name)
       
    def _ready(self) -> List[str]:
        """
        Determine which tasks are ready to run 
        """
        ready = []
        for id, task in self.tasks.items():
            self.logger.debug(f"Checking Task({task.tool_name})[{id}] is ready")
            if id in self.results:
                self.logger.debug(f"Task({task.tool_name})[{id}] already completed - ignore")
                continue

            # All deps must be completed
            if not all(d in self.results for d in task.deps):
                self.logger.debug(f"Not all Task({task.tool_name})[{id}] dependencies completed - ignore {task.deps}")
                continue

            # If any dep failed and skip_on_error=False, block
            if not task.skip_on_error:
                if any(self.results[d].status == "error" for d in task.deps):
                    self.logger.debug("Dependencies completed with error - ignore")
                    continue
            self.logger.debug(f"Task({task.tool_name})[{id}] is ready")
            ready.append(id)

        return ready

    async def run(self, *, context: Optional[Dict[str, Any]] = None) -> Dict[str, TaskResult]:
        self.logger.info("TaskGraph starting execution")
        self.logger.debug(f"Task keys: {self.tasks.keys()}")
        ctx = dict(context or {})
        self.logger.debug(f"Initial context: {ctx}")
        
        pending = set(self.tasks.keys())
                
        while pending:
            ran_any = False

            for name in list(pending):
                if name not in self._ready():
                    self.logger.info("Task not ready, skipping")
                    continue

                task = self.tasks[name]
                self.logger.info(f"Running task: {name}")
                self.logger.debug(f"Task deps: {task.deps}")

                start = time.perf_counter()

                try:
                    # retries/backoff/CB appled inside task.fn
                    out = await task.fn(ctx)
                    latency_ms = int((time.perf_counter() - start) * 1000)

                    self.logger.info(f"Task succeeded: {name}")
                    self.logger.debug(f"Output: {out}")

                    self.results[name] = TaskResult(
                        status="ok",
                        latency_ms=latency_ms,
                        message="ok",
                        value = out,
                    )

                    # Merge dict outputs into context
                    if isinstance(out, dict):
                        ctx.update({f"{name}.{k}": v for k, v in out.items()})

                except Exception as e:
                    latency_ms = int((time.perf_counter() - start) * 1000)
                    self.logger.error(f"Task failed: {name} error={e}")

                    self.results[name] = TaskResult(
                        status="error",
                        latency_ms=latency_ms,
                        message=str(e),
                    )

                pending.remove(name)
                ran_any = True

            if not ran_any:
                self.logger.error("Deadlock detected — marking remaining tasks as skipped")
                for name in list(pending):
                    self.results[name] = TaskResult(
                        status="skipped",
                        latency_ms=0,
                        message="blocked by upstream",
                    )
                    pending.remove(name)

        self.logger.info("TaskGraph completed")
        self.logger.debug(f"Final context: {ctx}")
        
        return self.results