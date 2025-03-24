'''
AST解析器模块
该模块负责：
1. 将伪代码解析为抽象语法树（AST）
2. 支持多种操作类型的解析
3. 处理变量赋值和函数调用
4. 提供代码验证功能

Author: Ender-Zhang 102596313+Ender-Zhang@users.noreply.github.com
Date: 2025-03-24 21:04:43
LastEditors: Ender-Zhang 102596313+Ender-Zhang@users.noreply.github.com
LastEditTime: 2025-03-24 21:42:29
'''
import ast
from typing import List, Dict, Any, Optional
import re

class CodeParser:
    """
    代码解析器类
    负责将伪代码解析为操作列表
    
    主要功能：
    1. 解析Python风格的伪代码
    2. 识别各种操作类型
    3. 提取操作参数
    4. 生成标准化的操作列表
    """
    
    def __init__(self, code: str):
        """
        初始化代码解析器
        
        Args:
            code: 要解析的伪代码字符串
        """
        self.code = code
        # 定义支持的操作类型及其对应的正则表达式模式
        self.operation_patterns = {
            'user_input': r'^(\w+)\s*=\s*user_input\(\s*\)$',
            'app_operation': r'^(\w+)\s*=\s*AppOperation\(\s*(.*?)\s*\)$',
            'open_manus': r'^(\w+)\s*=\s*OpenManus\(\s*(.*?)\s*\)$',
            'summary_result': r'^(\w+)\s*=\s*SummaryResult\(\s*(.*?)\s*\)$',
            'response': r'^response\(\s*(.*?)\s*\)$'
        }
        
    def parse(self) -> List[Dict[str, Any]]:
        """
        解析代码并返回操作列表
        
        Returns:
            包含所有操作信息的列表，每个操作是一个字典
        """
        try:
            operations = []
            lines = self.code.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # 尝试匹配每种操作类型
                for op_type, pattern in self.operation_patterns.items():
                    match = re.match(pattern, line)
                    if match:
                        # 根据操作类型处理匹配结果
                        if op_type == 'user_input':
                            # 处理用户输入操作
                            target = match.group(1)
                            operations.append({
                                'type': op_type,
                                'target': target
                            })
                        elif op_type == 'response':
                            # 处理响应操作
                            args_str = match.group(1)
                            args = self._parse_args(args_str)
                            operations.append({
                                'type': op_type,
                                'args': args
                            })
                        else:
                            # 处理其他操作类型
                            target = match.group(1)
                            args_str = match.group(2)
                            args = self._parse_args(args_str)
                            operations.append({
                                'type': op_type,
                                'target': target,
                                'args': args
                            })
                        break
                        
            return operations
        except Exception as e:
            raise ValueError(f"代码解析错误: {str(e)}")
        
    def _parse_args(self, args_str: str) -> Dict[str, Any]:
        """
        解析操作参数
        
        Args:
            args_str: 参数字符串，格式如 "arg1='value1', arg2='value2'"
            
        Returns:
            解析后的参数字典
        """
        args = {}
        # 移除空白字符
        args_str = args_str.strip()
        if not args_str:
            return args
            
        # 分割参数对
        pairs = args_str.split(',')
        for i, pair in enumerate(pairs):
            pair = pair.strip()
            if '=' not in pair:
                # 如果是第一个参数且没有等号，将其作为request_dict参数
                if i == 0:
                    args['request_dict'] = pair
                continue
                
            # 解析参数名和值
            key, value = pair.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # 处理字符串值（移除引号）
            if value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            elif value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
                
            args[key] = value
            
        return args
        
    def validate(self) -> bool:
        """
        验证代码格式是否正确
        
        Returns:
            代码是否有效的布尔值
        """
        try:
            # 尝试解析代码
            ast.parse(self.code)
            return True
        except SyntaxError:
            return False
            
    def get_variables(self) -> List[str]:
        """
        获取代码中定义的所有变量名
        
        Returns:
            变量名列表
        """
        variables = []
        tree = ast.parse(self.code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append(target.id)
                        
        return variables 

    def validate_syntax(self) -> bool:
        """验证代码语法"""
        return self.validate()

    def validate_structure(self) -> bool:
        """验证代码结构"""
        # 检查必要的操作是否存在
        # 检查操作顺序是否正确
        pass 