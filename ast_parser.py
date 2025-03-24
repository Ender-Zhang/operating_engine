'''
代码解析器模块
该模块负责：
1. 将伪代码解析为操作列表
2. 支持多种操作类型的解析
3. 处理变量赋值和函数调用
4. 提供代码验证功能

Author: Ender-Zhang 102596313+Ender-Zhang@users.noreply.github.com
Date: 2025-03-24 21:04:43
LastEditors: Ender-Zhang 102596313+Ender-Zhang@users.noreply.github.com
LastEditTime: 2025-03-24 22:42:36
'''
from typing import List, Dict, Any, Optional
import re
import ast

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
        self.operations = []  # 保存解析后的操作列表
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
            # 首先使用正则表达式快速匹配操作
            self.operations = self._parse_with_regex()
            
            # 然后使用AST分析代码结构和依赖关系
            ast_tree = ast.parse(self.code)
            self._analyze_with_ast(ast_tree, self.operations)
            
            return self.operations
        except Exception as e:
            raise ValueError(f"代码解析错误: {str(e)}")
            
    def get_operations(self) -> List[Dict[str, Any]]:
        """
        获取解析后的操作列表
        
        Returns:
            包含所有操作信息的列表
        """
        return self.operations
        
    def get_operation_by_line(self, line_number: int) -> Optional[Dict[str, Any]]:
        """
        根据行号获取操作
        
        Args:
            line_number: 行号
            
        Returns:
            对应行号的操作信息，如果不存在则返回None
        """
        for op in self.operations:
            if op.get('line_number') == line_number:
                return op
        return None
        
    def get_operation_by_type(self, op_type: str) -> List[Dict[str, Any]]:
        """
        根据操作类型获取操作列表
        
        Args:
            op_type: 操作类型
            
        Returns:
            指定类型的所有操作列表
        """
        return [op for op in self.operations if op.get('type') == op_type]
        
    def _parse_with_regex(self) -> List[Dict[str, Any]]:
        """使用正则表达式解析基本操作"""
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
                        target = match.group(1)
                        operations.append({
                            'type': op_type,
                            'target': target,
                            'line_number': len(operations) + 1
                        })
                    elif op_type == 'response':
                        args_str = match.group(1)
                        args = self._parse_args(args_str)
                        operations.append({
                            'type': op_type,
                            'args': args,
                            'line_number': len(operations) + 1
                        })
                    else:
                        target = match.group(1)
                        args_str = match.group(2)
                        args = self._parse_args(args_str)
                        operations.append({
                            'type': op_type,
                            'target': target,
                            'args': args,
                            'line_number': len(operations) + 1
                        })
                    break
                    
        return operations
        
    def _analyze_with_ast(self, tree: ast.AST, operations: List[Dict[str, Any]]) -> None:
        """使用AST分析代码结构和依赖关系"""
        # 收集所有变量定义
        variable_defs = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variable_defs[target.id] = node
                        
        # 分析每个操作的依赖关系
        for op in operations:
            if 'target' in op:
                # 检查变量是否被定义
                if op['target'] not in variable_defs:
                    op['undefined_variable'] = True
                    
            # 检查参数中的变量引用
            if 'args' in op and 'request_dict' in op['args']:
                var_name = op['args']['request_dict']
                if var_name not in variable_defs:
                    op['undefined_param'] = True
                    
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
            # 使用AST验证基本语法
            ast.parse(self.code)
            
            # 使用正则验证操作格式
            lines = self.code.split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                matched = False
                for pattern in self.operation_patterns.values():
                    if re.match(pattern, line):
                        matched = True
                        break
                        
                if not matched:
                    return False
                    
            return True
        except Exception:
            return False
            
    def get_variables(self) -> List[str]:
        """
        获取代码中定义的所有变量名
        
        Returns:
            变量名列表
        """
        variables = []
        tree = ast.parse(self.code)
        
        # 使用AST收集变量定义
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
        try:
            # 解析代码获取操作列表
            operations = self.parse()
            
            # 检查必要的操作是否存在
            has_user_input = any(op['type'] == 'user_input' for op in operations)
            has_response = any(op['type'] == 'response' for op in operations)
            
            if not has_user_input or not has_response:
                return False
                
            # 检查操作顺序是否正确
            for i, op in enumerate(operations):
                # 检查是否有未定义的变量
                if op.get('undefined_variable') or op.get('undefined_param'):
                    return False
                    
                # 检查操作顺序
                if i > 0 and op['type'] == 'user_input' and operations[i-1]['type'] == 'response':
                    return False
                    
            return True
        except Exception:
            return False 