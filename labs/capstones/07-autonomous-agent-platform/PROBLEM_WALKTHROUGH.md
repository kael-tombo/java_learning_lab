# Problem Walkthrough: Autonomous Agent System with Planning and Tool Use

## Problem Statement

**Design an autonomous agent system that observes its environment, plans actions using ReAct (Reasoning + Acting) methodology, maintains short-term and long-term memory, uses a registry of pluggable tools, supports multi-agent orchestration with delegation, and provides monitoring for observability.**

The system must handle complex multi-step tasks that require planning (goal decomposition, tool selection, execution, evaluation), adapt to changing conditions, and maintain coherent state across extended interactions.

### Business Requirements
- Autonomous goal decomposition: break complex goals into sub-tasks
- ReAct planning: interleave reasoning traces with tool calls
- 20+ pluggable tools (web search, calculator, code execution, data retrieval)
- Short-term memory (conversation context) with 8K token window
- Long-term memory (episodic + semantic) with vector-based retrieval
- Multi-agent orchestration: supervisor agent delegates to specialist agents
- Monitoring: agent decisions, tool usage, execution traces, latency breakdowns

### Technical Constraints
- Java 21+ runtime
- Observe-Think-Act loop with configurable max iterations
- Tool registry with typed inputs/outputs and error handling
- Memory: in-memory buffer (short-term) + vector store (long-term)
- ReAct planner: LLM-based planning with structured output parsing
- Multi-agent: hierarchical (supervisor + workers) with delegation protocol
- Monitoring: event-sourced execution traces with real-time dashboard

---

## Solution Architecture

### Step 1: Core Agent Runtime (Observe-Think-Act Loop)

```java
public class AgentRuntime {
    private final String agentId;
    private final PlanningEngine planner;
    private final ToolRegistry toolRegistry;
    private final AgentMemory memory;
    private final AgentMonitor monitor;
    private final int maxIterations;

    public AgentRuntime(String agentId, PlanningEngine planner, ToolRegistry tools,
                        AgentMemory memory, AgentMonitor monitor, int maxIterations) {
        this.agentId = agentId;
        this.planner = planner;
        this.toolRegistry = tools;
        this.memory = memory;
        this.monitor = monitor;
        this.maxIterations = maxIterations;
    }

    public ExecutionResult execute(Goal goal) {
        String sessionId = UUID.randomUUID().toString();
        monitor.startSession(sessionId, agentId, goal);

        memory.storeShortTerm("goal", goal.getDescription());
        ExecutionContext ctx = new ExecutionContext(sessionId, agentId, goal);

        try {
            for (int iteration = 0; iteration < maxIterations; iteration++) {
                long stepStart = System.nanoTime();

                // 1. OBSERVE: Gather current state
                Observation observation = observe(ctx);

                // 2. THINK: Plan next action using ReAct
                Thought thought = planner.plan(ctx, observation);

                // 3. ACT: Execute planned action
                ActionResult actionResult = act(ctx, thought.getAction());

                // Update context
                ctx.addStep(new ExecutionStep(observation, thought, actionResult));

                // Store in memory
                memory.storeShortTerm("step_" + iteration, thought.getReasoning());
                memory.storeEpisodic(sessionId, iteration, observation, thought, actionResult);

                // Monitor
                long stepDuration = System.nanoTime() - stepStart;
                monitor.logStep(sessionId, iteration, thought, actionResult, stepDuration);

                // Check if goal achieved
                if (actionResult.isGoalAchieved()) {
                    monitor.completeSession(sessionId, "SUCCESS", iteration);
                    return new ExecutionResult(sessionId, "SUCCESS",
                        ctx.getSteps(), actionResult.getFinalAnswer());
                }

                // Check for errors
                if (actionResult.isFatal()) {
                    monitor.completeSession(sessionId, "FAILED", iteration);
                    return new ExecutionResult(sessionId, "FAILED",
                        ctx.getSteps(), actionResult.getError());
                }
            }

            monitor.completeSession(sessionId, "MAX_ITERATIONS", maxIterations);
            return new ExecutionResult(sessionId, "MAX_ITERATIONS",
                ctx.getSteps(), "Exceeded max iterations");
        } catch (Exception e) {
            monitor.completeSession(sessionId, "ERROR", -1);
            throw new AgentException("Agent execution failed", e);
        }
    }

    private Observation observe(ExecutionContext ctx) {
        List<String> recentSteps = memory.getRecentShortTerm(5);
        List<String> relevantMemories = memory.queryLongTerm(ctx.getGoal().getDescription(), 3);
        String toolsAvailable = toolRegistry.getToolDescriptions();

        return new Observation(ctx.getGoal(), recentSteps, relevantMemories, toolsAvailable);
    }

    private ActionResult act(ExecutionContext ctx, Action action) {
        if (action.getType() == ActionType.TOOL_CALL) {
            Tool tool = toolRegistry.getTool(action.getToolName());
            if (tool == null) {
                return ActionResult.error("Tool not found: " + action.getToolName());
            }
            try {
                return tool.execute(action.getParameters());
            } catch (Exception e) {
                return ActionResult.error("Tool execution failed: " + e.getMessage());
            }
        } else if (action.getType() == ActionType.THINK) {
            return ActionResult.thought(action.getReasoning());
        } else if (action.getType() == ActionType.DELEGATE) {
            return delegateToAgent(ctx, action);
        } else {
            return ActionResult.error("Unknown action type: " + action.getType());
        }
    }

    private ActionResult delegateToAgent(ExecutionContext ctx, Action action) {
        String agentName = action.getParameters().get("agent");
        String subGoal = action.getParameters().get("goal");
        // Delegate to sub-agent and await result
        AgentRuntime subAgent = AgentRegistry.getAgent(agentName);
        Goal subGoalObj = new Goal(subGoal, ctx.getGoal().getPriority());
        ExecutionResult result = subAgent.execute(subGoalObj);
        return ActionResult.delegationResult(agentName, result);
    }
}
```

### Step 2: ReAct Planning Engine

```java
public class PlanningEngine {
    private final LLMInterface llm;
    private final ToolRegistry toolRegistry;

    public PlanningEngine(LLMInterface llm, ToolRegistry toolRegistry) {
        this.llm = llm;
        this.toolRegistry = toolRegistry;
    }

    public Thought plan(ExecutionContext ctx, Observation observation) {
        // Build ReAct prompt
        String prompt = buildReActPrompt(observation);

        // Call LLM
        String llmResponse = llm.generate(prompt);

        // Parse structured response
        return parseThought(llmResponse);
    }

    private String buildReActPrompt(Observation observation) {
        StringBuilder sb = new StringBuilder();
        sb.append("You are an autonomous agent. Answer the following goal using the tools available.\n\n");
        sb.append("Goal: ").append(observation.getGoal().getDescription()).append("\n\n");
        sb.append("Available tools:\n");
        sb.append(toolRegistry.getToolDescriptions()).append("\n\n");

        List<String> recentSteps = observation.getRecentSteps();
        if (!recentSteps.isEmpty()) {
            sb.append("Recent steps:\n");
            for (String step : recentSteps) {
                sb.append("- ").append(step).append("\n");
            }
            sb.append("\n");
        }

        List<String> memories = observation.getRelevantMemories();
        if (!memories.isEmpty()) {
            sb.append("Relevant past experiences:\n");
            for (String memory : memories) {
                sb.append("- ").append(memory).append("\n");
            }
            sb.append("\n");
        }

        sb.append("Available tools:\n");
        sb.append(toolRegistry.getToolDescriptions()).append("\n\n");

        sb.append("Respond in this format:\n");
        sb.append("Thought: <your reasoning>\n");
        sb.append("Action: <tool_name | think | delegate>\n");
        sb.append("Action Input: <json parameters>\n");

        return sb.toString();
    }

    private Thought parseThought(String llmResponse) {
        // Parse structured output from LLM
        String reasoning = extractSection(llmResponse, "Thought:");
        String action = extractSection(llmResponse, "Action:");
        String actionInput = extractSection(llmResponse, "Action Input:");

        ActionType actionType;
        String toolName = null;
        Map<String, String> parameters = new HashMap<>();

        switch (action.trim().toLowerCase()) {
            case "think":
                actionType = ActionType.THINK;
                break;
            case "delegate":
                actionType = ActionType.DELEGATE;
                parameters = parseJson(actionInput);
                break;
            default:
                actionType = ActionType.TOOL_CALL;
                toolName = action.trim();
                parameters = parseJson(actionInput);
                break;
        }

        return new Thought(reasoning, actionType, toolName, parameters);
    }

    private String extractSection(String text, String header) {
        int start = text.indexOf(header);
        if (start < 0) return "";
        start += header.length();

        // Find next section or end
        String[] headers = {"Thought:", "Action:", "Action Input:", "Observation:"};
        int end = text.length();
        for (String h : headers) {
            int idx = text.indexOf(h, start);
            if (idx >= 0 && idx < end) end = idx;
        }

        return text.substring(start, end).trim();
    }

    private Map<String, String> parseJson(String json) {
        // Simple key-value parsing for structured JSON input
        Map<String, String> params = new HashMap<>();
        try {
            ObjectMapper mapper = new ObjectMapper();
            Map<String, Object> parsed = mapper.readValue(json,
                new TypeReference<Map<String, Object>>() {});
            parsed.forEach((k, v) -> params.put(k, String.valueOf(v)));
        } catch (Exception e) {
            params.put("input", json);
        }
        return params;
    }
}

class Thought {
    private final String reasoning;
    private final ActionType actionType;
    private final String toolName;
    private final Map<String, String> parameters;

    Thought(String reasoning, ActionType type, String toolName, Map<String, String> params) {
        this.reasoning = reasoning;
        this.actionType = type;
        this.toolName = toolName;
        this.parameters = params;
    }

    public Action getAction() {
        return new Action(actionType, toolName, reasoning, parameters);
    }
}
```

### Step 3: Tool Registry

```java
public class ToolRegistry {
    private final Map<String, Tool> tools = new ConcurrentHashMap<>();

    public void registerTool(Tool tool) {
        tools.put(tool.getName(), tool);
    }

    public Tool getTool(String name) {
        return tools.get(name);
    }

    public String getToolDescriptions() {
        return tools.values().stream()
            .map(t -> t.getName() + ": " + t.getDescription()
                + " (inputs: " + t.getInputSchema() + ")")
            .collect(Collectors.joining("\n"));
    }
}

public interface Tool {
    String getName();
    String getDescription();
    String getInputSchema();
    ActionResult execute(Map<String, String> parameters);
}

public class CalculatorTool implements Tool {
    @Override
    public String getName() { return "calculator"; }

    @Override
    public String getDescription() { return "Evaluates mathematical expressions. Input: expression(string)"; }

    @Override
    public String getInputSchema() { return "{\"expression\": \"string\"}"; }

    @Override
    public ActionResult execute(Map<String, String> params) {
        String expression = params.get("expression");
        try {
            // Evaluate expression safely (using ScriptEngine or custom parser)
            ScriptEngineManager manager = new ScriptEngineManager();
            ScriptEngine engine = manager.getEngineByName("JavaScript");
            Object result = engine.eval(expression);
            return ActionResult.success("Result: " + result.toString());
        } catch (Exception e) {
            return ActionResult.error("Calculation error: " + e.getMessage());
        }
    }
}

public class WebSearchTool implements Tool {
    private final WebSearchClient searchClient;

    @Override
    public String getName() { return "web_search"; }

    @Override
    public String getDescription() { return "Search the web for information. Input: query(string)"; }

    @Override
    public ActionResult execute(Map<String, String> params) {
        String query = params.get("query");
        if (query == null) query = params.get("input");
        try {
            String results = searchClient.search(query);
            return ActionResult.success(results);
        } catch (Exception e) {
            return ActionResult.error("Search failed: " + e.getMessage());
        }
    }
}
```

### Step 4: Agent Memory

```java
public class AgentMemory {
    private final Map<String, String> shortTermMemory = new LinkedHashMap<String, String>() {
        @Override protected boolean removeEldestEntry(Map.Entry<String, String> eldest) {
            return size() > 100;  // Keep last 100 entries
        }
    };
    private final VectorStore longTermMemory;

    public AgentMemory(VectorStore vectorStore) {
        this.longTermMemory = vectorStore;
    }

    // Short-term (working memory)
    public void storeShortTerm(String key, String value) {
        shortTermMemory.put(key, value);
    }

    public String getShortTerm(String key) {
        return shortTermMemory.get(key);
    }

    public List<String> getRecentShortTerm(int n) {
        return shortTermMemory.entrySet().stream()
            .skip(Math.max(0, shortTermMemory.size() - n))
            .map(e -> e.getKey() + ": " + e.getValue())
            .collect(Collectors.toList());
    }

    // Long-term (episodic + semantic)
    public void storeEpisodic(String sessionId, int step,
                               Observation observation, Thought thought, ActionResult result) {
        String episode = String.format("[Session: %s, Step: %d] Goal: %s | Thought: %s | Action: %s | Result: %s",
            sessionId, step,
            observation.getGoal().getDescription(),
            thought.getReasoning(),
            thought.getAction().getType(),
            result.isSuccess() ? "Success" : "Error: " + result.getError());

        longTermMemory.insert(hashCode(sessionId + "_" + step),
            VectorMath.normalize(randomVector(768)),
            Map.of("episode", episode, "session", sessionId, "step", String.valueOf(step)));
    }

    public void storeSemantic(String concept, String information) {
        longTermMemory.insert(hashCode(concept),
            VectorMath.normalize(randomVector(768)),
            Map.of("concept", concept, "information", information));
    }

    public List<String> queryLongTerm(String query, int topK) {
        float[] queryVec = VectorMath.normalize(randomVector(768));  // Mock
        List<SearchResult> results = longTermMemory.search(queryVec, topK, 10);
        return results.stream()
            .map(r -> r.getMetadata().getOrDefault("episode",
                     r.getMetadata().getOrDefault("information", "")))
            .collect(Collectors.toList());
    }

    private float[] randomVector(int dim) {
        float[] vec = new float[dim];
        for (int i = 0; i < dim; i++) vec[i] = (float) Math.random();
        return vec;
    }

    private int hashCode(String s) { return s.hashCode(); }
}
```

### Step 5: Multi-Agent Orchestrator

```java
public class MultiAgentOrchestrator {
    private final AgentRuntime supervisor;
    private final Map<String, AgentRuntime> agents = new ConcurrentHashMap<>();
    private final AgentMonitor monitor;

    public MultiAgentOrchestrator(AgentRuntime supervisor, AgentMonitor monitor) {
        this.supervisor = supervisor;
        this.monitor = monitor;
    }

    public void registerAgent(String name, AgentRuntime agent) {
        agents.put(name, agent);
        // Register delegation tool in supervisor
        supervisor.getToolRegistry().registerTool(new DelegationTool(name, agent));
    }

    public ExecutionResult executeComplexGoal(ComplexGoal goal) {
        monitor.log("orchestrator", "Starting complex goal: " + goal.getDescription());

        // Supervisor decomposes and delegates
        ExecutionPlan plan = supervisor.decomposeGoal(goal);
        monitor.log("orchestrator", "Created execution plan with " + plan.getSubGoals().size() + " steps");

        List<ExecutionResult> subResults = new ArrayList<>();
        for (SubGoal subGoal : plan.getSubGoals()) {
            monitor.log("orchestrator", "Delegating sub-goal: " + subGoal.getDescription()
                + " to agent: " + subGoal.getAssignedAgent());

            AgentRuntime agent = agents.get(subGoal.getAssignedAgent());
            if (agent == null) {
                throw new AgentException("No agent found: " + subGoal.getAssignedAgent());
            }

            ExecutionResult result = agent.execute(new Goal(subGoal.getDescription(), subGoal.getPriority()));
            subResults.add(result);
            monitor.log("orchestrator", "Sub-goal completed: " + subGoal.getDescription()
                + " status: " + result.getStatus());
        }

        // Synthesize results
        String finalAnswer = supervisor.synthesizeResults(goal, subResults);
        return new ExecutionResult(UUID.randomUUID().toString(), "SUCCESS",
            subResults, finalAnswer);
    }

    static class ComplexGoal {
        private final String description;
        private final List<String> requiredDomains;
        ComplexGoal(String description, List<String> domains) {
            this.description = description; this.requiredDomains = domains;
        }
        public String getDescription() { return description; }
    }

    static class ExecutionPlan {
        private final List<SubGoal> subGoals;
        ExecutionPlan(List<SubGoal> subGoals) { this.subGoals = subGoals; }
        public List<SubGoal> getSubGoals() { return subGoals; }
    }

    static class SubGoal {
        private final String description;
        private final String assignedAgent;
        private final int priority;
        SubGoal(String description, String agent, int priority) {
            this.description = description; this.assignedAgent = agent; this.priority = priority;
        }
        public String getDescription() { return description; }
        public String getAssignedAgent() { return assignedAgent; }
        public int getPriority() { return priority; }
    }
}
```

### Step 6: Monitoring

```java
public class AgentMonitor {
    private final Map<String, SessionTrace> sessions = new ConcurrentHashMap<>();
    private final List<MonitorEvent> eventLog = new CopyOnWriteArrayList<>();

    public void startSession(String sessionId, String agentId, Goal goal) {
        sessions.put(sessionId, new SessionTrace(sessionId, agentId, goal, System.currentTimeMillis()));
        eventLog.add(new MonitorEvent(sessionId, "SESSION_START", agentId, goal.getDescription()));
    }

    public void logStep(String sessionId, int iteration, Thought thought,
                         ActionResult result, long durationNanos) {
        SessionTrace trace = sessions.get(sessionId);
        if (trace != null) {
            trace.addStep(new StepTrace(iteration, thought, result, durationNanos));
        }
        eventLog.add(new MonitorEvent(sessionId, "STEP", null,
            String.format("Iteration %d: %s -> %s (%dms)",
                iteration, thought.getAction().getType(),
                result.isSuccess() ? "OK" : "FAIL",
                durationNanos / 1_000_000)));
    }

    public void completeSession(String sessionId, String status, int totalSteps) {
        SessionTrace trace = sessions.get(sessionId);
        if (trace != null) {
            trace.setStatus(status);
            trace.setTotalSteps(totalSteps);
            trace.setEndTime(System.currentTimeMillis());
        }
    }

    public MonitorDashboard getDashboard() {
        long totalSessions = sessions.size();
        long activeSessions = sessions.values().stream()
            .filter(s -> s.getStatus().equals("RUNNING")).count();
        long successSessions = sessions.values().stream()
            .filter(s -> s.getStatus().equals("SUCCESS")).count();
        long failedSessions = sessions.values().stream()
            .filter(s -> s.getStatus().equals("FAILED")).count();

        double avgSteps = sessions.values().stream()
            .filter(s -> s.getStatus().equals("SUCCESS"))
            .mapToInt(SessionTrace::getTotalSteps).average().orElse(0);

        double avgDuration = sessions.values().stream()
            .filter(s -> s.getStatus().equals("SUCCESS"))
            .mapToLong(s -> s.getEndTime() - s.getStartTime()).average().orElse(0);

        return new MonitorDashboard(totalSessions, activeSessions,
            successSessions, failedSessions, avgSteps, avgDuration,
            getRecentEvents(20));
    }

    public List<MonitorEvent> getRecentEvents(int n) {
        return eventLog.size() > n
            ? eventLog.subList(eventLog.size() - n, eventLog.size())
            : new ArrayList<>(eventLog);
    }
}
```

---

## Best Practices

### Planning
1. **ReAct with structured output**: Always enforce structured output format (Thought/Action/Action Input) for reliable parsing
2. **Max iterations**: Start with 10-15 max iterations; higher values risk infinite loops and token exhaustion
3. **Goal decomposition**: Complex goals should be decomposed into sub-goals (max 5-7 per level) for reliable execution
4. **Context window management**: After 5-8 steps, summarize recent history to avoid exceeding token limits

### Tool Design
1. **Input/output schemas**: Every tool must have typed input parameters and structured return values for reliable parsing
2. **Error handling**: Tools should return ActionResult.success/failure rather than throwing exceptions; agent handles failure gracefully
3. **Timeout protection**: Each tool execution must have a configurable timeout (default 30s); kill hanging tool calls
4. **Tool chaining**: If a task requires multiple tools, the agent should plan the sequence rather than expecting a single tool to do everything

### Memory
1. **Short-term vs long-term**: Short-term is conversation buffer (last 5-10 steps); long-term is vector-indexed past sessions for pattern recall
2. **Memory consolidation**: After session completion, summarize long sessions and store summary in long-term memory
3. **Episodic retrieval**: When facing a similar goal, retrieve relevant past sessions to inform current planning
4. **Forgetting**: Implement decay for long-term memory; memories older than 30 days have lower retrieval weight

### Multi-Agent
1. **Supervisor pattern**: Single supervisor agent decomposes goals and delegates to specialist agents; avoids coordination complexity
2. **Agent specialization**: Each agent should specialize in one domain (research, code, math); avoid overlapping capabilities
3. **Handoff protocol**: Delegation should include context (goal, relevant memories, constraints); agent reports back with structured result
4. **Error escalation**: If a sub-agent fails, supervisor should retry with different approach or fall back to alternative agent

### Safety
1. **Input validation**: All tool inputs must be validated and sanitized; prevent prompt injection via tool parameters
2. **Rate limiting**: Limit tool calls per minute (60/min for web search, 300/min for calculator) to prevent abuse
3. **Human-in-the-loop**: For destructive actions (file deletion, database modification), require human confirmation before execution
4. **Audit trail**: Every agent decision, tool call, and result must be logged for post-hoc analysis

## Performance Benchmarks

| Metric | Value | Condition |
|--------|-------|-----------|
| Goal decomposition | 500ms | Complex goal into 5 sub-goals |
| ReAct planning iteration | 2s | LLM call + parsing (GPT-4) |
| Tool execution (calculator) | 10ms | Simple arithmetic |
| Tool execution (web search) | 1.5s | HTTP request + parse |
| Memory retrieval (long-term) | 50ms | Vector search, 10K memories |
| Session completion | 30s-5min | 5-15 iterations |
| Multi-agent delegation | 500ms | Supervisor to sub-agent handoff |
| Monitoring overhead | < 5ms | Per-step instrumentation |
