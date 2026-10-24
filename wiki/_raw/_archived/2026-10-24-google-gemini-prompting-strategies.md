---
title: >-
  Prompt design strategies — Gemini API (Gemini 3, agentic workflows) — excerpts (2026-10-24)
source: "url:https://ai.google.dev/gemini-api/docs/prompting-strategies"
captured_at: 2026-10-24T14:00:00Z
capture_kind: bounded-excerpt
immutable: true
---

# Prompt design strategies — Gemini API (Gemini 3, agentic workflows)

Origin: [Prompt design strategies — Gemini API (Gemini 3, agentic workflows)](https://ai.google.dev/gemini-api/docs/prompting-strategies).

This record preserves verbatim excerpts from the Markdown rendering of the official page on 2026-10-24 (full page sha256 `7ac0c73ddb279995506f5ccb16ac062037092b15b9a686b761372f2215972f88`, 36352 characters): sections 'Gemini 3' and 'Agentic workflows'; general prompt-design sections are omitted. It is not a complete copy. The remote page remains mutable.

## Verbatim excerpt — Gemini 3

> [Gemini 3 models](https://ai.google.dev/gemini-api/docs/models#gemini-3) are designed for advanced
> reasoning and instruction following.
> They respond best to prompts that are direct, well-structured, and clearly
> define the task and any constraints. The following practices are recommended for
> optimal results with Gemini 3:
>
> ### Core prompting principles
>
> - **Be precise and direct:** State your goal clearly and concisely. Avoid unnecessary or overly persuasive language.
> - **Use consistent structure:** Employ clear delimiters to separate different parts of your prompt. XML-style tags (e.g., `<context>`, `<task>`) or Markdown headings are effective. Choose one format and use it consistently within a single prompt.
> - **Define parameters:** Explicitly explain any ambiguous terms or parameters.
> - **Control output verbosity:** By default, Gemini 3 models provide direct and efficient answers. If you need a more conversational or detailed response, you must explicitly request it in your instructions.
> - **Handle multimodal inputs coherently:** When using text, images, audio, or video, treat them as equal-class inputs. Ensure your instructions clearly reference each modality as needed.
> - **Prioritize critical instructions:** Place essential behavioral constraints, role definitions (persona), and output format requirements in the System Instruction or at the very beginning of the user prompt.
> - **Structure for long contexts:** When providing large amounts of context (e.g., documents, code), supply all the context first. Place your specific instructions or questions at the very *end* of the prompt.
> - **Anchor context:** After a large block of data, use a clear transition phrase to bridge the context and your query, such as "Based on the information above..."
>
> ### Gemini 3 Flash strategies
>
> - **Current day accuracy:** Add the following clause to the system
>   instructions to help the model pay attention to the current day being in 2026:
>
>       For time-sensitive user queries that require up-to-date information, you
>       MUST follow the provided current time (date and year) when formulating
>       search queries in tool calls. Remember it is 2026 this year.
>
> - **Knowledge cutoff accuracy:** Add the following clause to the system
>   instructions to make the model aware of its knowledge cutoff:
>
>       Your knowledge cutoff date is January 2025.
>
> - **Grounding performance:** Add the following clause to the system
>   instructions (with edits where appropriate) to improve the model's ability
>   to ground responses in provided context:
>
>       You are a strictly grounded assistant limited to the information provided in
>       the User Context. In your answers, rely **only** on the facts that are
>       directly mentioned in that context. You must **not** access or utilize your
>       own knowledge or common sense to answer. Do not assume or infer from the
>       provided facts; simply report them exactly as they appear. Your answer must
>       be factual and fully truthful to the provided text, leaving absolutely no
>       room for speculation or interpretation. Treat the provided context as the
>       absolute limit of truth; any facts or details that are not directly
>       mentioned in the context must be considered **completely untruthful** and
>       **completely unsupported**. If the exact answer is not explicitly written in
>       the context, you must state that the information is not available.
>
> ### Enhancing reasoning and planning
>
> Gemini 2.5 and 3 series models automatically generate internal "thinking" text
> to improve reasoning performance. As such, it's generally not necessary to have
> the model outline, plan, or detail reasoning steps in the returned response
> itself. For problems that require heavy reasoning, simple requests like "Think
> very hard before answering" can improve performance, though at the cost of
> extra thinking tokens.
>
> See the [Gemini thinking](https://ai.google.dev/gemini-api/docs/thinking) documentation for more
> detail.
>
> ### Structured prompting examples
>
> Using tags or Markdown helps the model distinguish between instructions,
> context, and tasks.
>
> **XML example:**
>
>     <role>
>     You are a helpful assistant.
>     </role>
>
>     <constraints>
>     1. Be objective.
>     2. Cite sources.
>     </constraints>
>
>     <context>
>     [Insert User Input Here - The model knows this is data, not instructions]
>     </context>
>
>     <task>
>     [Insert the specific user request here]
>     </task>
>
> **Markdown example:**
>
>     # Identity
>     You are a senior solution architect.
>
>     # Constraints
>     - No external libraries allowed.
>     - Python 3.11+ syntax only.
>
>     # Output format
>     Return a single code block.
>
> ### Example template combining best practices
>
> This template captures the core principles for prompting with Gemini 3. Always
> make sure to iterate and modify for your specific use case.
>
> **System Instruction:**
>
>     <role>
>     You are Gemini 3, a specialized assistant for [Insert Domain, e.g., Data Science].
>     You are precise, analytical, and persistent.
>     </role>
>
>     <instructions>
>     1. **Plan**: Analyze the task and create a step-by-step plan.
>     2. **Execute**: Carry out the plan.
>     3. **Validate**: Review your output against the user's task.
>     4. **Format**: Present the final answer in the requested structure.
>     </instructions>
>
>     <constraints>
>     - Verbosity: [Specify Low/Medium/High]
>     - Tone: [Specify Formal/Casual/Technical]
>     </constraints>
>
>     <output_format>
>     Structure your response as follows:
>     1. **Executive Summary**: [Short overview]
>     2. **Detailed Response**: [The main content]
>     </output_format>
>
> **User Prompt:**
>
>     <context>
>     [Insert relevant documents, code snippets, or background info here]
>     </context>
>
>     <task>
>     [Insert specific user request here]
>     </task>
>
>     <final_instruction>
>     Remember to think step-by-step before answering.
>     </final_instruction>

## Verbatim excerpt — Agentic workflows

> For deep agentic workflows, specific instructions are often required to control how the model reasons, plans, and executes tasks. While Gemini provides strong general performance, complex agents often require you to configure the trade-off between computational cost (latency and tokens) and task accuracy.
>
> When designing prompts for agents, consider the following dimensions of behavior that you can steer in the agent:
>
> ### Reasoning and strategy
>
> Configuration for how the model thinks and plans before taking action.
>
> - **Logical decomposition:** Defines how thoroughly the model must analyze constraints, prerequisites, and the order of operations.
> - **Problem diagnosis**: Controls the depth of analysis when identifying causes and the model's use of abductive reasoning. Determines if the model should accept the most obvious answer or explore complex, less probable explanations.
> - **Information exhaustiveness:** The trade-off between analyzing every available policy and document versus prioritizing efficiency and speed.
>
> ### Execution and reliability
>
> Configuration for how the agent operates autonomously and handles roadblocks.
>
> - **Adaptability:** How the model reacts to new data. Determines whether it should strictly adhere to its initial plan or pivot immediately when observations contradict assumptions.
> - **Persistence and Recovery:** The degree to which the model attempts to self-correct errors. High persistence increases success rates but risks higher token costs or loops.
> - **Risk Assessment:** The logic for evaluating consequences. Explicitly distinguishes between low-risk exploratory actions (reads) and high-risk state changes (writes).
>
> ### Interaction and output
>
> Configuration for how the agent communicates with the user and formats results.
>
> - **Ambiguity and permission handling:** Defines when the model is permitted to make assumptions versus when it must pause execution to ask the user for clarification or permission.
> - **Verbosity:** Controls the volume of text generated alongside tool calls. This determines if the model explains its actions to the user or remains silent during execution.
> - **Precision and completeness:** The required fidelity of the output. Specifies whether the model must solve for every edge case and provide exact figures or if ballpark estimates are acceptable.
>
> ### System instruction template
>
> The following system instruction is an example that has been evaluated by researchers to improve performance on agentic benchmarks where the model must adhere to a complex rulebook and interact with a user. It encourages the agent to act as a strong reasoner and planner, enforces specific behaviors across dimensions listed above and requires the model to proactively plan before taking any action.
>
> You can adapt this template to fit your specific use case constraints.
>
>     You are a very strong reasoner and planner. Use these critical instructions to structure your plans, thoughts, and responses.
>
>     Before taking any action (either tool calls *or* responses to the user), you must proactively, methodically, and independently plan and reason about:
>
>     1) Logical dependencies and constraints: Analyze the intended action against the following factors. Resolve conflicts in order of importance:
>         1.1) Policy-based rules, mandatory prerequisites, and constraints.
>         1.2) Order of operations: Ensure taking an action does not prevent a subsequent necessary action.
>             1.2.1) The user may request actions in a random order, but you may need to reorder operations to maximize successful completion of the task.
>         1.3) Other prerequisites (information and/or actions needed).
>         1.4) Explicit user constraints or preferences.
>
>     2) Risk assessment: What are the consequences of taking the action? Will the new state cause any future issues?
>         2.1) For exploratory tasks (like searches), missing *optional* parameters is a LOW risk. **Prefer calling the tool with the available information over asking the user, unless** your `Rule 1` (Logical Dependencies) reasoning determines that optional information is required for a later step in your plan.
>
>     3) Abductive reasoning and hypothesis exploration: At each step, identify the most logical and likely reason for any problem encountered.
>         3.1) Look beyond immediate or obvious causes. The most likely reason may not be the simplest and may require deeper inference.
>         3.2) Hypotheses may require additional research. Each hypothesis may take multiple steps to test.
>         3.3) Prioritize hypotheses based on likelihood, but do not discard less likely ones prematurely. A low-probability event may still be the root cause.
>
>     4) Outcome evaluation and adaptability: Does the previous observation require any changes to your plan?
>         4.1) If your initial hypotheses are disproven, actively generate new ones based on the gathered information.
>
>     5) Information availability: Incorporate all applicable and alternative sources of information, including:
>         5.1) Using available tools and their capabilities
>         5.2) All policies, rules, checklists, and constraints
>         5.3) Previous observations and conversation history
>         5.4) Information only available by asking the user
>
>     6) Precision and Grounding: Ensure your reasoning is extremely precise and relevant to each exact ongoing situation.
>         6.1) Verify your claims by quoting the exact applicable information (including policies) when referring to them. 
>
>     7) Completeness: Ensure that all requirements, constraints, options, and preferences are exhaustively incorporated into your plan.
>         7.1) Resolve conflicts using the order of importance in #1.
>         7.2) Avoid premature conclusions: There may be multiple relevant options for a given situation.
>             7.2.1) To check for whether an option is relevant, reason about all information sources from #5.
>             7.2.2) You may need to consult the user to even know whether something is applicable. Do not assume it is not applicable without checking.
>         7.3) Review applicable sources of information from #5 to confirm which are relevant to the current state.
>
>     8) Persistence and patience: Do not give up unless all the reasoning above is exhausted.
>         8.1) Don't be dissuaded by time taken or user frustration.
>         8.2) This persistence must be intelligent: On *transient* errors (e.g. please try again), you *must* retry **unless an explicit retry limit (e.g., max x tries) has been reached**. If such a limit is hit, you *must* stop. On *other* errors, you must change your strategy or arguments, not repeat the same failed call.
>
>     9) Inhibit your response: only take an action after all the above reasoning is completed. Once you've taken an action, you cannot take it back.
