# Privacy Policy

**Last Updated: October 29, 2025**

## Overview

The WuYing AgentBay Plugin (hereinafter referred to as "the Plugin") is used to integrate Alibaba Cloud WuYing AgentBay's cloud sandbox capabilities into the Dify platform. The Plugin acts as a middleware layer, forwarding user operation requests to the Alibaba Cloud AgentBay service.

## Information We Collect

### Configuration Information
- **AgentBay API Key**: Used for authentication with the Alibaba Cloud WuYing AgentBay service

### Operation Data
The following data is passed to the AgentBay service for processing:
- Session creation requests
- Commands and code content to be executed
- File operation requests
- Browser and UI automation instructions

### Technical Information
- Session IDs and status
- Operation execution results
- Error logs

**We do not collect**: Personal identity information, location information, device fingerprints, or any other information unrelated to the Plugin's functionality.

## Data Storage and Security

- **API Key**: Encrypted and stored in the Dify platform
- **Session Data**: Temporarily stored in runtime memory, not persisted
- **Cloud Environment Data**: Stored in Alibaba Cloud AgentBay sandbox environment, immediately cleaned up after session deletion
- **Transmission Security**: All data is transmitted through HTTPS encrypted channels

## Third-Party Services

The Plugin sends operation requests to the following services:
- **Alibaba Cloud WuYing AgentBay**: Processes all cloud environment operations. Please refer to Alibaba Cloud or AgentBay product privacy policies for detailed privacy terms
- **Dify Platform**: Plugin runtime platform

## Your Rights

- **Access**: View API key configuration at any time
- **Delete**: Delete API key configuration, delete session data, uninstall the Plugin
- **Control**: Full control over when to create/delete sessions and execute operations

## Usage Recommendations

- Keep your API key secure
- Delete sessions promptly when no longer needed
- Avoid processing highly sensitive personal information
- Assess data processing risks

## Disclaimer

1. The Plugin is provided as a technical tool, and the developer makes no guarantees regarding usage results
2. Data security in cloud environments is the responsibility of Alibaba Cloud AgentBay service
3. Users should assess risks and be responsible for the consequences of usage

## Contact

For questions, please contact:
- GitHub Issues: https://github.com/5101good/agentbay-dify-plugin/issues
- Email: 5101good@gmail.com

---

**By using this Plugin, you agree to this Privacy Policy.**