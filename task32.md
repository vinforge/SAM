
Excellent. Here is a comprehensive, phased implementation plan for the SAM Deep Research Engine.
This plan integrates the multi-step "Deep Research Agent" concept with the self-correcting "SELF-REFINE with Search" methodology. It is designed to be built on top of SAM's existing components (Agent Zero, Web Retrieval, Phase 5 Meta-Reasoning) and can be triggered as a specialized, user-initiated task.
Implementation Plan: The SAM Deep Research Engine
Overall Goal: To implement a new operational mode in SAM that allows it to conduct autonomous, multi-step, and critically self-correcting research campaigns, delivering a structured and well-sourced report as its final output.
Phase 1: The Core Research Loop & User-Facing Controls
Objective: To build the fundamental "Deconstruct -> Search -> Report" pipeline and the necessary UI controls to activate and monitor it.
Create the "Deep Research" Strategy Module:
Action: In a new module, sam/agents/strategies/deep_research.py, create an orchestrator class DeepResearchStrategy.
Functionality: This class will manage the state and sequence of the entire research task.
Implement the Activation Triggers:
Action (UI): Add a new [🔬 Conduct Deep Research] button next to the main chat input in the Secure Streamlit App (Port 8502).
Action (Backend): Create a new API endpoint that the UI button calls. This endpoint will instantiate the DeepResearchStrategy with the user's query and start the process.
Action (Keyword - Optional): Add logic to the main input handler to detect a prefix like "research:" and route the query to the Deep Research Engine.
Implement the Core Pipeline (Steps 1, 2, 5):
Step 1 (Deconstruct): The DeepResearchStrategy will make its first LLM call to deconstruct the user's query into a structured JSON object (main_topic, sub_questions, key_entities).
Step 2 (Initial Broad Search): The strategy will then command Agent Zero to use the CocoIndexTool to perform a broad search on the main_topic.
Step 5 (Final Report Generation): After all data is collected, the strategy will make a final LLM call using a dedicated "report generation" prompt template, providing all synthesized information as context. The output will be a structured Markdown report.
Implement Real-Time Status Feedback UI:
Action: The backend DeepResearchStrategy must maintain its current state (e.g., "STEP_1_DECONSTRUCTING", "STEP_2_SEARCHING").
Action: Create a new API endpoint, GET /research-status, that the frontend can poll.
Action (UI): When a research task is running, the chat interface should be replaced with a status display that periodically polls the status endpoint and shows live updates to the user (e.g., [2/5] Performing broad web search...).
Definition of Done for Phase 1: A user can type a query, click the "Deep Research" button, see real-time progress updates, and receive a basic, structured report at the end. The core scaffolding is in place.
Phase 2: "SELF-REFINE with Search" - The Critical Thinking Loop
Objective: To enhance the core pipeline with the critique-driven, self-correcting refinement loop. This phase implements the intelligence.
Integrate the Phase 5 Meta-Reasoning Engine as the "Critic":
Action: Create a new, specialized prompt template for the critique step. This prompt will leverage the capabilities of the Phase 5 Dimension Conflict Detector and meta-reasoning engine.
Prompt Goal: Instruct the LLM to act as a critical analyst and identify specific flaws (unverified claims, contradictions, missing perspectives) in a given text.
Implement the "Critique & Verification" Loop (New Steps 3a-3e):
Action: In the DeepResearchStrategy orchestrator, after the initial search (Step 2), insert the new refinement loop:
3a (Initial Synthesis): Take the raw search results and create a concise summary.
3b (Structured Critique): Feed this summary into the new "critic" prompt to get a list of identified flaws.
3c (Generate Verification Queries): Take the list of flaws and use another LLM call to transform them into specific, actionable search queries (e.g., "weakness: unverified performance claim" -> query: "official benchmark TPV system speed").
3d (Execute Verification Searches): Command Agent Zero to execute these new, highly targeted queries using the most appropriate tools from the Web Retrieval System.
3e (Refined Synthesis): Combine the initial summary with the results of the verification searches to create a new, more robust and fact-checked knowledge base for the rest of the research task.
Enhance the UI Status Feedback:
Action: Add new status messages to the real-time UI display to make this internal loop visible to the user:
[3/6] Critically analyzing initial findings...
[4/6] Performing verification searches for 3 identified claims...
Definition of Done for Phase 2: The research engine no longer just gathers information; it actively critiques and verifies its own findings mid-process, leading to a much more reliable final report.
Phase 3: Advanced Integration & AI-Initiated Triggers
Objective: To fully integrate the Deep Research Engine with SAM's other advanced systems and enable proactive, AI-initiated research tasks.
Integrate TPV for Loop & Cost Management:
Action: Wrap the entire research loop with the TPV Active Reasoning Control system.
Functionality: If the "Critique & Verification" loop (Phase 2) runs multiple times without significantly improving the quality of the synthesis (i.e., the TPV "progress" plateaus), the TPV controller will halt the process and move directly to the final report generation.
Benefit: This prevents infinite loops and runaway resource consumption, making the agent robust and efficient.
Integrate the Conversational Intelligence Engine:
Action: When a Deep Research task completes, the entire execution trace—the initial query, the deconstruction, the critiques, the verification queries, and the final report—should be automatically packaged and saved as a single, comprehensive thread in the Conversation History.
Benefit: Provides a perfect, auditable record of the research project.
Implement the AI-Initiated "Research Proposal" Trigger:
Action: Create a new background process as part of SAM's "sleep" cycle. This process will use the Phase 5 Dimension Conflict Detector to scan SAM's long-term knowledge base for unresolved conflicts.
Action: When a significant conflict is found, the system will auto-generate a "Research Proposal" and post it as a message on the "✉️ Messages from SAM" page.
Action (UI): This message will include a [🔬 Launch Deep Research Task] button that, when clicked by the user, initiates the Deep Research Engine with the context of the proposal.
Definition of Done for Phase 3: The Deep Research Engine is now a fully autonomous, self-regulating, and proactive component of the SAM ecosystem. It can be commanded by the user directly or can be deployed by SAM itself to resolve internal knowledge conflicts, with user approval.