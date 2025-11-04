# AgentBay Dify Plugin

[English](../README.md) | [日本語](README_ja_JP.md)

## 简介

**AgentBay** 是阿里云无影推出的云端沙箱服务,提供隔离的Linux、Windows、浏览器等多种云计算环境,让AI Agent能够安全地执行代码、操作文件、自动化浏览器等复杂任务。
关于AgentBay的详细信息和使用方法，请参考官方网站的信息：https://www.aliyun.com/product/agentbay

**本插件的价值:**

传统AI Agent受限于纯文本交互,无法执行实际的计算任务。本插件通过集成AgentBay,让Dify应用获得"真实行动能力":

- 🔧 **执行代码**: 在隔离环境中运行Python、Shell脚本等,处理数据分析、文件转换等任务
- 🌐 **浏览器自动化**: 自动访问网页、填写表单、抓取数据,完成Web端操作
- 📁 **文件处理**: 读写云端文件,处理文档、日志等资源
- 🖥️ **桌面自动化**: 操作Windows应用程序,实现RPA流程
- ☁️ **云端执行**: 所有操作在云端进行,安全隔离,无需本地环境

**典型应用场景:**
- 数据分析Agent: 运行Python脚本分析用户上传的数据
- 网页爬虫Agent: 自动访问网站提取信息
- 自动化测试Agent: 执行Web应用的自动化测试
- 文档处理Agent: 批量转换、处理文件格式
- RPA办公Agent: 自动化执行重复的桌面操作

## 功能特性

### 会话管理
- 创建多种类型云环境(Linux、Browser、Code、Windows、Mobile)
- 查看和管理所有活跃会话
- 安全删除会话和清理资源

### 命令与代码执行
- 在云环境中执行Shell命令
- 运行Python和其他编程语言代码
- 可配置执行超时时间

### 文件操作
- 读取、写入文件
- 列出目录内容

### 浏览器自动化
- 网页导航、元素交互(点击、输入、滚动)
- 页面截图、内容提取
- 元素分析、等待加载

### 桌面UI自动化
- 桌面截图
- 鼠标点击、键盘输入

## 快速开始

### 获取API密钥
访问 [AgentBay控制台](https://agentbay.console.aliyun.com/service-management) 获取您的API密钥。

### 配置插件
在Dify中安装插件后,配置API Key参数。

### 基础使用流程

**1. 创建会话**
```
工具: session_create
参数:
- image_id: linux_latest (可选,默认为linux_latest)
  可选值: browser_latest, code_latest, windows_latest, mobile_latest
```

**2. 执行操作**

执行命令:
```
工具: command_execute
参数:
- session_id: <会话ID>
- command: "ls -la"
- timeout_ms: 30000 (可选)
```

文件操作:
```
工具: file_operations
参数:
- session_id: <会话ID>
- action: read (或write、list)
- file_path: /path/to/file (read/write时必需)
```

浏览器自动化:
```
工具: browser_automation
参数:
- session_id: <会话ID>
- action: navigate (或click、type、screenshot等)
- url: https://example.com (navigate时必需)
```

**3. 清理资源**
```
工具: session_delete
参数:
- session_id: <会话ID>
- sync_context: false (可选)
```

## Demo 示例

我们提供了开箱即用的示例，展示了插件的各种功能。这些示例存放在 [demo 目录](https://github.com/5101good/agentbay-dify-plugin/tree/main/demo) 中。

您可以通过以下步骤快速导入这些示例到 Dify：
1. 从 [demo 目录](https://github.com/5101good/agentbay-dify-plugin/tree/main/demo) 下载示例文件（Dify DSL 格式）
2. 在 Dify 中进入"工作室"，点击"导入 DSL 文件"
3. 选择下载的示例文件进行导入
4. 在导入的工作流中配置 AgentBay API Key
5. 运行示例查看插件的工作效果

## 工具说明

### session_create
创建新的云环境会话。支持5种环境类型:`linux_latest`(默认)、`browser_latest`(浏览器)、`code_latest`(开发)、`windows_latest`(Windows)、`mobile_latest`(移动)。返回session_id用于后续操作。

### session_list
列出当前账户下所有由此插件创建的活跃会话,包括会话ID、环境类型等信息。

### session_delete
删除指定会话并释放云端资源。建议操作完成后及时清理。

### command_execute
在会话中执行Shell命令,支持自定义工作目录和超时时间。适用于Linux/Windows环境的命令行操作。

### code_execute
在会话中运行代码,支持Python等多种编程语言。可指定工作目录,适合执行数据处理、自动化脚本等任务。

### file_operations
统一的文件操作工具,通过`action`参数指定操作类型:
- **read**: 读取文件内容
- **write**: 写入文件(自动创建不存在的文件)
- **list**: 列出目录内容

### browser_automation
功能完整的浏览器自动化工具,必须使用`browser_latest`环境。通过`action`参数支持多种操作:
- **navigate**: 访问网页
- **click/type**: 与页面元素交互(使用CSS选择器定位)
- **scroll**: 页面滚动
- **screenshot**: 截取页面截图(支持全页或可视区域)
- **get_content**: 获取页面HTML内容
- **analyze_elements**: 分析页面结构,帮助找到正确的选择器
- **wait_element/wait**: 等待元素或延时

### ui_operations
桌面UI自动化工具,适用于Windows、浏览器等图形环境。通过`action`参数支持:
- **screenshot**: 截取桌面截图
- **click**: 在指定坐标点击
- **type**: 输入文本
- **key**: 按下指定按键(如Enter、Tab等)

## 使用场景

**Web自动化测试**
1. 创建browser_latest会话
2. 使用browser_automation导航并交互
3. 截图验证结果
4. 删除会话

**数据处理**
1. 创建code_latest会话
2. 使用file_operations上传数据文件
3. 使用code_execute执行分析脚本
4. 使用file_operations下载结果
5. 删除会话

**系统运维**
1. 创建linux_latest会话
2. 使用command_execute执行检查命令
3. 使用file_operations读取日志
4. 删除会话

## 相关链接

- [AgentBay控制台](https://agentbay.console.aliyun.com)
- [AgentBay SDK](https://github.com/aliyun/wuying-agentbay-sdk)

## 联系方式

- GitHub Issues
- Email: 5101good@gmail.com

## 免责声明
本插件仅作为技术工具提供，使用时请注意：

1. **合法使用**: 确保所有操作符合法律法规，不得用于非法目的
2. **数据责任**: 用户对处理的数据负责，建议避免处理敏感信息
3. **服务依赖**: 需遵守阿里云无影AgentBay服务条款
4. **风险自担**: 使用存在数据丢失、服务中断等风险，用户自行承担
5. **责任限制**: 开发者不对使用导致的任何损失承担责任

使用本插件即表示同意上述条款。
