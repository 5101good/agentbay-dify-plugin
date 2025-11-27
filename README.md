# AgentBay Dify Plugin

[中文文档](readme/README_zh_Hans.md) | [日本語](readme/README_ja_JP.md)

## Introduction

**AgentBay** is a cloud sandbox service from Alibaba Cloud WuYing, providing isolated computing environments (Linux, Windows, Browser, etc.) that enable AI Agents to safely execute code, manipulate files, automate browsers, and perform complex tasks.
For detailed information and usage instructions about AgentBay, please refer to the official website: https://www.aliyun.com/product/agentbay

**Why This Plugin:**

Traditional AI Agents are limited to text-based interactions and cannot execute actual computational tasks. This plugin integrates AgentBay to give your Dify applications "real action capabilities":

- 🔧 **Code Execution**: Run Python, Shell scripts in isolated environments for data analysis, file conversion, etc.
- 🌐 **Browser Automation**: Automate web browsing, form filling, data scraping, and web operations
- 📁 **File Operations**: Read/write cloud files, process documents and logs
- 🖥️ **Desktop Automation**: Control Windows applications for RPA workflows
- ☁️ **Cloud-Based**: All operations run in the cloud with security isolation, no local environment needed

**Typical Use Cases:**
- Data Analysis Agent: Run Python scripts to analyze user-uploaded data
- Web Scraping Agent: Automatically visit websites to extract information
- Automated Testing Agent: Execute web application automated tests
- Document Processing Agent: Batch convert and process file formats
- RPA Office Agent: Automate repetitive desktop operations

## Features

### Session Management
- Create various cloud environments (Linux, Browser, Code, Windows, Mobile)
- View and manage all active sessions
- Safely delete sessions and clean up resources

### Command & Code Execution
- Execute Shell commands in cloud environments
- Run Python and other programming languages
- Configurable execution timeout

### File Operations
- Read and write files
- List directory contents

### Browser Automation
- Web navigation, element interaction (click, type, scroll)
- Page screenshots, content extraction
- Element analysis, wait for loading

### Desktop UI Automation
- Desktop screenshots
- Mouse clicks, keyboard input

## Quick Start

### Get API Key
Visit [AgentBay Console](https://agentbay.console.aliyun.com/service-management) to get your API key.

### Configure Plugin
After installing the plugin in Dify, configure the API Key parameter.

### Basic Usage

**1. Create Session**
```
Tool: session_create
Parameters:
- image_id: linux_latest (optional, default is linux_latest)
  Options: browser_latest, code_latest, windows_latest, mobile_latest
```

**2. Perform Operations**

Execute commands:
```
Tool: command_execute
Parameters:
- session_id: <session ID>
- command: "ls -la"
- timeout_ms: 30000 (optional)
```

File operations:
```
Tool: file_operations
Parameters:
- session_id: <session ID>
- action: read (or write, list)
- file_path: /path/to/file (required for read/write)
```

Browser automation:
```
Tool: browser_automation
Parameters:
- session_id: <session ID>
- action: navigate (or click, type, screenshot, etc.)
- url: https://example.com (required for navigate)
```

**3. Clean Up Resources**
```
Tool: session_delete
Parameters:
- session_id: <session ID>
- sync_context: false (optional)
```

## Demo Examples

We provide ready-to-use demo examples that showcase the plugin's capabilities. These examples are available in the [demo directory](https://github.com/5101good/agentbay-dify-plugin/tree/main/demo).

> **Note**: These demos are simple examples for reference and educational purposes only.

You can quickly get started by importing these examples into Dify:
1. Download the demo file (in Dify DSL format) from the [demo directory](https://github.com/5101good/agentbay-dify-plugin/tree/main/demo)
2. In Dify, go to "Studio" and click "Import DSL File"
3. Select the downloaded demo file to import
4. Configure the AgentBay API Key in the imported workflow
5. Run the demo to see how the plugin works

## Tools Reference

### session_create
Create a new cloud environment session. Supports 5 environment types: `linux_latest` (default), `browser_latest` (browser), `code_latest` (development), `windows_latest` (Windows), `mobile_latest` (mobile). Returns session_id for subsequent operations.

### session_list
List all active sessions created by this plugin under the current account, including session ID, environment type, etc.

### session_delete
Delete specified session and release cloud resources. Recommended to clean up promptly after operations.

### command_execute
Execute Shell commands in a session with support for custom working directory and timeout. Suitable for command-line operations in Linux/Windows environments.

### code_execute
Run code in a session, supporting Python and other programming languages. Can specify working directory, suitable for data processing, automation scripts, etc.

### file_operations
Unified file operation tool, specify operation type via `action` parameter:
- **read**: Read file content
- **write**: Write to file (automatically creates non-existent files)
- **list**: List directory contents

### browser_automation
Full-featured browser automation tool, requires `browser_latest` environment. Supports multiple operations via `action` parameter:
- **navigate**: Visit web pages
- **click/type**: Interact with page elements (locate using CSS selectors)
- **scroll**: Page scrolling
- **screenshot**: Capture page screenshots (supports full page or viewport)
- **get_content**: Get page HTML content
- **analyze_elements**: Analyze page structure to help find correct selectors
- **wait_element/wait**: Wait for elements or delays

### ui_operations
Desktop UI automation tool, suitable for Windows, browser and other graphical environments. Supports via `action` parameter:
- **screenshot**: Capture desktop screenshots
- **click**: Click at specified coordinates
- **type**: Type text
- **key**: Press specified keys (e.g., Enter, Tab, etc.)

## Use Cases

**Web Automation Testing**
1. Create browser_latest session
2. Use browser_automation to navigate and interact
3. Screenshot to verify results
4. Delete session

**Data Processing**
1. Create code_latest session
2. Use file_operations to upload data files
3. Use code_execute to run analysis scripts
4. Use file_operations to download results
5. Delete session

**System Operations**
1. Create linux_latest session
2. Use command_execute to run check commands
3. Use file_operations to read logs
4. Delete session

## Known Issues

**⚠️ Cannot Use on Official Dify Cloud**

Due to network restrictions, the AgentBay service cannot be accessed from the official Dify cloud platform (cloud.dify.ai), which will cause plugin initialization to fail. 

**Solution**: Please use this plugin in a self-hosted Dify instance.

## Links

- [AgentBay Console](https://agentbay.console.aliyun.com)
- [AgentBay SDK](https://github.com/aliyun/wuying-agentbay-sdk)

## Contact

- GitHub Issues
- Email: 5101good@gmail.com

## Disclaimer
This plugin is provided as a technical tool. Please note the following when using:

1. **Legal Use**: Ensure all operations comply with laws and regulations, and do not use for illegal purposes
2. **Data Responsibility**: Users are responsible for the data they process, and it is recommended to avoid processing sensitive information
3. **Service Dependency**: Must comply with Alibaba Cloud WuYing AgentBay service terms
4. **Risk Assumption**: Usage involves risks such as data loss and service interruption, which users assume at their own risk
5. **Liability Limitation**: Developers are not responsible for any losses caused by usage

Using this plugin indicates agreement to the above terms.
