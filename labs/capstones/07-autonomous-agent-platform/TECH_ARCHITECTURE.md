# Technical Architecture: Autonomous Agent System

## Architecture Overview

```
[User Input / Goal]
       |
+------v-------+
| Agent Runtime |
| (Observe-    |
|  Think-Act)  |
+------+-------+
       |
+------v-------+    +---------------+
| Planning     |<-->| Tool Registry |
| Engine       |    | - Calculator  |
| (ReAct)      |    | - Web Search  |
+------+-------+    | - Code Exec   |
       |            | - Data Query  |
+------v-------+    +---------------+
| Agent Memory |
| - Short-term |
| - Episodic   |
| - Semantic   |
+------+-------+
       |
+------v-------+
| Multi-Agent  |
| Orchestrator |
+------+-------+
       |
+------v-------+
| Agent Monitor|
| + Dashboard  |
+--------------+
```

## Component Breakdown

### 1. Agent Runtime (Observe-Think-Act Loop)
- **Observe**: Gather current state (goal, recent steps, relevant memories, tool descriptions)
- **Think**: Call PlanningEngine with observation to generate reasoning + action
- **Act**: Execute action (tool call, think, delegate), collect result
- **Loop**: Repeat until goal achieved, max iterations reached, or fatal error
- **Config**: maxIterations (default 15), stepTimeout (default 30s), retryOnError (default true)

### 2. Planning Engine (ReAct)
- **Input**: Observation (goal, context, tools, memories)
- **Processing**: LLM call with structured ReAct prompt
- **Output**: Parsed Thought (reasoning + action type + tool name + parameters)
- **Prompt template**: System instructions + Goal + Tool descriptions + Recent steps + Relevant memories + Output format
- **Parsing**: Extract Thought/Action/Action Input sections using regex; parse Action Input JSON

### 3. Tool Registry
- **Registration**: Map<String, Tool>; each tool must implement getName(), getDescription(), getInputSchema(), execute()
- **Built-in tools**: calculator, web_search, code_execution, data_query, file_read, datetime
- **Delegation tools**: Dynamically registered per agent; delegate_agent_{name} for each registered sub-agent
- **Error handling**: Tool returns ActionResult.success/failure; agent handles failure in next planning step

### 4. Agent Memory
- **Short-term**: LinkedHashMap (capacity 100); stores key-value pairs; LRU eviction; used for conversation context
- **Episodic memory**: Vector database; stores full episodes (session, step, goal, thought, action, result); retrieved by similarity
- **Semantic memory**: Vector database; stores concepts and facts extracted from tool outputs; cross-session knowledge
- **Retrieval**: Query embedding + vector similarity search; top-K results (default 5) appended to observation

### 5. Multi-Agent Orchestrator
- **Supervisor agent**: Decomposes complex goals into sub-goals; assigns sub-goals to specialist agents
- **Specialist agents**: Each handles a domain (research, code, data analysis, creative writing)
- **Delegation protocol**: Supervisor sends (sub-goal + context) to specialist; specialist returns structured result
- **Synthesis**: Supervisor combines sub-results into coherent final answer

### 6. Agent Monitor
- **Event sourcing**: All agent decisions, tool calls, and results logged as MonitorEvent
- **Session traces**: Complete execution trace per session (goal, steps, duration, status)
- **Dashboard**: Real-time metrics (active sessions, success rate, avg steps, avg duration, recent events)
- **Observability**: Micrometer metrics (session duration, step duration, tool call latency, error rate)

## Agent Execution Flow

```
Iteration 1:
  OBSERVE: Goal="Calculate Q3 revenue growth", Tools=[calculator, data_query], Recent=[], Memories=[]
  THINK: "I need to first query the revenue data for Q2 and Q3"
  ACT: data_query({"query": "SELECT revenue FROM financials WHERE quarter IN ('Q2','Q3')"})
  RESULT: Q2=$1.2M, Q3=$1.5M

Iteration 2:
  OBSERVE: Goal="Calculate Q3 revenue growth", Recent=["data_query: Q2=$1.2M, Q3=$1.5M"], Tools=[calculator]
  THINK: "Growth = (Q3-Q2)/Q2 = (1.5-1.2)/1.2 = 0.25 = 25%"
  ACT: calculator({"expression": "(1.5 - 1.2) / 1.2 * 100"})
  RESULT: 25.0

Iteration 3:
  OBSERVE: Goal="Calculate Q3 revenue growth", Recent=["calculator: 25.0"]
  THINK: "The result is 25.0. The goal is achieved."
  ACT: think("Q3 revenue growth is 25% compared to Q2")
  RESULT: Goal achieved!
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Java 21 | Runtime |
| LLM Interface | OpenAI API / Anthropic API | ReAct planning |
| Vector Store | Custom HNSW / Pinecone | Long-term memory |
| Tool Framework | Custom (Tool interface) | Extensible tools |
| Orchestration | Custom (Supervisor pattern) | Multi-agent coordination |
| Monitoring | Micrometer + Prometheus | Observability |
| Serialization | Jackson | Structured data |

## Memory Architecture

```
Short-term (Working):
  Capacity: 100 entries (LRU)
  Scope: Current session
  Persistence: In-memory only

Episodic (Past sessions):
  Storage: Vector database
  Granularity: Per-step (session+step key)
  Retrieval: Similarity search on goal/thought embeddings
  Retention: 90 days

Semantic (Knowledge):
  Storage: Vector database
  Content: Facts extracted from tool outputs
  Examples: "Q3 2025 revenue was $1.5M", "API rate limit is 100 req/min"
  Retention: Permanent until explicitly forgotten
```

## Configuration

```yaml
agent:
  name: supervisor
  maxIterations: 15
  stepTimeoutMs: 30000
  retryOnError: true

planning:
  provider: openai
  model: gpt-4-turbo
  temperature: 0.3
  maxTokens: 2048

memory:
  shortTermCapacity: 100
  longTermTopK: 5
  episodicRetentionDays: 90

monitoring:
  metricsEnabled: true
  eventLogRetention: 10000
  dashboardRefreshMs: 5000
```

## Security

- **Tool sandboxing**: Code execution tool runs in isolated container (gVisor/Firecracker)
- **Input sanitization**: All tool parameters validated against input schema; HTML/JS stripped from web search results
- **Rate limiting**: Per-agent rate limits (60 calls/min per agent); per-tool rate limits (10 calls/min for web search)
- **Audit log**: All agent decisions, tool inputs, and outputs logged to immutable audit store
