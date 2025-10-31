# MCP Progressive Disclosure Server - Architecture

## System Overview

This document provides detailed architecture for an MCP (Model Context Protocol) server that implements progressive disclosure patterns similar to Claude Code Skills, enabling any coding agent to dynamically discover and use capabilities.

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Client Layer                               │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐    │
│  │   AI Agent    │  │   AI Agent    │  │    AI Agent      │    │
│  │   (Claude)    │  │   (GPT-4)     │  │   (Custom LLM)   │    │
│  └───────┬───────┘  └───────┬───────┘  └────────┬─────────┘    │
└──────────┼──────────────────┼───────────────────┼───────────────┘
           │                  │                   │
           └──────────────────┼───────────────────┘
                              │
                    ┌─────────▼────────┐
                    │   Load Balancer  │
                    └─────────┬────────┘
                              │
           ┌──────────────────┼──────────────────┐
           │                  │                  │
     ┌─────▼─────┐     ┌─────▼─────┐     ┌─────▼─────┐
     │  MCP      │     │  MCP      │     │  MCP      │
     │  Server   │     │  Server   │     │  Server   │
     │  Instance │     │  Instance │     │  Instance │
     └─────┬─────┘     └─────┬─────┘     └─────┬─────┘
           │                  │                  │
           └──────────────────┼──────────────────┘
                              │
                    ┌─────────▼────────┐
                    │  Shared Services  │
                    │  - Redis Cache    │
                    │  - PostgreSQL     │
                    │  - File Storage   │
                    └──────────────────┘
```

## Core Components

### 1. API Gateway Layer

**Responsibilities**:
- Request routing
- Authentication/Authorization
- Rate limiting
- Request/response validation
- Logging and metrics

**Technologies**:
- Express.js / Fastify
- JWT for authentication
- express-rate-limit
- express-validator

**Endpoints**:
```typescript
// Discovery
GET    /api/v1/capabilities
GET    /api/v1/capabilities/:id
POST   /api/v1/capabilities/:id/enable
POST   /api/v1/capabilities/:id/disable

// Tool Execution
POST   /api/v1/tools/:name
GET    /api/v1/tools

// Skill Management
GET    /api/v1/skills
GET    /api/v1/skills/:name
POST   /api/v1/skills/:name/load

// Session Management
POST   /api/v1/sessions
GET    /api/v1/sessions/:id
DELETE /api/v1/sessions/:id
PUT    /api/v1/sessions/:id

// Health & Metrics
GET    /health
GET    /metrics
```

### 2. Progressive Disclosure Engine

**Core Responsibility**: Manage what capabilities are exposed and when

#### Components:

##### 2.1 Capability Registry
```typescript
interface Capability {
  id: string;
  type: 'toolset' | 'skill';
  name: string;
  description: string;
  metadata: {
    complexity: 'low' | 'medium' | 'high';
    tokenCost: number;
    category: string;
    tags: string[];
  };
  loader: () => Promise<LoadedCapability>;
}

class CapabilityRegistry {
  private capabilities: Map<string, Capability>;
  
  registerCapability(capability: Capability): void;
  listCapabilities(filter?: CapabilityFilter): Capability[];
  getCapability(id: string): Capability | null;
  loadCapability(id: string): Promise<LoadedCapability>;
}
```

##### 2.2 Context Budget Manager
```typescript
interface ContextBudget {
  total: number;          // e.g., 8000 tokens
  used: number;
  reserved: number;
  available: number;
}

class ContextBudgetManager {
  private budgets: Map<string, ContextBudget>;
  
  initializeBudget(sessionId: string, total: number): void;
  allocate(sessionId: string, amount: number): boolean;
  release(sessionId: string, amount: number): void;
  getRemaining(sessionId: string): number;
  canLoad(sessionId: string, capability: Capability): boolean;
}
```

##### 2.3 Lazy Loading Engine
```typescript
class LazyLoadingEngine {
  private cache: LRUCache<string, LoadedCapability>;
  
  async load(
    capability: Capability,
    sessionId: string,
    contextBudget: ContextBudgetManager
  ): Promise<LoadedCapability>;
  
  preload(capabilityIds: string[]): Promise<void>;
  unload(capabilityId: string, sessionId: string): void;
}
```

### 3. Toolset Manager

**Handles API-based capabilities organized into logical groups**

#### Toolset Structure:
```typescript
interface Toolset {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  tools: Tool[];
  dependencies?: string[];
}

interface Tool {
  name: string;
  description: string;
  parameters: JSONSchema;
  handler: ToolHandler;
  examples?: ToolExample[];
}

type ToolHandler = (
  params: unknown,
  context: ExecutionContext
) => Promise<ToolResult>;
```

#### Example Toolsets:

**Repository Operations**:
```typescript
const repositoryToolset: Toolset = {
  id: 'repository',
  name: 'Repository Operations',
  description: 'Manage GitHub repositories',
  enabled: false,
  tools: [
    {
      name: 'list_repositories',
      description: 'List repositories for a user or organization',
      parameters: {
        type: 'object',
        properties: {
          owner: { type: 'string' },
          type: { enum: ['all', 'public', 'private'] }
        }
      },
      handler: async (params) => {
        // Implementation
      }
    },
    {
      name: 'get_repository',
      description: 'Get details of a specific repository',
      parameters: {
        type: 'object',
        properties: {
          owner: { type: 'string' },
          repo: { type: 'string' }
        },
        required: ['owner', 'repo']
      },
      handler: async (params) => {
        // Implementation
      }
    }
  ]
};
```

**Issue Management**:
```typescript
const issueToolset: Toolset = {
  id: 'issues',
  name: 'Issue Management',
  description: 'Create, update, and manage GitHub issues',
  enabled: false,
  tools: [
    {
      name: 'list_issues',
      description: 'List issues in a repository',
      parameters: { /* ... */ },
      handler: async (params) => { /* ... */ }
    },
    {
      name: 'create_issue',
      description: 'Create a new issue',
      parameters: { /* ... */ },
      handler: async (params) => { /* ... */ }
    },
    {
      name: 'update_issue',
      description: 'Update an existing issue',
      parameters: { /* ... */ },
      handler: async (params) => { /* ... */ }
    }
  ]
};
```

### 4. Skills Manager

**Handles procedural knowledge and complex workflows**

#### Skill Structure:
```typescript
interface Skill {
  id: string;
  metadata: SkillMetadata;
  content?: SkillContent;  // Lazy loaded
  resources?: Map<string, Resource>;  // Lazy loaded
}

interface SkillMetadata {
  name: string;
  description: string;
  license?: string;
  allowedTools?: string[];
  author?: string;
  version?: string;
  complexity: 'low' | 'medium' | 'high';
  tokenEstimate: number;
}

interface SkillContent {
  instructions: string;  // Markdown content
  examples?: Example[];
  templates?: Template[];
}

interface Resource {
  path: string;
  type: 'script' | 'template' | 'data' | 'image';
  content: string | Buffer;
  metadata: {
    size: number;
    mimeType: string;
  };
}
```

#### Skill Loading Process:

```typescript
class SkillManager {
  private skillsDir: string;
  private loadedSkills: Map<string, Skill>;
  
  // Phase 1: Load only metadata
  async scanSkills(): Promise<SkillMetadata[]> {
    const skills: SkillMetadata[] = [];
    const dirs = await fs.readdir(this.skillsDir);
    
    for (const dir of dirs) {
      const skillPath = path.join(this.skillsDir, dir, 'SKILL.md');
      const content = await fs.readFile(skillPath, 'utf-8');
      const { data } = matter(content);  // Parse YAML frontmatter
      
      skills.push({
        name: data.name,
        description: data.description,
        license: data.license,
        allowedTools: data['allowed-tools'],
        ...data.metadata,
        complexity: this.estimateComplexity(content),
        tokenEstimate: this.estimateTokens(content)
      });
    }
    
    return skills;
  }
  
  // Phase 2: Load full content when needed
  async loadSkill(skillId: string): Promise<Skill> {
    if (this.loadedSkills.has(skillId)) {
      return this.loadedSkills.get(skillId)!;
    }
    
    const skillPath = path.join(this.skillsDir, skillId, 'SKILL.md');
    const content = await fs.readFile(skillPath, 'utf-8');
    const { data, content: markdown } = matter(content);
    
    const skill: Skill = {
      id: skillId,
      metadata: data as SkillMetadata,
      content: {
        instructions: markdown,
        examples: this.extractExamples(markdown),
        templates: this.extractTemplates(markdown)
      }
    };
    
    this.loadedSkills.set(skillId, skill);
    return skill;
  }
  
  // Phase 3: Load resources on demand
  async loadResource(
    skillId: string,
    resourcePath: string
  ): Promise<Resource> {
    const fullPath = path.join(
      this.skillsDir,
      skillId,
      resourcePath
    );
    
    const content = await fs.readFile(fullPath);
    const stats = await fs.stat(fullPath);
    
    return {
      path: resourcePath,
      type: this.detectResourceType(fullPath),
      content,
      metadata: {
        size: stats.size,
        mimeType: mime.lookup(fullPath) || 'application/octet-stream'
      }
    };
  }
}
```

### 5. Session Manager

**Manages agent sessions and state**

```typescript
interface Session {
  id: string;
  agentId: string;
  createdAt: Date;
  lastActivity: Date;
  state: {
    enabledCapabilities: string[];
    contextBudget: ContextBudget;
    preferences: SessionPreferences;
    cache: Map<string, unknown>;
  };
}

interface SessionPreferences {
  autoEnable?: boolean;
  tokenBudget?: number;
  cacheTTL?: number;
}

class SessionManager {
  private sessions: Map<string, Session>;
  private storage: RedisClient | InMemoryStore;
  
  async createSession(
    agentId: string,
    preferences?: SessionPreferences
  ): Promise<Session>;
  
  async getSession(sessionId: string): Promise<Session | null>;
  
  async updateSession(
    sessionId: string,
    updates: Partial<Session>
  ): Promise<void>;
  
  async deleteSession(sessionId: string): Promise<void>;
  
  async enableCapability(
    sessionId: string,
    capabilityId: string
  ): Promise<void>;
  
  async disableCapability(
    sessionId: string,
    capabilityId: string
  ): Promise<void>;
  
  async cleanupInactiveSessions(maxAge: number): Promise<void>;
}
```

### 6. Execution Engine

**Handles tool invocation and skill execution**

```typescript
interface ExecutionContext {
  sessionId: string;
  agentId: string;
  requestId: string;
  enabledCapabilities: Set<string>;
  metadata: {
    timestamp: Date;
    userAgent?: string;
  };
}

interface ExecutionResult {
  success: boolean;
  result?: unknown;
  error?: ErrorDetails;
  metrics: {
    executionTime: number;
    tokensUsed: number;
    apiCalls: number;
  };
}

class ExecutionEngine {
  async executeTool(
    toolName: string,
    parameters: unknown,
    context: ExecutionContext
  ): Promise<ExecutionResult> {
    const startTime = Date.now();
    
    try {
      // Validate tool is enabled
      const tool = await this.validateAndGetTool(toolName, context);
      
      // Validate parameters
      this.validateParameters(parameters, tool.parameters);
      
      // Execute tool
      const result = await tool.handler(parameters, context);
      
      // Track metrics
      const executionTime = Date.now() - startTime;
      await this.trackMetrics(toolName, executionTime, context);
      
      return {
        success: true,
        result,
        metrics: {
          executionTime,
          tokensUsed: this.estimateTokens(result),
          apiCalls: result.apiCalls || 0
        }
      };
    } catch (error) {
      return {
        success: false,
        error: this.formatError(error),
        metrics: {
          executionTime: Date.now() - startTime,
          tokensUsed: 0,
          apiCalls: 0
        }
      };
    }
  }
  
  async executeSkill(
    skillId: string,
    parameters: unknown,
    context: ExecutionContext
  ): Promise<ExecutionResult> {
    // Load skill if not already loaded
    const skill = await this.skillManager.loadSkill(skillId);
    
    // Apply skill instructions to agent context
    // This varies based on how the agent consumes skills
    
    return {
      success: true,
      result: {
        skillLoaded: true,
        instructions: skill.content?.instructions
      },
      metrics: {
        executionTime: 0,
        tokensUsed: skill.metadata.tokenEstimate,
        apiCalls: 0
      }
    };
  }
}
```

## Data Flow

### Capability Discovery Flow

```
Agent Request
     │
     ▼
[API Gateway]
     │
     ├─── Authentication
     ├─── Rate Limiting
     └─── Validation
     │
     ▼
[Capability Registry]
     │
     ├─── Load Metadata Only
     ├─── Filter by Session
     └─── Sort by Relevance
     │
     ▼
[Response Builder]
     │
     └─── Minimal JSON Response
     │
     ▼
Agent Receives List
```

### Capability Enablement Flow

```
Agent Enables Capability
     │
     ▼
[API Gateway]
     │
     └─── Validate Session
     │
     ▼
[Session Manager]
     │
     ├─── Check Context Budget
     └─── Validate Permissions
     │
     ▼
[Progressive Disclosure Engine]
     │
     ├─── Calculate Token Cost
     ├─── Load Full Capability
     └─── Update Session State
     │
     ▼
[Cache Layer]
     │
     └─── Cache for Session
     │
     ▼
Response with Tools/Skills
```

### Tool Execution Flow

```
Agent Calls Tool
     │
     ▼
[API Gateway]
     │
     ├─── Authentication
     └─── Validate Tool Access
     │
     ▼
[Execution Engine]
     │
     ├─── Validate Parameters
     ├─── Check Rate Limits
     └─── Execute Handler
     │
     ▼
[Tool Handler]
     │
     ├─── Business Logic
     ├─── External API Calls
     └─── Result Processing
     │
     ▼
[Response Builder]
     │
     ├─── Format Response
     ├─── Track Metrics
     └─── Update Context Budget
     │
     ▼
Agent Receives Result
```

## Storage Architecture

### Redis Cache Structure

```typescript
// Session data
sessions:{sessionId} -> Session
sessions:{sessionId}:capabilities -> Set<capabilityId>
sessions:{sessionId}:budget -> ContextBudget

// Capability cache
capabilities:{capabilityId}:metadata -> Metadata
capabilities:{capabilityId}:content -> LoadedCapability

// Rate limiting
ratelimit:{clientId}:{endpoint} -> Counter

// Metrics
metrics:{date}:{toolName} -> Stats
```

### PostgreSQL Schema

```sql
-- Sessions table
CREATE TABLE sessions (
  id UUID PRIMARY KEY,
  agent_id VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  last_activity TIMESTAMP NOT NULL,
  preferences JSONB,
  INDEX idx_agent_id (agent_id),
  INDEX idx_last_activity (last_activity)
);

-- Enabled capabilities per session
CREATE TABLE session_capabilities (
  session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
  capability_id VARCHAR(255) NOT NULL,
  enabled_at TIMESTAMP NOT NULL,
  PRIMARY KEY (session_id, capability_id)
);

-- Tool execution logs
CREATE TABLE tool_executions (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES sessions(id),
  tool_name VARCHAR(255) NOT NULL,
  parameters JSONB,
  result JSONB,
  success BOOLEAN NOT NULL,
  execution_time_ms INTEGER NOT NULL,
  created_at TIMESTAMP NOT NULL,
  INDEX idx_session_id (session_id),
  INDEX idx_tool_name (tool_name),
  INDEX idx_created_at (created_at)
);

-- Usage metrics
CREATE TABLE usage_metrics (
  id UUID PRIMARY KEY,
  date DATE NOT NULL,
  agent_id VARCHAR(255) NOT NULL,
  capability_id VARCHAR(255) NOT NULL,
  invocation_count INTEGER NOT NULL,
  total_execution_time_ms BIGINT NOT NULL,
  total_tokens_used INTEGER NOT NULL,
  PRIMARY KEY (date, agent_id, capability_id)
);
```

### File System Structure

```
/skills
  ├── code-review/
  │   ├── SKILL.md
  │   ├── checklist.md
  │   └── templates/
  │       └── review-template.md
  ├── api-design/
  │   ├── SKILL.md
  │   └── schemas/
  │       ├── rest-api.yaml
  │       └── graphql.schema
  └── testing/
      ├── SKILL.md
      └── scripts/
          └── test-generator.ts

/toolsets
  ├── repository.ts
  ├── issues.ts
  ├── pull-requests.ts
  └── security.ts
```

## Security Architecture

### Authentication Flow

```
Client Request
     │
     ▼
[API Gateway]
     │
     ├─── Extract Token
     │    (Bearer, API Key, or OAuth)
     │
     ▼
[Auth Service]
     │
     ├─── Validate Token
     ├─── Load Permissions
     └─── Create Auth Context
     │
     ▼
[Request Handler]
```

### Authorization Model

```typescript
interface Permission {
  resource: string;  // e.g., "toolset:issues"
  action: string;    // e.g., "read", "write", "execute"
  conditions?: {
    repositories?: string[];
    rateLimit?: number;
  };
}

interface AuthContext {
  clientId: string;
  permissions: Permission[];
  rateLimit: {
    requestsPerMinute: number;
    tokensPerHour: number;
  };
}
```

### Security Layers

1. **Network Layer**
   - TLS 1.3 for all connections
   - IP whitelisting (optional)
   - DDoS protection

2. **Authentication Layer**
   - JWT tokens with short expiry
   - Refresh token rotation
   - API key management

3. **Authorization Layer**
   - Role-based access control
   - Resource-level permissions
   - Capability-specific access

4. **Input Validation**
   - JSON schema validation
   - Parameter sanitization
   - SQL injection prevention

5. **Output Filtering**
   - PII redaction
   - Secret detection
   - Response size limits

6. **Audit Layer**
   - All requests logged
   - Sensitive operation alerts
   - Compliance reporting

## Scalability Considerations

### Horizontal Scaling

**Load Balancer Configuration**:
```yaml
algorithm: least_connections
health_check:
  endpoint: /health
  interval: 10s
  timeout: 5s
  unhealthy_threshold: 3

sticky_sessions: false  # Stateless design
```

**Server Instances**:
- Auto-scaling based on CPU/memory
- Minimum 2 instances for HA
- Maximum scales with demand
- Graceful shutdown on scale-down

### Caching Strategy

**Cache Levels**:

1. **L1: In-Memory Cache** (per instance)
   - Capability metadata
   - Frequently used skills
   - Session data (with Redis sync)
   - TTL: 5 minutes

2. **L2: Redis Cache** (shared)
   - All session data
   - Loaded capabilities
   - Rate limit counters
   - TTL: 1 hour

3. **L3: CDN** (for static assets)
   - Skill markdown files
   - Templates and schemas
   - Documentation
   - TTL: 24 hours

### Performance Targets

- **API Response Time**: < 100ms (p95)
- **Tool Execution**: < 500ms (p95)
- **Skill Loading**: < 200ms (p95)
- **Throughput**: 1000 requests/second per instance
- **Concurrent Sessions**: 10,000 per instance

## Monitoring and Observability

### Metrics Collection

```typescript
interface Metrics {
  // Request metrics
  requestsTotal: Counter;
  requestDuration: Histogram;
  requestErrors: Counter;
  
  // Capability metrics
  capabilitiesEnabled: Counter;
  capabilityLoadTime: Histogram;
  
  // Tool execution metrics
  toolExecutions: Counter;
  toolExecutionDuration: Histogram;
  toolErrors: Counter;
  
  // Resource metrics
  tokensUsed: Counter;
  contextBudgetUtilization: Gauge;
  cacheHitRate: Gauge;
  
  // System metrics
  activeConnections: Gauge;
  activeSessions: Gauge;
  memoryUsage: Gauge;
  cpuUsage: Gauge;
}
```

### Logging Strategy

```typescript
// Structured logging
logger.info('Tool executed', {
  sessionId: context.sessionId,
  toolName: 'list_issues',
  duration: 145,
  tokensUsed: 50,
  success: true,
  timestamp: new Date().toISOString()
});
```

### Alerting Rules

1. **Error Rate > 5%**: Alert immediately
2. **Response Time > 1s (p95)**: Alert within 5min
3. **Cache Hit Rate < 70%**: Warning
4. **Memory Usage > 90%**: Alert immediately
5. **Failed Authentication > 100/min**: Security alert

## Deployment Architecture

### Container Structure

```dockerfile
# Multi-stage build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: mcp-server:latest
        ports:
        - containerPort: 3000
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Disaster Recovery

### Backup Strategy

1. **Session Data**: Replicated in Redis cluster
2. **Execution Logs**: Daily backups to S3
3. **Configuration**: Version controlled in Git
4. **Secrets**: Stored in Kubernetes secrets with encryption

### Recovery Procedures

1. **Instance Failure**: Auto-healing via Kubernetes
2. **Redis Failure**: Failover to replica
3. **Complete Outage**: Restore from backups within 1 hour
4. **Data Corruption**: Point-in-time recovery from backups

## Future Enhancements

1. **Multi-tenancy**: Isolated environments per organization
2. **Skill Marketplace**: Share and discover community skills
3. **Version Control**: Skills and toolsets versioning
4. **Analytics Dashboard**: Usage insights and trends
5. **A/B Testing**: Test different skill implementations
6. **Federated Learning**: Learn from usage patterns
7. **Multi-region**: Geographic distribution for latency
8. **GraphQL API**: Alternative API interface
9. **WebSocket Support**: Real-time streaming responses
10. **Skill Composition**: Combine multiple skills dynamically
