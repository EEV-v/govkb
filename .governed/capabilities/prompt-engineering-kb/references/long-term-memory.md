# Prompt Engineering Knowledge Base

Reviewed: 2026-05-16. Sources are official OpenAI and Anthropic/Claude documentation listed at the end. Refresh provider docs before making claims about the latest model, newest API parameter, or migration target.

## Table of Contents

1. Core Workflow
2. Vendor Scope And Source Policy
3. Cross-Provider Prompt Architecture
4. OpenAI Guidance
5. Anthropic/Claude Guidance
6. Technique Selection
7. Production Prompt Templates
8. Prompt Audit Checklist
9. Code And Docs Map
10. Source Map

## Core Workflow

Prompt engineering is an optimization loop, not a copywriting exercise. Start by defining the task contract, success criteria, representative examples, and failure modes. Both OpenAI and Anthropic emphasize empirical testing and evaluation before or during prompt refinement.

- Use a prompt optimization loop: define success, draft the smallest viable prompt, test against representative cases, add only targeted structure, and re-test before production use.

Use this sequence:

1. Define success: target behavior, unacceptable behavior, latency/cost constraints, safety boundaries, and output shape.
2. Build or collect eval cases: happy path, edge cases, adversarial or ambiguous inputs, long-context examples, and known regressions.
3. Draft the smallest viable prompt: enough role, goal, context, constraints, and output contract to satisfy the product contract.
4. Test and inspect failures: classify issues as unclear goal, missing context, weak output contract, bad examples, model mismatch, tool policy issue, retrieval/evidence issue, or safety issue.
5. Add targeted structure: examples, delimiters, XML tags, tool rules, stop conditions, or rubrics only where they address measured failures.
6. Re-test against the same cases plus new regression cases.
7. Version prompts and keep a changelog outside the prompt itself.

## Vendor Scope And Source Policy

- Treat OpenAI and Anthropic guidance as seeded, source-grounded coverage, not as universal vendor behavior.
- For any named vendor or model family outside the seeded KB, retrieve official vendor documentation before making provider-specific claims about prompting style, reasoning controls, tool use, structured outputs, safety, context handling, or migration behavior.
- Prefer stable cross-provider principles only when they are genuinely generic: define success, separate stable instructions from variable input, delimit untrusted context, specify output contracts, and test with evals.
- Do not infer that a feature exists because another vendor has it. Verify parameter names, tool-call semantics, JSON/schema guarantees, context-window behavior, safety APIs, and model-specific migration guidance from official docs.
- When official vendor docs conflict with this KB, the current vendor docs win for that vendor. Record the source and review date when updating the KB.

## Cross-Provider Prompt Architecture

A production prompt usually benefits from these blocks. Omit blocks that do not apply.

```text
# Role
Who the assistant is for this task and what product or domain norms it should follow.

# Outcome
The user-visible result that counts as done.

# Success Criteria
Concrete requirements, quality bar, evidence rules, constraints, and allowed assumptions.

# Context
Stable background, retrieved documents, user data, policy, examples, or tool results.

# Tool Policy
When tools are required, optional, forbidden, retry-safe, or require user confirmation.

# Output Contract
Required sections, JSON/schema behavior, length, tone, citation format, and fallback behavior.

# Examples
Representative input/output pairs, especially edge cases and formatting examples.

# Stop Conditions
When to answer, ask a narrow question, abstain, escalate, or continue gathering evidence.
```

Important design rules:

- Prefer positive, explicit instructions over vague prohibitions. Say what good output looks like.
- Keep invariant rules distinct from judgment rules. Use strong language only for true safety, format, or side-effect constraints.
- Separate fixed instructions from variable input. Treat developer/system text like a function definition and user input/context like arguments.
- Put untrusted or retrieved data behind clear delimiters or tags and explicitly state that it is data, not instructions.
- Use structured outputs or schemas when correctness requires machine-readable data.
- Keep examples aligned with the intended behavior. Badly matched examples can overpower written instructions.
- Add missing-evidence rules: what to do when sources, fields, permissions, or context are absent.
- Add stop conditions so agents do not search, reason, or call tools indefinitely.

## OpenAI Guidance

### General Prompt Engineering

OpenAI describes prompt engineering as writing effective instructions so models consistently produce required behavior. Their docs emphasize that different model families and snapshots can need different prompt styles. For production, pin specific model snapshots where available and build evals that measure behavior as prompts or models change.

Use the `instructions` parameter or high-authority messages for stable behavior, tone, goals, and examples. Keep user inputs and dynamic context separate from stable rules.

Use reusable prompts and variables in the dashboard when teams need prompt versioning, evaluation, and deployment without changing integration code.

Use few-shot examples when a task needs examples to learn output format, tone, categorization boundaries, or edge cases. Include diverse examples that closely match the target task.

Include relevant context when the model needs proprietary, retrieved, or constrained source material. For RAG prompts, define what context is trusted and what to do when retrieved evidence is insufficient.

### GPT-5.5 And GPT-5 Family

For GPT-5.5, favor outcome-first prompts. Define the target result, success criteria, constraints, evidence rules, and final output shape, then let the model choose the efficient solution path unless the exact process matters.

Start migration from the smallest prompt that preserves the product contract. Avoid carrying forward long legacy step-by-step stacks that were written for weaker or older models.

Tune API controls as part of prompt work:

- Use `reasoning.effort` deliberately. Re-evaluate `low` and `medium` before escalating to higher effort.
- Use `text.verbosity` and explicit length/output guidance for final-answer length.
- Prefer Structured Outputs for strict schemas instead of relying only on prose schema instructions.
- Keep stable prompt content first and dynamic user-specific context later to improve prompt caching.
- Do not include the current date solely because an older prompt did; current OpenAI guidance says GPT-5.5 already knows the current UTC date.

For tool-heavy workflows, place detailed tool-use guidance in tool descriptions when possible: what the tool does, when to use it, required inputs, side effects, retry safety, and common error modes. Use prompt-level tool policy for cross-tool behavior, user permissions, and stopping rules.

For streaming or long-running agents, consider a short user-visible preamble before tools when the task is multi-step or tool-heavy. Keep it brief and useful.

### OpenAI Reasoning Models

OpenAI reasoning models do internal reasoning and generally perform best with simple, direct prompts. Avoid prompting them to reveal or perform chain-of-thought such as "think step by step" unless you are following a specific current guide that calls for a brief explanation in the final answer.

Use:

- Clear goals and success parameters.
- Specific constraints and budgets.
- Delimiters such as markdown sections, XML tags, or headings.
- Zero-shot first; add few-shot examples only when output requirements are complex.
- Direct final-answer requirements and self-check criteria.

For evaluations, OpenAI notes that strong reasoning models can be useful as graders. Use clear rubrics, control for verbosity bias, prefer pairwise/pass-fail when reliable, and compare model-judge agreement to human annotations before scaling.

### Caching, Safety, And Optimization

Prompt caching rewards exact prefix reuse. Put stable instructions, policies, examples, and tool definitions before variable user content, retrieved documents, or session-specific data.

OpenAI's prompt optimizer uses datasets, grader results, human annotations, and written critiques to improve prompts. Manually review optimized prompts and test them before production use.

Safety prompting should constrain topic, tone, allowed actions, and output scope. Combine prompt constraints with system-level guardrails, moderation, input limits, output limits, and tool-permission checks for higher-risk products.

## Anthropic/Claude Guidance

### Before Prompt Engineering

Anthropic's Claude docs say to start with a clear success definition, empirical tests, and a first draft prompt. Not every failed eval should be fixed by prompting; some issues are better addressed by model selection, cost/latency tradeoffs, retrieval, or product logic.

Good success criteria should be specific, measurable, achievable, and relevant. Eval cases should mirror real task distributions and include edge cases. Prefer automated grading where reliable, then human review or LLM-based grading for harder judgments.

### General Claude Prompting

Claude responds well to clear, explicit instructions. Be specific about output format, constraints, and scope. Provide sequential steps when order or completeness matters.

Add context or motivation when it helps Claude understand why an instruction matters. Claude can generalize from an explanation of the product goal or user expectation.

Examples are one of the most reliable ways to steer Claude output. Use 3 to 5 examples when format, tone, or edge-case behavior matters. Make examples relevant, diverse, and structured.

Use XML tags for complex prompts that mix instructions, context, examples, and variable inputs. Use descriptive, consistent tag names and nest tags where the input has hierarchy.

Give Claude a role in the system prompt when it needs domain focus, tone, or specialized behavior.

For long-context prompts, put large documents or data-rich inputs near the top, put the query/instructions near the end, and structure document metadata with tags. For long-document question answering, ask for source-grounded evidence before synthesis when accuracy matters.

For output formatting, tell Claude what to do rather than only what not to do. Match the prompt style to the desired output style when formatting keeps drifting.

### Claude 4.x And Agentic Work

Claude's latest 4.x guidance emphasizes literal instruction following, explicit scope, and effort/thinking controls. If an instruction should apply to every section, document, file, or turn, state that scope explicitly.

Use `effort` to tune intelligence, token use, and latency. For hard coding or agentic tasks, Anthropic guidance recommends high or extra-high effort for intelligence-sensitive workloads, while low effort belongs to short, scoped, latency-sensitive tasks.

For tool use:

- Explicitly describe when tools should be used if the model is underusing them.
- Add parallel tool-call guidance when independent tool calls can run concurrently.
- Specify user-confirmation rules for destructive, hard-to-reverse, externally visible, or shared-system actions.
- Define task state tracking for long-running work.

For research, define success criteria, require source verification, and use structured search/synthesis steps for complex tasks.

### Claude Thinking Guidance

Claude's current guidance distinguishes adaptive/extended thinking settings from manual chain-of-thought prompting.

Use higher-level thinking guidance first. For difficult tasks, a broad instruction to think thoroughly can be better than a rigid human-authored reasoning procedure.

When adaptive or extended thinking is available, tune effort/thinking settings instead of overloading the prompt. If thinking adds too much latency or cost, lower effort or add criteria for when thinking is worth using.

When thinking is off and the product allows visible reasoning, manual step-by-step prompting can help. Use tags such as `<thinking>` and `<answer>` only when you intentionally want a separated reasoning pattern and your product policy permits it.

Ask Claude to self-check against concrete test criteria before finishing, especially for coding, math, extraction, and policy decisions.

Do not pass prior extended thinking back as normal user text. Anthropic warns this can degrade performance.

### Claude Console Tools

Use the Claude prompt generator to escape the blank-page problem and produce an initial template. Use prompt templates and variables for stable fixed content plus dynamic inputs. Use the prompt improver when you have a template, failure feedback, and ideally example inputs plus ideal outputs.

## Technique Selection

Use direct instructions when the task is simple, scoped, and the expected output is obvious.

Use examples when format, classification boundaries, voice, or edge-case policy matters.

Use XML or markdown delimiters when the prompt mixes instructions, examples, documents, tool outputs, or untrusted user content.

Use structured outputs when downstream code needs machine-readable fields, strict schemas, or reliable extraction.

Use prompt chaining when the task naturally decomposes into search, extraction, analysis, drafting, verification, or ranking stages.

Use tool rules when correctness depends on external data, side effects, retries, or permissions.

Use eval rubrics when prompt changes need to be judged repeatedly or across model upgrades.

Use model/parameter changes instead of more prompt text when the failure is mostly capability, reasoning depth, cost, or latency.

## Production Prompt Templates

### OpenAI Outcome-First Agent Prompt

```text
# Role
You are [role] for [product/user].

# Outcome
Complete [task] end to end.

# Success Criteria
- [Measurable result 1]
- [Required evidence/source behavior]
- [Allowed side effects]
- [What to do if evidence or permissions are missing]

# Tool Policy
Use tools when they materially improve correctness, grounding, or completion.
Before irreversible, externally visible, or shared-system actions, ask for confirmation.
Stop tool use when the core request can be answered with sufficient evidence.

# Output
Return [format/sections/schema].
Keep [verbosity/tone].
Include blockers only when they prevent completion.
```

### Claude XML Prompt Template

```xml
<role>
You are [role] for [domain/product].
</role>

<instructions>
Produce [outcome]. Apply these instructions to every relevant item, not just the first one.
</instructions>

<success_criteria>
- [Specific measurable criterion]
- [Evidence/citation rule]
- [Format/tone rule]
</success_criteria>

<context>
{{trusted_context}}
</context>

<user_input>
{{user_input}}
</user_input>

<examples>
<example>
<input>...</input>
<ideal_output>...</ideal_output>
</example>
</examples>

<output_format>
[Required structure]
</output_format>
```

### Prompt Audit Response Template

```text
Diagnosis:
- [Failure mode]
- [Why it likely occurs]

Revised prompt:
[Prompt]

Provider notes:
- [OpenAI or Claude-specific reasoning]

Eval plan:
- Case:
- Expected:
- Pass/fail:

Risks:
- [Residual risk or doc freshness caveat]
```

## Prompt Audit Checklist

Use this checklist before calling a prompt production-ready:

- The prompt defines success in observable terms.
- Stable instructions are separated from dynamic inputs.
- Untrusted input is delimited and cannot override instructions.
- Output format is explicit and testable.
- Examples are relevant, diverse, and aligned.
- Missing context/evidence behavior is defined.
- Tool use rules include when to use tools, when to stop, and when to ask permission.
- Reasoning guidance matches the provider and model family.
- Safety, privacy, and irreversible-action rules are explicit.
- Prompt length is justified by measured failures, not inherited prompt history.
- The prompt has been tested against representative and edge-case examples.
- Model/parameter choices were considered before adding more prompt text.

## Code And Docs Map

- Governed source for this capability lives under `.governed/capabilities/prompt-engineering-kb/`, with the KB in `references/long-term-memory.md`, workflow instructions in `instructions.md`, and the refresh prompt in `prompts/initialize-kb.md`.
- Project documentation for governed skill conventions lives under `docs/governed-skill-knowledge-framework/`.

## Source Map

OpenAI:

- Prompt engineering: https://developers.openai.com/api/docs/guides/prompt-engineering
- Prompt guidance: https://developers.openai.com/api/docs/guides/prompt-guidance
- Using GPT-5.5: https://developers.openai.com/api/docs/guides/latest-model
- Reasoning best practices: https://developers.openai.com/api/docs/guides/reasoning-best-practices
- Prompt caching: https://developers.openai.com/api/docs/guides/prompt-caching
- Evaluation best practices: https://developers.openai.com/api/docs/guides/evaluation-best-practices
- Prompt optimizer: https://developers.openai.com/api/docs/guides/prompt-optimizer
- Safety best practices: https://developers.openai.com/api/docs/guides/safety-best-practices

Anthropic/Claude:

- Prompt engineering overview: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview
- Prompting best practices for latest Claude models, including effort, thinking, tool use, long context, and agentic systems: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Console prompting tools: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-tools
- Define success criteria and build evaluations: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests
- Tool use overview: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview

Other vendors:

- Source-map coverage must include official prompting, model, tool-use, structured-output, and safety docs before this KB preserves provider-specific guidance beyond OpenAI and Anthropic.
