'''
Author: Ender-Zhang 102596313+Ender-Zhang@users.noreply.github.com
Date: 2025-03-24 21:04:18
LastEditors: Ender-Zhang 102596313+Ender-Zhang@users.noreply.github.com
LastEditTime: 2025-03-24 22:28:40
FilePath: /operating_engine/operations.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from base_operation import BaseOperation
from typing import Dict, Any, Optional

class AppOperation(BaseOperation):
    def execute(self, request_dict: str, instruction: str) -> Dict[str, Any]:
        try:
            self.validate_params(['request_dict', 'instruction'], 
                               request_dict=request_dict, 
                               instruction=instruction)
            
            print(f"执行App操作: {instruction}")
            result = {
                "status": "success",
                "message": f"已执行: {instruction}"
            }
            
            return self.record_success(result, "app_operation")
        except Exception as e:
            return self.handle_error(e)

class OpenManus(BaseOperation):
    def execute(self, request_dict: str, save_pic: Optional[str] = None, 
                get_report: Optional[str] = None, pic: Optional[str] = None) -> Dict[str, Any]:
        try:
            self.validate_params(['request_dict'], request_dict=request_dict)
            
            if save_pic:
                print(f"保存图片: {save_pic}")
            if get_report:
                print(f"获取报告，使用图片: {pic}")
                
            result = {
                "status": "success",
                "message": "操作完成"
            }
            
            return self.record_success(result, "open_manus")
        except Exception as e:
            return self.handle_error(e)

class SummaryResult(BaseOperation):
    def execute(self, request_dict: str) -> Dict[str, Any]:
        try:
            self.validate_params(['request_dict'], request_dict=request_dict)
            
            print("生成总结报告")
            result = {
                "status": "success",
                "message": "总结报告已生成"
            }
            
            return self.record_success(result, "summary_result")
        except Exception as e:
            return self.handle_error(e)

class UserInput(BaseOperation):
    def execute(self, request_dict: str = None) -> Dict[str, Any]:
        try:
            # 用户输入操作会暂停执行，等待输入
            result = {
                "input": None,  # 初始值为None，等待用户输入
                "status": "waiting",
                "variable_name": request_dict  # 保存变量名，用于后续存储
            }
            return self.record_success(result, "user_input")
        except Exception as e:
            return self.handle_error(e)

    def handle_user_input(self, input_value: str, variable_name: str = None) -> Dict[str, Any]:
        """
        处理用户输入
        
        Args:
            input_value: 用户输入的值
            variable_name: 要保存的变量名
            
        Returns:
            处理结果
        """
        try:
            # 如果指定了变量名，将输入值保存到上下文中
            if variable_name:
                self.context.context.update_variable(variable_name, input_value)
            
            result = {
                "status": "success",
                "input": input_value,
                "variable_name": variable_name
            }
            return self.record_success(result, "user_input")
        except Exception as e:
            return self.handle_error(e)

class Response(BaseOperation):
    def execute(self, request_dict: str) -> Dict[str, Any]:
        try:
            self.validate_params(['request_dict'], request_dict=request_dict)
            
            # 从上下文中获取变量值
            result = self.context.context.get_variable(request_dict)
            print(f"响应结果: {result}")
            
            return self.record_success(result, "response")
        except Exception as e:
            return self.handle_error(e) 