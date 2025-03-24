from typing import Dict, Any, Optional
from dataclasses import dataclass
import json
import os
import datetime
from enum import Enum

class ExecutionStatus(Enum):
    WAITING = "waiting"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class ExecutionContext:
    variables: Dict[str, Any]
    current_step: int
    total_steps: int
    execution_history: list
    error_count: int
    status: ExecutionStatus
    last_error: Optional[str] = None
    waiting_for_input: bool = False
    last_operation: Optional[Dict[str, Any]] = None

class ContextManager:
    def __init__(self):
        self.context = ExecutionContext(
            variables={},
            current_step=0,
            total_steps=0,
            execution_history=[],
            error_count=0,
            status=ExecutionStatus.WAITING
        )
        self._setup_save_dir()

    def _setup_save_dir(self):
        """创建保存目录"""
        self.save_dir = "execution_contexts"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def save_context(self, execution_id: str):
        """保存执行上下文到文件"""
        context_data = {
            "variables": self.context.variables,
            "current_step": self.context.current_step,
            "total_steps": self.context.total_steps,
            "execution_history": self.context.execution_history,
            "error_count": self.context.error_count,
            "last_error": self.context.last_error,
            "status": self.context.status.value,
            "waiting_for_input": self.context.waiting_for_input,
            "last_operation": self.context.last_operation
        }
        file_path = os.path.join(self.save_dir, f"{execution_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(context_data, f, ensure_ascii=False, indent=2)

    def load_context(self, execution_id: str) -> bool:
        """从文件加载执行上下文"""
        file_path = os.path.join(self.save_dir, f"{execution_id}.json")
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                context_data = json.load(f)
                context_data['status'] = ExecutionStatus(context_data['status'])
                self.context = ExecutionContext(**context_data)
            return True
        except Exception as e:
            self.context.last_error = str(e)
            return False

    def update_variable(self, name: str, value: Any):
        """更新变量值"""
        self.context.variables[name] = value

    def get_variable(self, name: str) -> Any:
        """获取变量值"""
        return self.context.variables.get(name)

    def record_step(self, step_type: str, details: Dict[str, Any]):
        """记录执行步骤"""
        self.context.execution_history.append({
            "step": self.context.current_step,
            "type": step_type,
            "details": details,
            "timestamp": str(datetime.datetime.now())
        })
        self.context.current_step += 1

    def record_error(self, error: str):
        """记录错误"""
        self.context.error_count += 1
        self.context.last_error = error
        self.context.status = ExecutionStatus.ERROR

    def reset(self):
        """重置上下文"""
        self.context = ExecutionContext(
            variables={},
            current_step=0,
            total_steps=0,
            execution_history=[],
            error_count=0,
            status=ExecutionStatus.WAITING
        )

    def set_waiting_for_input(self, waiting: bool, last_operation: Optional[Dict[str, Any]] = None):
        """设置等待用户输入状态"""
        self.context.waiting_for_input = waiting
        self.context.last_operation = last_operation
        self.context.status = ExecutionStatus.PAUSED if waiting else ExecutionStatus.RUNNING 