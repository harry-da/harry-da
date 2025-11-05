# Replicating Claude Code Skills with MCP Server

## Executive Summary

This document presents comprehensive research on replicating Claude Code Skills' progressive disclosure capabilities through a single HTTP MCP (Model Context Protocol) endpoint. The goal is to provision capabilities similar to Claude Code Skills to any coding agent, breaking free from vendor lock-in.

## Table of Contents

1. [Understanding Claude Code Skills](#understanding-claude-code-skills)
2. [Understanding MCP (Model Context Protocol)](#understanding-mcp)
3. [Progressive Disclosure Patterns](#progressive-disclosure-patterns)
4. [Architecture Design](#architecture-design)
5. [Implementation Strategy](#implementation-strategy)
6. [References and Resources](#references-and-resources)

---

## Understanding Claude Code Skills

### What are Claude Code Skills?

Claude Code Skills (officially called "Agent Skills") are specialized modules that capture and automate expertise or procedural knowledge. Instead of repeating detailed instructions in every prompt, capabilities are packaged in structured folders containing instruction files, scripts, and resources that Claude can dynamically load and use.

### Progressive Disclosure in Claude Skills

Progressive disclosure is the key design pattern that enables efficient skill usage:

#### Three-Phase Loading Process:

1. **Metadata Loading ("Table of Contents")**
   - Only skill name and description are loaded initially
   - Minimal context usage
   - Quick overview of all available skills
   - Enables rapid relevance assessment

2. **Selective Expansion ("Chapter")**
   - Full SKILL.md file loaded when skill matches user request
   - Detailed instructions and procedures become available
   - Domain-specific knowledge accessible on-demand

3. **Granular Detail ("Appendix")**
   - Sub-files and scripts loaded only when explicitly needed
   - Maximum context efficiency
   - Scalability for complex workflows

### Benefits of Progressive Disclosure

- **Consistency**: Ensures uniform outputs aligned with standards
- **Scalability**: Grows library without burdening AI performance
- **Custom Automation**: Enables domain-specific expertise
- **Context Efficiency**: Critical for LLM token management
- **Better Decision Making**: Reduces cognitive load on agents

---

## Understanding MCP (Model Context Protocol)

### What is MCP?

MCP is an open-source standard that connects AI applications to external systems like databases, files, APIs, and tools. It acts as a universal interface (like "USB-C for AI") allowing applications to access external data and trigger actions.

### MCP Server Components

An MCP server exposes capabilities through:

- **Tools**: Functions that agents can invoke
- **Resources**: Data sources agents can access
- **Prompts**: Pre-defined instruction templates
- **Toolsets**: Grouped collections of related tools

### Key MCP Features

1. **Standardized API**: Uniform way to expose capabilities
2. **Dynamic Discovery**: Agents can discover available tools
3. **Session Management**: Maintains context across requests
4. **Security**: OAuth 2.1 and API key support
5. **Transport Flexibility**: HTTP/SSE, HTTP streaming, stdio

---

## Progressive Disclosure Patterns

### Dynamic Toolset Management

Based on GitHub's MCP server implementation, progressive disclosure is achieved through:

#### Toolset Structure
```go
type Toolset struct {
    Name        string
    Description string
    Enabled     bool
    Tools       []Tool
}
```

#### Meta-Tools for Discovery

When dynamic toolsets are enabled:

1. **list_available_toolsets**
   - Returns available toolsets and activation status
   - Minimal context overhead
   - Enables intelligent selection

2. **get_toolset_tools**
   - Preview tools inside a toolset before activation
   - Informed decision making
   - No commitment to loading

3. **enable_toolset**
   - Activates specific toolset
   - Makes tools available to agent
   - Dynamic capability expansion

#### Workflow Example

```
Agent Start → Only Meta-Tools Available
     ↓
User Request: "Fix issue #123"
     ↓
Agent: list_available_toolsets()
     ↓
Agent: enable_toolset("issues")
     ↓
Issues Tools Now Available
     ↓
Agent: get_issue(123)
```

### Skills-Based Progressive Disclosure

Alternative pattern based on Claude's Skills:

#### Skill Directory Structure
```
skills/
├── skill-name/
│   ├── SKILL.md          # Metadata + Instructions
│   ├── scripts/          # Optional scripts
│   └── assets/           # Optional resources
```

#### SKILL.md Format
```yaml
---
name: skill-name
description: Clear description of when to use this skill
license: MIT
allowed-tools:
  - tool1
  - tool2
metadata:
  author: Author Name
  version: "1.0"
---

# Detailed Instructions

Full procedural knowledge and examples...
```

#### Discovery Process

1. Server loads only YAML frontmatter at startup
2. Agent receives skill catalog (names + descriptions)
3. When skill matches intent, full SKILL.md loaded
4. Referenced resources loaded only when needed

---

## Architecture Design

### Option 1: Toolset-Based Architecture

**Best for**: API-heavy integrations, GitHub operations, database queries

```
┌─────────────────────────────────────────┐
│         MCP HTTP Server                  │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │     Meta-Tools Layer               │ │
│  │  - list_toolsets()                 │ │
│  │  - get_toolset_tools()             │ │
│  │  - enable_toolset()                │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │     Toolset Registry               │ │
│  │  - Repository Operations           │ │
│  │  - Issue Management                │ │
│  │  - Pull Requests                   │ │
│  │  - Code Security                   │ │
│  │  - Notifications                   │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │     Session Manager                │ │
│  │  - Redis/In-Memory Store           │ │
│  │  - Enabled Toolsets Per Session    │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Pros**:
- Clean API organization
- Easy to scale horizontally
- Clear security boundaries per toolset
- Performance optimized for API operations

**Cons**:
- Less flexible for procedural knowledge
- Requires more code for each tool

### Option 2: Skills-Based Architecture

**Best for**: Procedural workflows, coding standards, complex multi-step tasks

```
┌─────────────────────────────────────────┐
│         MCP HTTP Server                  │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │     Skills Discovery Layer         │ │
│  │  - list_skills()                   │ │
│  │  - get_skill_metadata()            │ │
│  │  - load_skill()                    │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │     Skills Registry                │ │
│  │  - File System Scanner             │ │
│  │  - YAML Parser                     │ │
│  │  - Markdown Renderer               │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │     Context Manager                │ │
│  │  - Loaded Skills Per Session       │ │
│  │  - Token Budget Tracking           │ │
│  │  - Resource Cache                  │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Pros**:
- Easier to author new capabilities
- Better for complex workflows
- More maintainable procedural knowledge
- Non-programmers can contribute

**Cons**:
- Less structured than toolsets
- Parsing overhead for markdown
- May need interpreter for scripts

### Option 3: Hybrid Architecture (Recommended)

Combines both approaches for maximum flexibility:

```
┌─────────────────────────────────────────┐
│         MCP HTTP Server                  │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │     Unified Discovery Layer        │ │
│  │  - list_capabilities()             │ │
│  │  - enable_capability()             │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌──────────────┬─────────────────────┐ │
│  │  Toolsets    │  Skills             │ │
│  │  Registry    │  Registry           │ │
│  └──────────────┴─────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │     Progressive Disclosure Engine  │ │
│  │  - Lazy Loading                    │ │
│  │  - Context Budget Management       │ │
│  │  - Caching Strategy                │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Benefits**:
- Use toolsets for API-heavy operations
- Use skills for procedural knowledge
- Single consistent interface
- Maximum flexibility

---

## Implementation Strategy

### Phase 1: Foundation (Weeks 1-2)

**Goals**: Set up basic MCP server with HTTP endpoint

**Tasks**:
1. Set up TypeScript/Node.js project structure
2. Install MCP SDK and dependencies
3. Implement basic HTTP server with Express
4. Create core server initialization
5. Implement health check endpoint
6. Set up logging and error handling
7. Create basic test suite

**Deliverables**:
- Working HTTP server
- Basic MCP protocol support
- Health monitoring
- Documentation

### Phase 2: Progressive Disclosure Core (Weeks 3-4)

**Goals**: Implement progressive disclosure mechanism

**Tasks**:
1. Design toolset/skill registry interface
2. Implement meta-tools for discovery
3. Create session management system
4. Build progressive loading engine
5. Implement context budget tracking
6. Add caching layer
7. Create example toolsets

**Deliverables**:
- Working progressive disclosure
- Session management
- Example toolsets
- API documentation

### Phase 3: Skills System (Weeks 5-6)

**Goals**: Add Skills-based capabilities

**Tasks**:
1. Implement SKILL.md parser
2. Create skills directory scanner
3. Build skill loading mechanism
4. Add resource management
5. Implement allowed-tools security
6. Create skill templates
7. Write authoring guide

**Deliverables**:
- Skills loading system
- Security controls
- Example skills
- Authoring documentation

### Phase 4: Integration & Testing (Weeks 7-8)

**Goals**: Make it usable by any coding agent

**Tasks**:
1. Implement OAuth 2.1 authentication
2. Add API key management
3. Create client SDKs (Python, JavaScript)
4. Build integration examples
5. Performance testing and optimization
6. Security audit
7. Comprehensive documentation

**Deliverables**:
- Production-ready server
- Client libraries
- Integration examples
- Security report
- User guide

### Phase 5: Advanced Features (Weeks 9-10)

**Goals**: Production hardening and scaling

**Tasks**:
1. Horizontal scaling with Redis
2. Rate limiting and quotas
3. Monitoring and observability
4. Circuit breakers and resilience
5. Admin dashboard
6. Usage analytics
7. Migration tools

**Deliverables**:
- Scalable architecture
- Monitoring solution
- Admin tools
- Analytics dashboard

---

## Technical Specifications

### HTTP API Endpoints

#### Discovery Endpoints
```
GET  /api/v1/capabilities
GET  /api/v1/capabilities/:id
POST /api/v1/capabilities/:id/enable
POST /api/v1/capabilities/:id/disable
```

#### Tool Execution
```
POST /api/v1/tools/:name
GET  /api/v1/tools
```

#### Skill Management
```
GET  /api/v1/skills
GET  /api/v1/skills/:name
POST /api/v1/skills/:name/load
```

#### Session Management
```
POST /api/v1/sessions
GET  /api/v1/sessions/:id
DELETE /api/v1/sessions/:id
```

### Request/Response Format

#### List Capabilities Request
```http
GET /api/v1/capabilities
Authorization: Bearer <token>
```

#### List Capabilities Response
```json
{
  "capabilities": [
    {
      "id": "github-issues",
      "type": "toolset",
      "name": "GitHub Issues",
      "description": "Manage GitHub issues",
      "enabled": false,
      "tools_count": 8
    },
    {
      "id": "code-review",
      "type": "skill",
      "name": "Code Review",
      "description": "Perform comprehensive code reviews",
      "enabled": false,
      "complexity": "high"
    }
  ]
}
```

#### Enable Capability Request
```http
POST /api/v1/capabilities/github-issues/enable
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "sess_abc123"
}
```

#### Enable Capability Response
```json
{
  "capability_id": "github-issues",
  "enabled": true,
  "tools": [
    {
      "name": "list_issues",
      "description": "List issues in a repository",
      "parameters": {...}
    }
  ]
}
```

#### Tool Invocation Request
```http
POST /api/v1/tools/list_issues
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "sess_abc123",
  "parameters": {
    "owner": "harry-da",
    "repo": "harry-da",
    "state": "open"
  }
}
```

#### Tool Invocation Response
```json
{
  "success": true,
  "result": {
    "issues": [...]
  },
  "context_used": 150,
  "context_remaining": 7850
}
```

### Security Considerations

#### Authentication
- OAuth 2.1 for third-party integrations
- API keys for direct access
- JWT tokens for session management

#### Authorization
- Capability-based access control
- Tool-level permissions
- Rate limiting per client
- Audit logging

#### Data Protection
- Input validation and sanitization
- Output filtering
- Secret management
- Encryption at rest and in transit

### Performance Guidelines

#### Context Management
- Maximum 8000 token budget per session
- Lazy loading of all capabilities
- Aggressive caching of metadata
- LRU eviction for skills

#### Scalability
- Stateless API design
- Redis for distributed sessions
- Horizontal pod autoscaling
- CDN for static resources

#### Monitoring
- Request/response metrics
- Token usage tracking
- Error rate monitoring
- Performance profiling

---

## References and Resources

### Claude Code Skills
1. [eesel AI: Guide to Claude Skills](https://www.eesel.ai/blog/claude-skills)
2. [Anthropic Engineering: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
3. [GitHub: claude-skills - Comprehensive guide](https://github.com/pahar0/claude-skills)
4. [BDTechTalks: Inside Claude Skills](https://bdtechtalks.com/2025/10/20/anthropic-agent-skills/)
5. [MCPJam: Progressive disclosure might replace MCP](https://www.mcpjam.com/blog/claude-agent-skills)

### MCP Protocol
1. [Model Context Protocol Official Docs](https://modelcontextprotocol.io/docs/getting-started/intro)
2. [Microsoft .NET MCP Quickstart](https://learn.microsoft.com/en-us/dotnet/ai/quickstarts/build-mcp-server)
3. [FreeCodeCamp: Build Custom MCP Server with TypeScript](https://www.freecodecamp.org/news/how-to-build-a-custom-mcp-server-with-typescript-a-handbook-for-developers/)
4. [Simplescraper: Complete Guide to MCP](https://simplescraper.io/blog/how-to-mcp)
5. [TowardsDataScience: MCP Tutorial](https://towardsdatascience.com/model-context-protocol-mcp-tutorial-build-your-first-mcp-server-in-6-steps/)

### Progressive Disclosure in MCP
1. [GitHub: Progressive Disclosure in MCP Servers](https://github.com/orgs/ModelContextProtocol-Security/discussions/3)
2. [MCP Tutorials: From Concept to Production](https://modelcontextprotocol.info/docs/tutorials/)
3. [Google ADK: Model Context Protocol](https://google.github.io/adk-docs/mcp/)
4. [Azure: Build Agents using MCP](https://learn.microsoft.com/en-us/azure/developer/ai/intro-agents-mcp)

### Implementation Examples
1. [GitHub: example-mcp-server-streamable-http](https://github.com/yigitkonur/example-mcp-server-streamable-http)
2. [MCP Best Practices](https://modelcontextprotocol.info/docs/best-practices/)
3. [MCPcat: MCP Server Best Practices](https://mcpcat.io/blog/mcp-server-best-practices/)
4. [Block Engineering: MCP Server Design Playbook](https://engineering.block.xyz/blog/blocks-playbook-for-designing-mcp-servers)
5. [GitHub: modular-mcp-server](https://github.com/T-hash06/modular-mcp-server)
6. [skills-mcp: Bring Claude's Skills to any MCP agent](https://github.com/skills-mcp/skills-mcp)

### Additional Resources
1. [MCPcat: Building MCP Server in TypeScript](https://mcpcat.io/guides/building-mcp-server-typescript/)
2. [InfyWays: Build Your First MCP Server](https://www.infyways.com/build-your-first-mcp-server-with-typescript/)
3. [Collabnix: MCP Server Tutorial](https://collabnix.com/how-to-build-mcp-server-using-typescript-from-scratch-complete-tutorial/)

---

## Next Steps

1. Review this research document with stakeholders
2. Validate architecture decisions
3. Create detailed project plan with GitHub issues
4. Set up development environment
5. Begin Phase 1 implementation
6. Establish CI/CD pipeline
7. Create integration test suite

---

## Conclusion

Replicating Claude Code Skills' progressive disclosure through MCP is achievable and provides significant benefits:

1. **Vendor Independence**: Not locked into Claude
2. **Universal Compatibility**: Any MCP-compatible agent can use it
3. **Scalable Architecture**: Grows with your needs
4. **Standard Protocol**: Built on open standards
5. **Future Proof**: Extensible and maintainable

The hybrid architecture combining toolsets and skills provides the best balance of structure and flexibility, enabling both API-heavy operations and procedural knowledge delivery through a single HTTP endpoint.

By following the phased implementation plan, we can build a production-ready MCP server that brings Claude Code Skills-like capabilities to any coding agent, democratizing advanced agent capabilities across the AI ecosystem.
