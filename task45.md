Implementation Plan: Integrating markitdown for Enhanced Procedural Formatting
Objective: To replace the manual string-based formatting of Procedure objects with the robust, self-contained markitdown library. This will improve the clarity and structure of the context provided to the LLM, resulting in higher-quality and more reliable chat responses.
Phase 1: Setup and Validation (The Foundation)
Goal: To safely add the new dependency and verify its basic functionality within the SAM project environment.
Task 1.1: Add Dependency:
Action: Add markitdown to the project's dependency file (requirements.txt or pyproject.toml).
Example (requirements.txt):
Generated code
# ... existing dependencies
markitdown==<latest_version>
Use code with caution.
Action: Run the installation command (e.g., pip install -r requirements.txt) in a clean virtual environment to ensure there are no conflicts.
Task 1.2: Create a Standalone Verification Script:
Action: Create a new, temporary script: scripts/verify_markitdown_integration.py. This script will not be part of the final application but is crucial for testing.
Purpose of the Script:
Import the Document, Heading, and Paragraph classes from markitdown.
Programmatically create a simple document object (e.g., a heading and a paragraph).
Call str(doc) to render it as a Markdown string.
Print the resulting string to the console.
Include a final "✅ Verification Successful" message if no errors occur.
Rationale: This confirms that the library is installed correctly and can be imported and used within SAM's environment before we modify any core application code.
Phase 2: Core Implementation (The Refactor)
Goal: To refactor the existing procedure formatting logic to use markitdown.
Task 2.1: Locate the Target Function:
Action: Identify the function responsible for converting a Procedure object into a string for the LLM. This is likely located in a file like sam/memory/procedural_integration.py and might be named _format_procedure_for_context or similar.
Task 2.2: Rewrite the Function using markitdown:
Action: Replace the entire body of the target function with the new, markitdown-based logic. The implementation should be similar to the detailed example provided previously, using Document, Heading, List, NumberedList, and Paragraph objects to build the document structure.
Key Logic:
Instantiate a Document() object.
Add the procedure's name, description, tags, and parameters using appropriate markitdown elements.
Create a NumberedList and loop through the procedure.steps, adding each step. Use nested List objects for details and expected_outcome to create a rich, hierarchical structure.
Return the final string by calling str(doc).
Phase 3: Testing and Integration Validation
Goal: To ensure the new formatting function works correctly with the rest of the Procedural Memory system.
Task 3.1: Update Unit Tests:
Action: Locate the unit tests for the old formatting function.
Action: Rewrite the tests to validate the new markitdown-based implementation.
Test Cases:
Test a simple procedure with only a name and steps.
Test a complex procedure that includes a description, tags, parameters, and steps with nested details.
Test an edge case with an empty procedure or a procedure with no steps.
Validation: The tests should assert that the output string is valid, well-formed Markdown that contains all the expected information.
Task 3.2: End-to-End Integration Test:
Action: Manually run SAM and perform a procedural query that you know will trigger the new formatting function (e.g., "How do I deploy the app safely?").
Action: Set a breakpoint or add a print() statement just before the prompt is sent to the LLM to inspect the generated Markdown context.
Action: Verify that the context is perfectly formatted and that the final chat response from the LLM is high-quality and accurately reflects the structured information.
Deliverables & Definition of Done:
This implementation is complete when:
✅ The markitdown library is successfully added as a project dependency.
✅ The old manual string-formatting function has been entirely replaced with the new, markitdown-based implementation.
✅ All relevant unit tests have been updated and are passing.
✅ An end-to-end test confirms that the generated context is well-structured and leads to a high-quality chat response.
✅ The temporary verification script (scripts/verify_markitdown_integration.py) can be safely deleted, as its purpose is fulfilled by the unit tests.
This plan provides a clear, low-risk path to significantly improving the quality and maintainability of a critical component in SAM's reasoning pipeline.