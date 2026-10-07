# Anthropic AI Interview Guide

## Table of Contents
1. [Company Overview](#company-overview)
2. [Company Background & Mission](#company-background--mission)
3. [Interview Process Overview](#interview-process-overview)
4. [Role Types](#role-types)
5. [Claude Architecture & Model Family](#claude-architecture--model-family)
6. [Key Technical Concepts](#key-technical-concepts)
7. [Coding Expectations](#coding-expectations)
8. [System Design Topics](#system-design-topics)
9. [Research Preparation](#research-preparation)
10. [Behavioral Questions](#behavioral-questions)
11. [Sample Questions & Answers](#sample-questions--answers)
12. [Resources & Further Reading](#resources--further-reading)

---

## Company Overview

- **Founded:** 2021
- **Founders:** Dario Amodei, Daniela Amodei, and former OpenAI researchers
- **Headquarters:** San Francisco, CA
- **Key Product:** Claude (AI assistant), Claude API
- **Funding:** Over $7B raised (including investments from Google, Salesforce, Spark Capital)
- **Valuation:** Exceeding $15B (recent rounds)
- **Employees:** ~500+
- **Mission:** Build AI systems that are safe, interpretable, and steerable, with a focus on constitutional AI and alignment research.

Anthropic positions itself as the safety-first alternative in the frontier AI race. The company's entire research and product strategy revolves around understanding, measuring, and controlling advanced AI systems.

---

## Company Background & Mission

### Founding Story
Anthropic was founded by a group of former OpenAI employees who became concerned about the direction and safety practices at OpenAI. Led by Dario Amodei (former VP of Research at OpenAI) and Daniela Amodei (former VP of Safety & Policy at OpenAI), the team wanted to build an AI company where safety research was not an afterthought but the primary driver of technical decisions.

### Core Principles
1. **Safety First:** All model development is guided by safety research. Anthropic believes safety cannot be added after deployment — it must be engineered from the ground up.
2. **Interpretability:** Understanding how models work internally is a first-class research goal, not a side project.
3. **Constitutional AI:** Rather than relying solely on human feedback (RLHF), Anthropic uses AI-generated feedback guided by a constitution of principles to steer model behavior.
4. **Responsible Scaling:** Anthropic advocates for and practices measured, careful scaling of model capabilities with corresponding safety evaluations.

### Key Differences from Competitors
- **vs OpenAI:** More conservative deployment, stronger emphasis on interpretability research, constitutional AI vs heavy RLHF
- **vs Google DeepMind:** Smaller team, more unified research focus, faster iteration
- **vs Cohere:** Frontier research plus product, not just enterprise APIs

---

## Interview Process Overview

### Stage 1: Initial Screen (30-45 minutes)
- Recruiter phone screen
- Discussion of background, research interests, role expectations
- High-level technical fit assessment
- Cultural alignment on safety values

### Stage 2: Technical Phone Screen (60 minutes)
- Role-dependent content:
  - **Research roles:** Discuss past research, paper walkthrough
  - **Engineering roles:** Coding problem (Python), ML concepts
  - **Safety roles:** Alignment problem discussion, technical safety knowledge
- May include a take-home research review or coding assignment

### Stage 3: Virtual Onsite (4-6 hours, split across 1-2 days)
Typically consists of 4-5 sessions:

1. **Research Discussion (60 min)**
   - Present and defend past research
   - Evaluate novel research ideas
   - Demonstrate depth in alignment/safety

2. **Coding Session (60 min)**
   - Algorithmic coding (medium-hard LeetCode)
   - ML implementation from scratch
   - Research code implementation

3. **System Design (45-60 min)**
   - ML system design
   - Scaling inference infrastructure
   - Training pipeline architecture

4. **Alignment & Safety (45-60 min)**
   - Technical safety knowledge
   - Red-teaming approaches
   - Ethical reasoning

5. **Behavioral & Team Fit (30-45 min)**
   - Collaboration style
   - Research philosophy
   - Long-term thinking

### Stage 4: Final Round (optional)
- Meeting with founders or senior leadership
- Strategic thinking about AI safety
- Long-term vision alignment

---

## Role Types

### 1. ML Engineer (MLE)
- **Focus:** Building and optimizing Claude's training and inference infrastructure
- **Key Skills:** Distributed systems, PyTorch, CUDA, performance optimization
- **Interview Weight:** Coding (40%), System Design (35%), ML Knowledge (25%)

### 2. Research Scientist (RS)
- **Focus:** Advancing alignment research, interpretability, safety
- **Key Skills:** Deep learning theory, experimental design, publications
- **Interview Weight:** Research Discussion (50%), Technical Knowledge (30%), Coding (20%)

### 3. Applied AI / Applied Research
- **Focus:** Adapting Claude for real-world applications, API improvements
- **Key Skills:** Full-stack ML, product thinking, prompt engineering
- **Interview Weight:** System Design (35%), Coding (30%), Behavioral (20%), ML (15%)

### 4. Safety Researcher
- **Focus:** Red-teaming, harm evaluation, alignment taxonomies
- **Key Skills:** Adversarial ML, evaluation design, safety metrics
- **Interview Weight:** Safety Knowledge (40%), Research (30%), Coding (20%), Behavioral (10%)

### 5. Infrastructure / Platform Engineer
- **Focus:** Training infrastructure, distributed computing, data pipelines
- **Key Skills:** Kubernetes, high-performance computing, networking
- **Interview Weight:** System Design (45%), Coding (35%), ML Knowledge (20%)

---

## Claude Architecture & Model Family

### Claude Model Family

#### Claude 3.5 (Current Generation)
- **Claude 3.5 Haiku:** Fast, lightweight, low-cost — ideal for real-time applications
- **Claude 3.5 Sonnet:** Balanced performance and speed — best for most workloads
- **Claude 3.5 Opus:** Most capable, deepest reasoning — complex analysis and research

Each variant shares the same core architecture but differs in parameter count, compute budget during training, and inference optimizations.

#### Key Architecture Decisions
1. **Transformer-based:** Foundation is the standard transformer architecture with Anthropic-specific innovations
2. **Constitutional Training:** Unique multi-stage training process combining pretraining, constitutional RLHF, and safety fine-tuning
3. **Long Context:** Claude supports up to 200K tokens context window (approximately 150,000 words)
4. **Tool Use:** Native function calling and tool integration capabilities

### Constitutional AI (CAI)

Constitutional AI is Anthropic's signature technique for training harmless AI assistants without extensive human feedback.

**How it works:**

1. **Supervised Phase:**
   - Model generates responses to harmful prompts
   - Model critiques its own responses using a constitution (set of principles)
   - Model revises responses based on self-critique
   - Fine-tune on revised (harmless) responses

2. **RL Phase (RLAIF):**
   - Generate multiple responses for each prompt
   - Use the constitution to have the model evaluate and rank responses
   - Train a preference model using AI-generated feedback (not human)
   - Optimize the language model using reinforcement learning against this preference model

**The Constitution** includes principles like:
- "Choose the response that is most helpful and honest"
- "Choose the response that avoids stereotyping or discrimination"
- "Choose the response that respects autonomy"
- "Choose the response that is least likely to cause harm"

### RLHF at Anthropic

While Constitutional AI reduces reliance on human feedback, Anthropic still uses human feedback in certain contexts:

- **High-stakes decisions:** Humans evaluate edge cases
- **Constitution refinement:** Human researchers iteratively improve the constitution
- **Red-teaming evaluation:** Human experts probe for failure modes

### Interpretability Research

Anthropic has one of the largest interpretability research teams. Key areas:

1. **Feature Visualization:** Understanding what individual neurons represent
2. **Sparse Autoencoders:** Decomposing model activations into interpretable features
3. **Circuit Analysis:** Tracing how features combine to produce outputs
4. **Activation Patching:** Identifying which model components are causally important

---

## Key Technical Concepts

### Constitutional AI — Deep Dive

**Why CAI instead of pure RLHF?**
- Scalability: Human feedback is expensive and slow
- Consistency: A written constitution provides stable guidance
- Transparency: The constitution is publicly available for scrutiny
- Control: Easier to update and modify compared to retraining reward models

**Technical challenges:**
- How to write principles that don't conflict
- Ensuring the model's self-critique is accurate
- Balancing harmlessness with helpfulness
- Measuring the effectiveness of constitutional training

### RLAIF (Reinforcement Learning from AI Feedback)

RLAIF is a generalization of Constitutional AI where AI models provide the preference labels instead of humans.

**Process:**
1. Prompt model to generate multiple completions
2. Use a separate AI judge (or the same model with a constitutional prompt) to evaluate completions
3. Train a reward model on AI-generated preference data
4. Fine-tune the language model using PPO or similar RL algorithm against this reward model

**Advantages over RLHF:**
- Cheaper and faster data generation
- Can scale to unlimited preference data
- More consistent labeling
- Can use stronger models as judges

**Disadvantages:**
- Potential for reward hacking
- AI judges may share blind spots with the model being trained
- Risk of amplifying existing biases

### Red-Teaming & Safety Evaluation

Anthropic employs systematic red-teaming to find model vulnerabilities:

1. **Automated Red-Teaming:**
   - Use one LLM to generate adversarial prompts
   - Use another to evaluate responses
   - Iterative discovery of failure modes

2. **Human Red-Teaming:**
   - Domain experts probe for specific harms
   - Adversarial users attempt jailbreaks
   - Structured evaluation across harm categories

3. **Taxonomy of Harms:**
   - Anthropic categorizes potential harms into a detailed taxonomy
   - Each category has specific evaluation criteria
   - Regular audits track progress across categories

4. **Responsible Scaling Policy:**
   - Define capability thresholds (AI Safety Level 1-4)
   - Require specific safety measures at each level
   - Independent audit of safety claims

### Interpretability — Technical Foundations

**Sparse Autoencoders (SAEs):**
- Train autoencoders with sparsity constraints on model activations
- Each sparse feature ideally corresponds to a human-interpretable concept
- Challenge: determining the right sparsity level

**Activation Patching:**
- Run model on inputs A and B
- Replace activations from A with activations from B at specific components
- Measure how much the output changes
- Identifies causally important components

**Feature Visualization:**
- For vision models: generate inputs that maximally activate specific neurons
- For language models: find text patterns that trigger specific features
- Challenges: multimodal features, distributed representations

---

## Coding Expectations

### Python Coding

**Core Competencies:**
- Strong Python fundamentals (data structures, OOP, decorators, context managers)
- NumPy/PyTorch proficiency (no TensorFlow at Anthropic)
- Ability to implement ML algorithms from scratch
- Research code: messy is okay as long as it's correct and reproducible

**Common Coding Problems:**

1. **Algorithmic (Medium-Hard LeetCode):**
   - Dynamic programming
   - Graph algorithms (BFS, DFS, Dijkstra, topological sort)
   - Tree operations (BST, segment trees, tries)
   - String manipulation and parsing
   - Concurrency/parallelism basics

2. **ML Implementations (Whiteboard/Coding):**
   - Linear regression from scratch (gradient descent)
   - Multi-head attention implementation
   - Transformer block implementation
   - Layer normalization
   - Cross-entropy loss with softmax
   - K-means clustering
   - PCA implementation

3. **Research Code:**
   - Implement a paper method from description
   - Debug and fix a broken model
   - Add a feature to existing codebase
   - Optimize a slow training loop

### PyTorch Proficiency

**Must Know:**
- `torch.nn.Module` — custom layers and models
- `torch.utils.data.Dataset` and `DataLoader`
- Automatic differentiation (`torch.autograd`)
- Optimizers (`torch.optim`)
- CUDA and device management
- Mixed precision training (`torch.cuda.amp`)
- Distributed training basics (`torch.distributed`)

**Nice to Have:**
- TorchScript / `torch.compile`
- FSDP (Fully Sharded Data Parallel)
- `torch.fx` for model transformation
- Custom CUDA kernels with `torch.utils.cpp_extension`

### Example Coding Question

```
Implement multi-head scaled dot-product attention from scratch.

Given:
- query: (batch_size, seq_len, d_model)
- key:   (batch_size, seq_len, d_model)
- value: (batch_size, seq_len, d_model)
- num_heads: integer
- mask: optional (batch_size, seq_len, seq_len)

Return:
- output: (batch_size, seq_len, d_model)
- attention_weights: (batch_size, num_heads, seq_len, seq_len)
```

---

## System Design Topics

### Scaling Inference

**Key Challenges:**
1. **Latency:** Claude must respond quickly despite massive model size
2. **Cost:** Inference at scale is expensive — optimization is critical
3. **Throughput:** Serving millions of users requires efficient batching
4. **Context Length:** 200K token context requires careful memory management

**Architecture Considerations:**
- **KV Cache Management:** Efficient caching of key-value pairs across requests
- **Continuous Batching:** Dynamically add/remove sequences from batches
- **Speculative Decoding:** Use a smaller draft model to accelerate generation
- **Quantization:** INT8/FP8 quantization for inference
- **Model Parallelism:** Tensor parallelism and pipeline parallelism
- **Prefix Caching:** Cache computations for common prefixes across requests

**Infrastructure Stack:**
- GPU clusters (NVIDIA H100/H200)
- High-speed interconnects (NVLink, InfiniBand)
- Custom inference servers (not just standard TorchServe)
- Load balancing and request routing

### Context Window Management

**Challenges with Long Contexts:**
- Attention computation scales quadratically with sequence length
- Memory usage grows linearly with KV cache size
- Model may lose focus on relevant information in very long contexts

**Solutions:**
- **Sliding Window Attention:** Only attend to recent tokens
- **Sparse Attention Patterns:** Attend to selected tokens only
- **Memory Retrieval:** External memory that model can query
- **Hierarchical Summarization:** Compress context hierarchically
- **Attention Sink:** Handle initial tokens that attract disproportionate attention

### Training Infrastructure

**Training at Anthropic Scale:**
- Thousands of GPUs for single training run
- Months of continuous training
- Frequent checkpointing and failure recovery
- Real-time monitoring of training metrics

**Key Components:**
- Data loading and preprocessing pipelines
- Distributed training orchestration
- Experiment tracking and hyperparameter management
- Evaluation and benchmarking infrastructure

---

## Research Preparation

### Must-Read Papers

**Core Anthropic Papers:**
1. **"Constitutional AI: Harmlessness from AI Feedback"** (Bai et al., 2022)
   - The foundational CAI paper
   - Understand the full methodology and results

2. **"Training a Helpful and Harmless Assistant from Human Feedback"** (Bai et al., 2022)
   - Anthropic's RLHF approach
   - Comparison with CAI

3. **"Discovering Latent Knowledge in Language Models Without Supervision"** (Burns et al., 2022)
   - Contrast-Consistent Search (CCS)
   - Probing for model beliefs

4. **"Towards Monosemanticity: Decomposing Language Models With Dictionary Learning"** (Bricken et al., 2023)
   - Sparse autoencoders for interpretability
   - Feature decomposition

5. **"Scalable Oversight via Cooperative AI"** (Anthropic, 2023)
   - Using AI to help evaluate AI
   - Debate and amplification approaches

**Foundational Papers to Know:**
1. "Attention Is All You Need" (Vaswani et al., 2017)
2. "Language Models are Few-Shot Learners" (GPT-3, Brown et al., 2020)
3. "Training Language Models to Follow Instructions with Human Feedback" (InstructGPT, Ouyang et al., 2022)
4. "Red Teaming Language Models to Reduce Harms" (Ganguli et al., 2022)

### How to Discuss Safety Alignment

**Framework for Discussion:**
1. **Define the Problem:** Why is alignment hard? (specification gaming, mesa-optimization, value locking)
2. **Current Approaches:** RLHF, CAI, debate, recursive reward modeling
3. **Limitations:** Proxy misspecification, reward hacking, capability vs alignment tension
4. **Evaluation:** How do we measure alignment? (helpfulness, harmlessness, honesty)
5. **Future Directions:** Where should the field go? (mechanistic interpretability, scalable oversight)

**Key Questions to Think About:**
- What are the fundamental limits of RLHF?
- Can constitutional AI fully replace human oversight?
- How do we align models that are smarter than humans?
- What role does interpretability play in safety?

### Research Presentation Tips

**Structure Your Presentation:**
1. **Motivation (2-3 min):** Why does this problem matter?
2. **Background (3-4 min):** What's known, what's missing?
3. **Method (5-7 min):** Your approach — be precise
4. **Experiments (5-7 min):** Results, ablation studies, failure cases
5. **Implications (2-3 min):** What does this mean for safety?

**Anticipate Questions:**
- Why did you choose this approach over alternatives?
- What are the failure modes of your method?
- How does this scale to larger models?
- What's the next step after this result?

---

## Behavioral Questions

### Safety Focus

**Expected Questions:**
- "Why do you care about AI safety?"
- "What do you think is the most pressing AI risk?"
- "How would you balance model capability with safety?"
- "Describe a time you had to advocate for safety over speed."

**How to Answer Well:**
- Show genuine engagement with safety issues (not just rehearsed talking points)
- Demonstrate nuanced understanding (safety is not binary)
- Acknowledge trade-offs and uncertainties
- Reference specific research or incidents

### Responsible AI

**Expected Questions:**
- "How would you handle a request to deploy a model with known biases?"
- "What metrics would you use to evaluate model safety?"
- "How do you think about fairness in AI systems?"
- "Describe a project where you had to address ethical concerns."

**How to Answer Well:**
- Show structured thinking about evaluation
- Reference real cases and solutions
- Balance idealism with practical constraints
- Demonstrate collaborative approach to ethics

### Long-Term Thinking

**Expected Questions:**
- "Where do you see AI in 10 years?"
- "How should Anthropic prepare for AGI?"
- "What research directions will matter most in 5 years?"
- "How do you think about career impact on AI safety?"

**How to Answer Well:**
- Show you've thought long-term (not just next quarter)
- Connect personal goals to company mission
- Be realistic about timelines and uncertainty
- Demonstrate intellectual humility

### Team Collaboration

**Expected Questions:**
- "Describe a conflict you had with a collaborator and how you resolved it."
- "How do you give and receive feedback on research?"
- "Tell me about a time you mentored someone."
- "How do you handle disagreement about research methodology?"

**How to Answer Well:**
- Use concrete examples (STAR method)
- Show self-awareness about weaknesses
- Demonstrate growth and learning from failures
- Emphasize collaborative wins over individual credit

---

## Sample Questions & Answers

### Technical: Constitutional AI

**Q:** "Explain how Constitutional AI differs from standard RLHF. What are the trade-offs?"

**A:** "Constitutional AI replaces human preference labeling with AI-generated feedback guided by a constitution. The key trade-offs are:

**Advantages:**
- Scalability: AI feedback is essentially free compared to expensive human labeling
- Consistency: The same constitution provides stable guidance across all examples
- Transparency: The constitution can be publicly scrutinized and improved
- Control: Easy to update the constitution without retraining reward models

**Disadvantages:**
- Quality ceiling: AI feedback may miss subtle issues that humans catch
- Blind spots: The AI judge might share the same limitations as the model being trained
- Gaming: Models might learn to produce constitution-pleasing responses rather than genuinely harmless ones
- Evaluation challenge: Harder to measure alignment when the evaluator is also AI

**In practice,** Anthropic uses a hybrid approach: CAI for the bulk of training with targeted human feedback for edge cases and high-stakes scenarios."

### Technical: Interpretability

**Q:** "How would you determine whether a model is actually reasoning or just pattern-matching?"

**A:** "This is a central question in interpretability. Here are several approaches:

1. **Probing:** Train classifiers on intermediate representations to see if the model has internal representations consistent with reasoning steps

2. **Activation Patching:** Intervene on specific components to see if they causally contribute to reasoning (vs being epiphenomenal)

3. **Consistency Checks:** Test if the model's reasoning is consistent across paraphrases, irrelevant perturbations, and counterfactuals

4. **Circuit Analysis:** Identify the specific subgraph of computations responsible for a behavior — does it implement something like actual reasoning or a shallow heuristic?

5. **Feature Attribution:** Use integrated gradients or attention attribution to identify which inputs actually drive the output

The key insight is that we need causal methods (activation patching, circuit analysis) rather than purely correlational methods (probing, attention visualization) to distinguish genuine reasoning from pattern-matching."

### Coding: Transformer Implementation

**Q:** "Implement a simplified transformer block using PyTorch."

**A:** The solution would demonstrate understanding of:
- Multi-head attention (split heads, scaled dot-product, concatenation)
- Layer normalization (pre-norm vs post-norm)
- Feed-forward network (typically 4x expansion)
- Residual connections
- Dropout for regularization

### Behavioral: Safety

**Q:** "Your model is performing exceptionally well on benchmarks, but your safety evaluation reveals subtle biases. The product team wants to launch. What do you do?"

**A:** "I would take a structured approach:

1. **Quantify the risk:** How severe are the biases? In what contexts do they manifest? What's the potential harm?

2. **Evaluate mitigations:** Can we add guardrails, post-processing, or prompting strategies to reduce harm before launch?

3. **Propose a staged rollout:** Launch with restricted use cases, monitor closely, and gather data

4. **Communicate transparently:** Document known issues for users, provide usage guidelines

5. **Escalate if needed:** If risks are significant, I would escalate to leadership with a clear analysis

Safety decisions are rarely binary. The goal is to be rigorous about evaluation, creative about mitigations, and transparent about limitations — not to block progress, but to ensure responsible deployment."

---

## Resources & Further Reading

### Anthropic Publications
- Anthropic Research Blog: https://www.anthropic.com/research
- Anthropic Safety Papers: (link removed)

### Key Papers to Study
1. Constitutional AI: Harmlessness from AI Feedback
2. Training a Helpful and Harmless Assistant
3. Discovering Latent Knowledge in Language Models
4. Towards Monosemanticity
5. Red Teaming Language Models

### Recommended Books
- "Superintelligence" by Nick Bostrom
- "The Alignment Problem" by Brian Christian
- "Human Compatible" by Stuart Russell

### Practice Resources
- LeetCode (Medium/Hard — Python)
- PyTorch tutorials and documentation
- Hugging Face Transformers course
- Anthropic's Claude API documentation

---

*Good luck with your Anthropic interview! Remember that Anthropic values genuine engagement with safety issues, deep technical understanding, and collaborative research philosophy.*
