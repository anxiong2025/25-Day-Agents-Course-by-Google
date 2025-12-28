# Day 22: Security & Guardrails

> **"Prompt Engineering is not a Security Strategy. Asking an LLM nicely to 'please ignore PII' is not governance; it's wishful thinking."**

## Overview

Day 22 focuses on building robust security mechanisms for AI Agents. Instead of relying on prompt-based instructions for safety, we learn to implement proper guardrails using ADK Callbacks, Plugins, and Google Cloud's Model Armor.

## Key Concepts

### 1. ADK Callbacks
Callbacks are hook mechanisms in the Agent Development Kit that let you intercept and validate agent behavior at key points:

- `before_agent_callback` - Before agent execution
- `before_model_callback` - Before LLM call (input guardrails)
- `after_model_callback` - After LLM call (output guardrails)
- `before_tool_callback` - Before tool execution
- `after_tool_callback` - After tool execution

### 2. Input Guardrails
Protect against malicious or problematic inputs:
- **Prompt Injection Detection** - Block attempts to manipulate LLM instructions
- **PII Detection & Redaction** - Identify and mask sensitive personal data
- **Content Safety Classification** - Filter harmful content categories

### 3. Output Guardrails
Validate and filter LLM outputs:
- **PII Filtering** - Remove accidentally leaked personal information
- **Hallucination Detection** - Flag uncited claims
- **Content Safety Filtering** - Block harmful generated content

### 4. Tool Guardrails
Control what actions agents can perform:
- Tool whitelisting/blacklisting
- Parameter validation
- Rate limiting
- Permission checks

### 5. Model Armor
Google Cloud's enterprise-grade AI security service:
- Prompt injection and jailbreak detection
- Sensitive data protection (PII)
- Malicious URL detection
- Content safety filtering
- Model and cloud agnostic

## Files

- `security_guardrails.ipynb` - Interactive notebook with hands-on examples
- `README.md` - This overview document

## Learning Objectives

After completing this day, you will be able to:

1. Implement ADK Callbacks for security validation
2. Build input guardrails (injection detection, PII protection)
3. Build output guardrails (filtering, hallucination detection)
4. Configure tool usage policies
5. Understand Model Armor integration
6. Apply security best practices to AI Agents

## Security Design Principles

| Principle | Description |
|-----------|-------------|
| **Defense in Depth** | Multiple layers, don't rely on single mechanism |
| **Least Privilege** | Agents only access necessary resources |
| **Fail Secure** | Default to safe behavior (deny vs allow) |
| **Audit Everything** | Log all security-related events |
| **Assume Breach** | Assume attackers will bypass some defenses |

## References

- [ADK Callbacks - Official Docs](https://google.github.io/adk-docs/callbacks/)
- [ADK Callbacks Design Patterns](https://google.github.io/adk-docs/callbacks/design-patterns-and-best-practices/)
- [ADK Plugins Documentation](https://google.github.io/adk-docs/plugins/)
- [Model Armor Overview](https://cloud.google.com/security/products/model-armor)
- [Model Armor Documentation](https://docs.cloud.google.com/model-armor/overview)
- [ADK Safety Documentation](https://google.github.io/adk-docs/safety/)
- [Agent Builder - Agent Identity](https://docs.cloud.google.com/agent-builder/agent-engine/agent-identity)
- [A2A Protocol - Enterprise Ready](https://a2a-protocol.org/latest/topics/enterprise-ready/)

## Security Checklist

### Input Protection
- [ ] Prompt Injection detection
- [ ] PII detection & redaction
- [ ] Content safety classification
- [ ] Input length limits
- [ ] Malicious URL detection

### Output Protection
- [ ] PII filtering
- [ ] Sensitive info leak detection
- [ ] Hallucination/false info flagging
- [ ] Harmful content filtering

### Tool Calls
- [ ] Tool whitelist/blacklist
- [ ] Parameter validation
- [ ] Rate limiting
- [ ] Permission checks

### Operations
- [ ] Audit logging
- [ ] Monitoring & alerting
- [ ] Regular security audits
- [ ] Incident response plan
