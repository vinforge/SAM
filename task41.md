Implementation Plan: Procedural Memory Engine for SAM
Objective: To design and implement a new, distinct memory component within SAM that allows users to create, store, edit, and invoke multi-step, goal-oriented procedures (e.g., "how-to" guides, checklists, personal workflows).
Phase 1: Backend Architecture & Data Model
Goal: To build the foundational data structures and storage mechanisms for Procedural Memory.
Task 1.1: Define the Procedure Data Class
Action: In a new file, sam/memory/procedural_memory.py, define a Pydantic or dataclass model for a single procedure. This structure is critical.
Generated python
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import uuid

class ProcedureStep(BaseModel):
    step_number: int
    description: str  # e.g., "Open the weekly sales report spreadsheet."
    details: Optional[str] = None  # e.g., "The file is located at /reports/sales.xlsx"
    expected_outcome: Optional[str] = None # e.g., "The spreadsheet is open and visible."

class Procedure(BaseModel):
    id: str = Field(default_factory=lambda: f"proc_{uuid.uuid4()}")
    name: str  # e.g., "Weekly Sales Report Workflow"
    description: str  # e.g., "A step-by-step guide to compile and send the weekly sales report."
    tags: List[str] = [] # e.g., ["reporting", "sales", "weekly"]
    steps: List[ProcedureStep]
    # Potentially add metadata like creation_date, last_used_date, etc.
Use code with caution.
Python
Task 1.2: Create the ProceduralMemoryStore
Action: In the same file, create a class ProceduralMemoryStore to manage all procedures. This will be a separate, dedicated store, not part of the main vector database.
Storage Mechanism: A simple JSON file or a dedicated SQLite table is perfect for this. We don't need complex vector search here; we need structured storage. Let's start with a JSON file for simplicity: sam/data/procedural_memory.json.
Core Methods:
add_procedure(procedure: Procedure): Adds a new procedure to the store.
get_procedure(procedure_id: str) -> Optional[Procedure]: Retrieves a procedure by its unique ID.
update_procedure(procedure_id: str, updated_data: Dict): Updates an existing procedure.
delete_procedure(procedure_id: str): Removes a procedure.
search_procedures(query: str) -> List[Procedure]: A simple text-based search that looks for the query in the name, description, and tags of all procedures.
Task 1.3: Secure the Procedural Memory Store
Action: Integrate the procedural_memory.json file with the SAM Secure Enclave. When SAM is locked, this file must be fully encrypted. When unlocked, its contents are decrypted into memory for use.
Rationale: Procedures can contain sensitive information about business processes or personal workflows, so they must be protected with the same rigor as all other SAM data.
Phase 2: Frontend UI in Memory Control Center
Goal: To provide a user-friendly interface for managing procedures.
Task 2.1: Create a New "Procedures" Tab
Action: In the Memory Control Center (Port 8501), add a new main tab next to "Memory Browser" and "Bulk Ingestion" called "🧠 Procedures".
Task 2.2: Design the Procedure Management UI
Action: The UI for this tab should have a two-panel layout:
Left Panel (Procedure List):
A search bar that calls the search_procedures() backend method.
A list of all existing procedures, showing their name and description.
A [+ New Procedure] button at the top.
Right Panel (Procedure Editor):
When a procedure is selected (or "New Procedure" is clicked), this panel becomes active.
It will display form fields for Name, Description, and Tags.
It will have a dynamic list for the Steps. Each step is a row with fields for Description, Details, etc. Buttons for [+ Add Step], [Move Up], [Move Down], and [Delete Step] are essential.
[Save Procedure] and [Delete Procedure] buttons at the bottom.
Task 2.3: Create Backend API Endpoints
Action: Create the necessary Flask/FastAPI endpoints to connect the UI to the ProceduralMemoryStore backend methods (add, get, update, delete, search). All endpoints must be protected by the @require_unlock security decorator.
Phase 3: Integration with SAM's Reasoning Engine
Goal: To make SAM aware of its new procedural memory so it can use it to answer questions and execute tasks.
Task 3.1: Enhance the "Meta-Router"
Action: This is the most critical integration step. We need to upgrade SAM's query analysis logic to recognize when a user is asking for a procedure.
Logic: Before performing a standard vector search, the new Meta-Router will analyze the query.
Generated python
def route_query(query: str):
    # A simple classifier using keywords
    if "how do I" in query or "steps to" in query or "workflow for" in query:
        return "procedural_search"
    else:
        return "knowledge_search" # The existing vector search
Use code with caution.
Python
Action: When procedural_search is triggered, SAM will call the procedural_store.search_procedures(query) method instead of the main vector store.
Task 3.2: Format the Procedure for LLM Context
Action: When a procedure is retrieved, it cannot be dumped into the LLM's context as raw JSON. Create a function to format it into clear, human-readable Markdown.
Generated code
# Example Markdown Output for LLM Context

You have retrieved the following procedure from your memory:

**Procedure Name:** Weekly Sales Report Workflow
**Description:** A step-by-step guide to compile and send the weekly sales report.
**Tags:** reporting, sales, weekly

**Steps:**
1. **Open the weekly sales report spreadsheet.**
   - Details: The file is located at /reports/sales.xlsx
2. **Refresh the data from the 'Data' tab.**
3. **Copy the summary chart and paste it into a new email.**
4. **Send the email to the 'sales-team@example.com' distribution list.**
Use code with caution.
Rationale: This structured formatting makes it incredibly easy for the LLM to understand and follow the procedure, or to explain it back to the user.
Task 3.3: Invocation and Task Execution
Action: Now, when a user asks, "SAM, how do I file the weekly sales report?", the following happens:
The Meta-Router identifies it as a procedural query.
It searches the ProceduralMemoryStore and finds the "Weekly Sales Report Workflow."
It formats the procedure into clean Markdown.
It injects this Markdown into the prompt for the LLM.
The LLM then generates the response: "To file the weekly sales report, you should follow these four steps. First, open the weekly sales report spreadsheet located at..."
✅ Definition of Done:
The Procedural Memory feature will be complete when:
✅ A user can create, view, edit, and delete multi-step procedures through a new, dedicated UI in the Memory Control Center.
✅ All created procedures are stored securely and are protected by the SAM Secure Enclave.
✅ When a user asks a "how-to" style question, SAM intelligently searches its Procedural Memory first.
✅ SAM can accurately present the steps of a retrieved procedure back to the user in a clear, formatted way.
✅ The entire feature is covered by unit and integration tests.
This implementation will give SAM a powerful new dimension of intelligence, enabling it to not just know things, but to do things based on learned, user-defined processes.