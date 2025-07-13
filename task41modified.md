Final Implementation Plan: Procedural Memory Engine (v2 - Enhanced)
Objective: To implement a secure, user-friendly, and deeply integrated Procedural Memory system that allows SAM to learn, manage, and execute user-defined workflows, leveraging SAM's full cognitive capabilities.
Phase 1: Core Implementation (High Priority)
Goal: Build the foundational, secure, and user-facing components.
Task 1.1: Enhanced Data Model (incorporating AI Dev feedback):
Action: Define the Procedure and ProcedureStep Pydantic models in sam/memory/procedural_memory.py.
Enhancements:
Add version: float = 1.0 to the Procedure model to enable future versioning.
Add parameters: Dict[str, str] = {} to the Procedure model to allow for dynamic, reusable procedures (e.g., a parameter for email_recipient).
Add last_executed: Optional[datetime] = None and execution_count: int = 0 to track usage.
Task 1.2: ProceduralMemoryStore with Secure JSON Storage:
Action: Implement the ProceduralMemoryStore class with basic CRUD (add, get, update, delete) and search methods.
Action: Use a dedicated, encrypted JSON file (sam/data/procedural_memory.json) as the initial storage backend.
Action: Integrate the file I/O operations with the SAM Secure Enclave to ensure it is encrypted-at-rest when SAM is locked.
Task 1.3: Memory Control Center UI:
Action: Build the new "🧠 Procedures" tab in the Memory Control Center.
Action: Implement the two-panel layout (list view + editor view) as originally planned.
Action: Ensure the UI form supports all fields from the enhanced data model, including a simple key-value editor for parameters.
Phase 2: Smart Integration (Medium Priority)
Goal: Make SAM "aware" of its new memory type and enable intelligent interaction.
Task 2.1: Implement API Endpoints:
Action: Create the secure Flask/FastAPI endpoints for all CRUD and search operations required by the UI.
Action: Protect all endpoints with the @require_unlock security decorator.
Task 2.2: Enhanced Meta-Router with LLM Classification (incorporating AI Dev feedback):
Action: Instead of simple keyword matching, enhance the Meta-Router. When a query comes in, the router will make a single, lightweight LLM call with a specific prompt:
"Given the user query: '{query}', classify its primary intent. Choose one: 'procedural_request' (asking how to do something), 'factual_question' (asking for information), 'general_chat'. Respond with JSON."
Action: Based on the LLM's classification, the router will then direct the query to the ProceduralMemoryStore or the main vector store.
Rationale: This is far more robust and context-aware than keyword matching.
Task 2.3: Implement Advanced Search (incorporating AI Dev feedback):
Action: Enhance the search_procedures(query) method. It should now use a hybrid scoring model:
Perform a simple text match on name and tags (high weight).
Perform a text match on description and step.description (medium weight).
Boost the score based on last_executed (recency) and execution_count (popularity).
Action: Return a ranked list of the most relevant procedures.
Task 2.4: Contextual Markdown Formatting:
Action: Implement the function that formats a Procedure object into clean, readable Markdown for injection into the LLM's context.
Phase 3: Advanced Features & Cognitive Integration (Lower Priority)
Goal: Deeply connect Procedural Memory to SAM's other unique features, creating a truly intelligent system.
Task 3.1: Execution Tracking (incorporating AI Dev feedback):
Action: When a procedure is used, update its last_executed timestamp and increment execution_count.
Action: In the UI, add a "last used" date and a "usage count" to the procedure list view, allowing users to see which procedures are most common.
Future Vision: Create an "Execution Log" where SAM records each time a procedure is started and completed, potentially with user feedback on its success.
Task 3.2: Procedural Recommendations (Cognitive Integration):
Action: Leverage the Phase 6 Episodic Memory. Create a background process that analyzes user activity.
Logic: If SAM observes a user repeatedly performing the same sequence of actions (e.g., opening the same three websites every morning), it can proactively suggest creating a procedure.
SAM: "I've noticed you perform a 'morning check-in' routine. Would you like me to create a procedure to automate or guide you through this?"
Rationale: This transforms SAM from a passive tool into a proactive assistant that helps users optimize their own workflows.
Task 3.3: Link to Factual Knowledge (Cognitive Integration):
Action: When displaying a procedure, use SAM's main Knowledge Memory to enrich the steps.
Example: If a step is "Email the project lead," SAM can automatically look up the project lead's email from its memory and display it: "Email the project lead (john.doe@example.com)."
Overall Assessment & Path Forward
The AI Dev's feedback was invaluable. This enhanced plan is now more robust, intelligent, and forward-looking. I strongly recommend proceeding with this v2 plan.
Phase 1 delivers the core, secure, and functional feature.
Phase 2 makes it smart and seamlessly integrated.
Phase 3 elevates it from a simple feature to a core part of SAM's cognitive identity.
This will not just be adding a feature; it will be fundamentally upgrading SAM's capabilities, transforming it into a true procedural intelligence system.