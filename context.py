'''
上下文管理模块
该模块负责：
1. 管理执行上下文
2. 保存和加载执行状态
3. 处理变量存储
4. 记录执行历史

Author: Ender-Zhang 102596313+Ender-Zhang@users.noreply.github.com
Date: 2025-03-24 21:04:43
LastEditors: Ender-Zhang 102596313+Ender-Zhang@users.noreply.github.com
LastEditTime: 2025-03-24 21:23:18
'''
import json
import os
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid

class ExecutionStatus(Enum):
    """
    执行状态枚举
    """
    RUNNING = "running"       # 正在执行
    PAUSED = "paused"        # 暂停等待用户输入
    COMPLETED = "completed"  # 执行完成
    ERROR = "error"          # 执行出错

class Context:
    """
    执行上下文类
    用于存储和管理执行过程中的状态信息
    """
    def __init__(self):
        """
        初始化执行上下文
        """
        self.execution_id = str(uuid.uuid4())  # 执行ID
        self.variables: Dict[str, Any] = {}    # 变量存储
        self.current_step = 0                  # 当前执行步骤
        self.total_steps = 0                   # 总步骤数
        self.status = ExecutionStatus.RUNNING  # 执行状态
        self.error_count = 0                   # 错误计数
        self.execution_history: List[Dict[str, Any]] = []  # 执行历史
        self.waiting_for_input = False         # 是否等待用户输入
        self.last_operation: Optional[Dict[str, Any]] = None  # 最后一个操作
        self.is_done = False                   # 是否完成

    def update_variable(self, name: str, value: Any) -> None:
        """
        更新变量值
        
        Args:
            name: 变量名
            value: 变量值
        """
        self.variables[name] = value

    def get_variable(self, name: str) -> Any:
        """
        获取变量值
        
        Args:
            name: 变量名
            
        Returns:
            变量值
        """
        return self.variables.get(name)

    def record_error(self, error: str) -> None:
        """
        记录错误信息
        
        Args:
            error: 错误信息
        """
        self.error_count += 1
        self.status = ExecutionStatus.ERROR
        self.execution_history.append({
            "step": self.current_step,
            "type": "error",
            "message": error
        })

    def set_waiting_for_input(self, waiting: bool, operation: Optional[Dict[str, Any]] = None) -> None:
        """
        设置等待用户输入状态
        
        Args:
            waiting: 是否等待用户输入
            operation: 等待的操作信息
        """
        self.waiting_for_input = waiting
        if waiting:
            self.status = ExecutionStatus.PAUSED
            self.last_operation = operation
        else:
            self.status = ExecutionStatus.RUNNING
            self.last_operation = None

    def mark_completed(self) -> None:
        """
        标记执行完成
        """
        self.status = ExecutionStatus.COMPLETED
        self.is_done = True

    def record_step(self, operation_type: str, result: Dict[str, Any]) -> None:
        """
        记录执行步骤
        
        Args:
            operation_type: 操作类型
            result: 执行结果
        """
        self.execution_history.append({
            "step": self.current_step,
            "type": operation_type,
            "result": result
        })

    def to_dict(self) -> Dict[str, Any]:
        """
        将上下文转换为字典
        
        Returns:
            包含上下文信息的字典
        """
        return {
            "execution_id": self.execution_id,
            "variables": self.variables,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "status": self.status.value,
            "error_count": self.error_count,
            "execution_history": self.execution_history,
            "waiting_for_input": self.waiting_for_input,
            "last_operation": self.last_operation,
            "is_done": self.is_done
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Context':
        """
        从字典创建上下文
        
        Args:
            data: 包含上下文信息的字典
            
        Returns:
            新的上下文实例
        """
        context = cls()
        context.execution_id = data.get("execution_id", str(uuid.uuid4()))
        context.variables = data.get("variables", {})
        context.current_step = data.get("current_step", 0)
        context.total_steps = data.get("total_steps", 0)
        context.status = ExecutionStatus(data.get("status", "running"))
        context.error_count = data.get("error_count", 0)
        context.execution_history = data.get("execution_history", [])
        context.waiting_for_input = data.get("waiting_for_input", False)
        context.last_operation = data.get("last_operation")
        context.is_done = data.get("is_done", False)
        return context

class ContextManager:
    """
    上下文管理器类
    负责管理执行上下文的保存和加载
    """
    def __init__(self):
        """
        初始化上下文管理器
        """
        self.context = Context()
        self.contexts_dir = "execution_contexts"
        os.makedirs(self.contexts_dir, exist_ok=True)

    def reset(self) -> None:
        """
        重置上下文
        """
        self.context = Context()

    def save_context(self, execution_id: str) -> None:
        """
        保存上下文到文件
        
        Args:
            execution_id: 执行ID
        """
        file_path = os.path.join(self.contexts_dir, f"{execution_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.context.to_dict(), f, ensure_ascii=False, indent=2)

    def load_context(self, execution_id: str) -> bool:
        """
        从文件加载上下文
        
        Args:
            execution_id: 执行ID
            
        Returns:
            是否成功加载上下文
        """
        file_path = os.path.join(self.contexts_dir, f"{execution_id}.json")
        if not os.path.exists(file_path):
            return False
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.context = Context.from_dict(data)
                return True
        except Exception:
            return False 