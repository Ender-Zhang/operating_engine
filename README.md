# 执行引擎 (Operating Engine)

一个用于执行自动化操作的执行引擎，支持伪代码解析和执行，并提供REST API接口。

## 功能特点

- 伪代码解析和执行
- 支持多种操作类型（用户输入、应用操作、菜单操作等）
- 执行上下文管理
- 用户输入处理
- RESTful API接口
- 错误处理和状态跟踪

## 系统架构

系统由以下主要组件构成：

1. **执行引擎 (Engine)**
   - 负责解析和执行伪代码
   - 管理执行上下文
   - 处理用户输入
   - 提供REST API接口

2. **代码生成器 (CodeGenerator)**
   - 生成示例伪代码
   - 支持不同类型的代码生成

3. **AST解析器 (AST Parser)**
   - 将伪代码解析为抽象语法树
   - 支持多种操作类型的解析

4. **上下文管理器 (Context Manager)**
   - 管理执行状态
   - 保存和加载执行上下文
   - 处理变量存储

5. **操作类 (Operations)**
   - UserInput: 处理用户输入
   - AppOperation: 执行应用操作
   - OpenManus: 处理菜单操作
   - SummaryResult: 生成总结结果
   - Response: 处理响应

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/operating_engine.git
cd operating_engine
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 启动服务

```bash
python engine.py
```

服务将在 `http://localhost:8000` 启动。

### API使用

#### 访问根路径，查看API信息

```bash
curl http://localhost:8000/
```

响应示例：
```json
{
    "name": "执行引擎API",
    "version": "1.0.0",
    "description": "用于执行自动化操作的API服务",
    "endpoints": {
        "engine": "/engine (POST) - 执行引擎主接口"
    }
}
```

#### 1. 开始新的执行

```bash
curl -X POST http://localhost:8000/engine \
  -H "Content-Type: application/json" \
  -d '{}'
```

响应示例：
```json
{
  "status": "paused",
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "waiting_for_input": true,
  "last_operation": {
    "type": "user_input",
    "target": "request_dict"
  }
}
```

#### 2. 提供用户输入

```bash
curl -X POST http://localhost:8000/engine \
  -H "Content-Type: application/json" \
  -d '{
    "execution_id": "550e8400-e29b-41d4-a716-446655440000",
    "input_data": {
      "input": "用户输入内容"
    }
  }'
```

#### 3. 继续执行

```bash
curl -X POST http://localhost:8000/engine \
  -H "Content-Type: application/json" \
  -d '{
    "execution_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### 伪代码示例

```python
# 获取用户输入
request_dict = user_input()

# 执行应用操作
modifid_request_dict = AppOperation(request_dict, instruction='帮我到京东订单页面')
response(modifid_request_dict)

# 获取用户输入
request_dict = user_input()

# 保存截图
save_pic = OpenManus(request_dict, save_pic='save_pic')

# 执行应用操作
modifid_request_dict = AppOperation(request_dict, instruction='帮我到淘宝订单页面')
response(modifid_request_dict)

# 获取用户输入
request_dict = user_input()

# 保存截图
save_pic = OpenManus(request_dict, save_pic='save_pic')

# 执行应用操作
modifid_request_dict = AppOperation(request_dict, instruction='帮我到美团订单页面')
response(modifid_request_dict)

# 获取用户输入
request_dict = user_input()

# 保存截图
save_pic = OpenManus(request_dict, save_pic='save_pic')

# 生成报告
save_pic = OpenManus(request_dict, get_report='get_report', pic='save_pic')

# 生成总结
modifid_request_dict = SummaryResult(request_dict)
response(modifid_request_dict)
```

## 开发指南

### 添加新的操作类型

1. 在 `operations.py` 中创建新的操作类
2. 在 `ExecutionEngine` 的 `operation_map` 中注册新操作
3. 在 `CodeGenerator` 中添加相应的代码生成方法

### 修改伪代码格式

1. 修改 `code_generator.py` 中的代码生成方法
2. 确保 `ast_parser.py` 支持新的代码格式

## 错误处理

系统提供以下错误处理机制：

1. 执行错误：记录错误信息并返回错误状态
2. 用户输入验证：确保输入数据格式正确
3. 上下文验证：确保执行上下文存在且状态正确

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 作者

Ender-Zhang (102596313+Ender-Zhang@users.noreply.github.com) 