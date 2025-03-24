from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from context import ContextManager

class BaseOperation(ABC):
    def __init__(self, context: ContextManager):
        self.context = context

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行操作"""
        pass

    def validate_params(self, required_params: list, **kwargs) -> bool:
        """验证参数"""
        for param in required_params:
            if param not in kwargs:
                raise ValueError(f"缺少必要参数: {param}")
        return True

    def handle_error(self, error: Exception):
        """处理错误"""
        self.context.record_error(str(error))
        return {
            "status": "error",
            "message": str(error)
        }

    def record_success(self, result: Dict[str, Any], operation_type: str):
        """记录成功执行"""
        self.context.record_step(operation_type, {
            "status": "success",
            "result": result
        })
        return result 