'''
Author: Ender-Zhang 102596313+Ender-Zhang@users.noreply.github.com
Date: 2025-03-24 21:04:18
LastEditors: Ender-Zhang 102596313+Ender-Zhang@users.noreply.github.com
LastEditTime: 2025-03-24 21:53:17
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
    def execute(self) -> Dict[str, Any]:
        try:
            # 用户输入操作会暂停执行，等待输入
            result = {
                "input": None,  # 初始值为None，等待用户输入
                "status": "waiting"
            }
            return self.record_success(result, "user_input")
        except Exception as e:
            return self.handle_error(e)

class Response(BaseOperation):
    def execute(self, request_dict: str) -> Dict[str, Any]:
        try:
            self.validate_params(['request_dict'], request_dict=request_dict)
            
            result = self.context.get_variable(request_dict)
            print(f"响应结果: {result}")
            
            return self.record_success(result, "response")
        except Exception as e:
            return self.handle_error(e) 