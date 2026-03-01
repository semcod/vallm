"""Sandbox abstraction layer for safe code execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from vallm.config import VallmSettings


@dataclass
class ExecutionResult:
    """Result of sandboxed code execution."""

    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    timed_out: bool = False
    duration_ms: float = 0.0
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.exit_code == 0 and not self.timed_out and self.error is None


class SandboxRunner:
    """Unified interface for running code in a sandbox."""

    def __init__(self, settings: Optional[VallmSettings] = None):
        if settings is None:
            settings = VallmSettings()
        self.backend_name = settings.sandbox_backend
        self.timeout = settings.sandbox_timeout
        self.memory_limit = settings.sandbox_memory_limit

    def run(self, code: str, language: str = "python") -> ExecutionResult:
        """Execute code in the configured sandbox backend."""
        if self.backend_name == "subprocess":
            return self._run_subprocess(code, language)
        elif self.backend_name == "docker":
            return self._run_docker(code, language)
        else:
            return ExecutionResult(
                exit_code=1,
                error=f"Unknown sandbox backend: {self.backend_name}",
            )

    def _run_subprocess(self, code: str, language: str) -> ExecutionResult:
        """Run code in a subprocess with resource limits."""
        import subprocess
        import tempfile
        import time
        import os

        ext_map = {"python": ".py", "javascript": ".js", "c": ".c"}
        cmd_map = {"python": ["python3"], "javascript": ["node"]}

        ext = ext_map.get(language, ".txt")
        cmd_prefix = cmd_map.get(language)

        if cmd_prefix is None:
            return ExecutionResult(
                exit_code=1,
                error=f"Unsupported language for subprocess: {language}",
            )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=ext, delete=False
        ) as f:
            f.write(code)
            tmp_path = f.name

        try:
            start = time.monotonic()
            proc = subprocess.run(
                cmd_prefix + [tmp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            duration = (time.monotonic() - start) * 1000

            return ExecutionResult(
                stdout=proc.stdout,
                stderr=proc.stderr,
                exit_code=proc.returncode,
                duration_ms=duration,
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                exit_code=124,
                timed_out=True,
                error=f"Execution timed out after {self.timeout}s",
            )
        except Exception as e:
            return ExecutionResult(exit_code=1, error=str(e))
        finally:
            os.unlink(tmp_path)

    def _run_docker(self, code: str, language: str) -> ExecutionResult:
        """Run code in a Docker container (requires docker package)."""
        try:
            import docker

            client = docker.from_env()

            image_map = {
                "python": "python:3.12-slim",
                "javascript": "node:20-slim",
            }
            cmd_map = {
                "python": ["python3", "-c", code],
                "javascript": ["node", "-e", code],
            }

            image = image_map.get(language, "python:3.12-slim")
            cmd = cmd_map.get(language, ["python3", "-c", code])

            container = client.containers.run(
                image,
                cmd,
                detach=True,
                network_disabled=True,
                read_only=True,
                mem_limit=self.memory_limit,
                cpu_quota=50000,
            )

            result = container.wait(timeout=self.timeout)
            logs = container.logs().decode("utf-8")
            container.remove()

            return ExecutionResult(
                stdout=logs,
                exit_code=result.get("StatusCode", 1),
            )
        except ImportError:
            return ExecutionResult(
                exit_code=1,
                error="docker package not installed. pip install docker",
            )
        except Exception as e:
            return ExecutionResult(exit_code=1, error=str(e))
