'''
执行引擎主模块
该模块负责：
1. 解析和执行伪代码
2. 管理执行上下文
3. 处理用户输入
4. 提供REST API接口

Author: Ender-Zhang 102596313+Ender-Zhang@users.noreply.github.com
Date: 2025-03-24 21:04:43
LastEditors: Ender-Zhang 102596313+Ender-Zhang@users.noreply.github.com
LastEditTime: 2025-03-24 21:23:18
'''
from ast_parser import CodeParser
from operations import AppOperation, OpenManus, SummaryResult, UserInput, Response
from context import ContextManager, ExecutionStatus
from code_generator import CodeGenerator
import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

class EngineRequest(BaseModel):
    """
    执行引擎请求模型
    用于处理所有类型的请求，包括：
    - 新的执行请求（execution_id为空）
    - 用户输入请求（包含input_data）
    - 继续执行请求（只有execution_id）
    """
    execution_id: Optional[str] = None  # 执行ID，用于标识和跟踪执行过程
    input_data: Optional[Dict[str, Any]] = None  # 用户输入数据

class ExecutionEngine:
    """
    执行引擎核心类
    负责：
    1. 管理执行上下文
    2. 解析和执行伪代码
    3. 处理用户输入
    4. 维护代码缓存
    """
    def __init__(self):
        """
        初始化执行引擎
        设置上下文管理器和操作映射表
        """
        self.context_manager = ContextManager()  # 上下文管理器，用于管理执行状态
        # 操作类型到操作类的映射
        self.operation_map = {
            'user_input': UserInput,      # 用户输入操作
            'app_operation': AppOperation, # 应用操作（如打开页面）
            'open_manus': OpenManus,      # 打开菜单操作
            'summary_result': SummaryResult, # 生成总结结果
            'response': Response          # 响应操作
        }
        self.code_cache = {}  # 代码缓存，存储每个执行ID对应的代码

    def execute_code(self, execution_id: str = None) -> Dict[str, Any]:
        """
        执行代码的主要方法
        
        Args:
            execution_id: 执行ID，用于标识和跟踪执行过程
            
        Returns:
            包含执行状态和结果的字典
        """
        # 如果没有提供执行ID，生成新的UUID
        if execution_id is None:
            execution_id = str(uuid.uuid4())
            
        # 尝试加载已存在的上下文，如果不存在则创建新的
        if not self.context_manager.load_context(execution_id):
            self.context_manager.reset()
            # 生成并缓存代码
            code = CodeGenerator.generate_code()
            self.code_cache[execution_id] = code
            
        # 如果正在等待用户输入，返回当前状态
        if self.context_manager.context.waiting_for_input:
            return {
                "status": "paused",
                "execution_id": execution_id,
                "waiting_for_input": True,
                "last_operation": self.context_manager.context.last_operation,
                "isDone": False
            }
            
        # 如果已经完成，返回完成状态
        if self.context_manager.context.status == ExecutionStatus.COMPLETED:
            return {
                "status": "completed",
                "execution_id": execution_id,
                "total_steps": self.context_manager.context.total_steps,
                "completed_steps": self.context_manager.context.current_step,
                "error_count": self.context_manager.context.error_count,
                "execution_history": self.context_manager.context.execution_history,
                "isDone": True
            }
            
        # 获取缓存的代码
        code = self.code_cache.get(execution_id)
        if not code:
            raise ValueError("未找到缓存的代码")
            
        # 解析代码并获取操作列表
        parser = CodeParser(code)
        operations = parser.parse()
        self.context_manager.context.total_steps = len(operations)
        
        try:
            # 执行每个操作
            while self.context_manager.context.current_step < len(operations):
                op = operations[self.context_manager.context.current_step]
                operation_class = self.operation_map.get(op['type'])
                if not operation_class:
                    raise ValueError(f"未知的操作类型: {op['type']}")
                    
                # 创建并执行操作
                operation = operation_class(self.context_manager)
                
                # 准备操作参数
                args = {}
                if op.get('args'):
                    for arg_name, arg_value in op['args'].items():
                        # 如果参数值是变量名，从上下文中获取变量值
                        if isinstance(arg_value, str):
                            if arg_value in self.context_manager.context.variables:
                                args[arg_name] = self.context_manager.context.variables[arg_value]
                            else:
                                # 如果是字符串但不是变量名，直接使用
                                args[arg_name] = arg_value
                        else:
                            args[arg_name] = arg_value
                
                # 如果是AppOperation，确保request_dict参数存在
                if op['type'] == 'app_operation' and 'request_dict' not in args:
                    raise ValueError("AppOperation需要request_dict参数")
                
                result = operation.execute(**args)
                
                # 如果是用户输入操作，暂停执行
                if op['type'] == 'user_input':
                    self.context_manager.context.set_waiting_for_input(True, op)
                    self.context_manager.save_context(execution_id)
                    return {
                        "status": "paused",
                        "execution_id": execution_id,
                        "waiting_for_input": True,
                        "last_operation": op,
                        "isDone": False
                    }
                
                # 更新变量（如果有目标变量）
                if op.get('target'):
                    self.context_manager.context.update_variable(op['target'], result)
                    
                # 增加当前步骤
                self.context_manager.context.current_step += 1
                    
                # 保存上下文
                self.context_manager.save_context(execution_id)
                
            # 标记执行完成
            self.context_manager.context.mark_completed()
            self.context_manager.save_context(execution_id)
            
            return {
                "status": "success",
                "execution_id": execution_id,
                "total_steps": self.context_manager.context.total_steps,
                "completed_steps": self.context_manager.context.current_step,
                "error_count": self.context_manager.context.error_count,
                "execution_history": self.context_manager.context.execution_history,
                "isDone": True
            }
            
        except Exception as e:
            # 记录错误并返回错误状态
            self.context_manager.context.record_error(str(e))
            self.context_manager.save_context(execution_id)
            return {
                "status": "error",
                "execution_id": execution_id,
                "error": str(e),
                "isDone": False
            }

    def handle_user_input(self, execution_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理用户输入的方法
        
        Args:
            execution_id: 执行ID
            input_data: 用户输入数据
            
        Returns:
            继续执行的结果
        """
        try:
            # 验证执行上下文是否存在
            if not self.context_manager.load_context(execution_id):
                raise ValueError("未找到执行上下文")
                
            # 验证是否在等待用户输入状态
            if not self.context_manager.context.waiting_for_input:
                raise ValueError("当前不在等待用户输入状态")
                
            # 更新用户输入变量
            last_op = self.context_manager.context.last_operation
            if last_op and last_op.get('target'):
                # 确保输入数据包含必要的字段
                if 'input' not in input_data:
                    raise ValueError("输入数据必须包含 'input' 字段")
                self.context_manager.context.update_variable(last_op['target'], input_data)
                
            # 继续执行
            self.context_manager.context.set_waiting_for_input(False)
            # 增加当前步骤，因为用户输入操作已经完成
            self.context_manager.context.current_step += 1
            self.context_manager.save_context(execution_id)
            
            result = self.execute_code(execution_id)
            
            # 确保返回结果包含isDone标志
            if "isDone" not in result:
                result["isDone"] = result.get("status") == "completed" or result.get("status") == "success"
                
            return result
            
        except Exception as e:
            # 记录错误并返回错误状态
            self.context_manager.context.record_error(str(e))
            self.context_manager.save_context(execution_id)
            return {
                "status": "error",
                "execution_id": execution_id,
                "error": str(e),
                "isDone": False
            }

# 创建FastAPI应用
app = FastAPI(
    title="执行引擎API",
    description="用于执行自动化操作的API服务",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 创建执行引擎实例
engine = ExecutionEngine()

@app.get("/")
async def root():
    """
    根路径处理函数
    返回API基本信息
    """
    return {
        "name": "执行引擎API",
        "version": "1.0.0",
        "description": "用于执行自动化操作的API服务",
        "endpoints": {
            "engine": "/engine (POST) - 执行引擎主接口"
        }
    }

@app.post("/engine")
@app.post("/engine/")
async def engine_endpoint(request: EngineRequest):
    """
    统一的执行引擎接口
    处理所有类型的请求：
    1. 新的执行请求（execution_id为空）
    2. 用户输入请求（包含input_data）
    3. 继续执行请求（只有execution_id）
    
    Args:
        request: 包含执行ID和用户输入的请求体
        
    Returns:
        执行结果，包含状态、执行ID、步骤信息等
    """
    try:
        # 根据请求类型调用相应的方法
        if not request.execution_id:
            result = engine.execute_code()
        elif request.input_data:
            result = engine.handle_user_input(request.execution_id, request.input_data)
        else:
            result = engine.execute_code(request.execution_id)
            
        # 确保返回结果包含isDone标志
        if "isDone" not in result:
            result["isDone"] = result.get("status") == "completed" or result.get("status") == "success"
            
        return result
    except Exception as e:
        # 发生错误时返回错误信息
        return {
            "status": "error",
            "error": str(e),
            "isDone": False
        }

def main():
    """启动FastAPI服务器"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main() 