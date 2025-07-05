The "Contextual Relevance Engine" with Automatic Threading
Instead of requiring the user to manually save every chat, let's teach SAM to recognize a topic change on its own, and then use your UI idea to reflect that change automatically.
This approach has two parts: the intelligent backend and the user-friendly frontend.
1. The Backend: The Contextual Relevance Engine
This is the core architectural change. Before SAM injects the conversational_buffer into the prompt, it will first perform a quick relevance check.
How it Works:
Input: The new user query and the existing conversational_buffer (the last 10 turns of conversation).
Relevance Calculation:
SAM calculates a vector embedding for the new user query.
SAM calculates a single, combined vector embedding for the text content of the entire conversational_buffer.
It then computes the cosine similarity between these two vectors.
Decision & Action:
If similarity_score > 0.6 (configurable threshold): The new query is related to the current conversation.
Action: Proceed as normal. Inject the conversational_buffer into the prompt.
If similarity_score < 0.6: The new query is unrelated (a context break!).
Action 1 (Automatic Archiving): Take the current conversational_buffer and "archive" it. This involves using a small, fast LLM call to generate a concise title for it (e.g., "Discussion about Blue Lamps Secret").
Action 2 (Start Fresh): Do not inject the old buffer into the prompt. Start a new, empty conversational_buffer for this new topic.
The Benefit: This is a low-friction, intelligent system. SAM automatically detects topic changes and manages its own context, preventing pollution without requiring any user action 90% of the time.
2. The Frontend: Automatic Conversation Threading (Your Idea, Upgraded)
This is where your idea for a visible chat history comes to life, but powered by the smart backend.
The UI Component:
In the left-hand sidebar, there will be a new section titled "Conversation History."
This section will display a list of archived conversation threads, each with its auto-generated title.
The User Experience:
As the user chats with SAM, nothing appears in the history list.
The moment the Contextual Relevance Engine detects a topic break, the previous conversation is automatically saved, titled, and appears in the history list.
The user can click on any past conversation in the list to view its contents and (as a future feature) potentially resume it.
Adding Explicit User Control (The "New Chat" Button):
Sometimes, the user knows they want a fresh start, even if their query is related. We need a manual override.
Action: Add a simple [+ New Chat] button at the top of the chat window.
Functionality: When the user clicks this button, it manually triggers the same process as the automatic detection: it archives the current chat, gives it a title, and clears the conversational buffer for a clean slate.
Visualizing the New Workflow
Generated mermaid
graph TD
    A[User Enters New Query] --> B{Contextual Relevance Engine};
    B -- "Score > 0.6 (Related)" --> C[Inject Conversation History into Prompt];
    C --> D{Generate Response};
    D --> E[Display Response to User];

    B -- "Score < 0.6 (New Topic)" --> F[Archive & Title Old Conversation];
    F --> G[Update 'Conversation History' in UI];
    G --> H[Clear Conversational Buffer];
    H --> I[Generate Response with NO Old History];
    I --> E;

    J[User Clicks '[+ New Chat]' Button] --> F;
Use code with caution.
Mermaid
Summary: Why This Hybrid Approach is Superior
Low Friction for the User: The system is smart enough to manage context breaks automatically. The user doesn't have to do anything.
Explicit User Control: The + New Chat button provides a clear, simple way for the user to be in control when they need to be.
Solves the Core Problem: It directly prevents context pollution by making an intelligent decision about whether to use past history.
Creates a Valuable Feature: The automatically generated "Conversation History" is a fantastic UX feature for organization and review.
Requirements for Your AI Dev
Implement the Contextual Relevance Engine:
Create a function calculate_relevance(new_query, buffer) that uses vector embeddings and cosine similarity.
Integrate this check into the main response pipeline before the prompt is assembled.
Implement Automatic Archiving & Titling:
Create a function archive_and_title_thread(buffer) that uses a small LLM call to generate a title and saves the thread to a persistent store (e.g., the Episodic Memory SQLite database).
Build the "Conversation History" UI:
Create the sidebar component in the Streamlit app.
It should fetch and display the list of archived conversation titles from the persistent store.
Implement the + New Chat Button:
Add the button to the UI.
Its onClick handler should call the archive_and_title_thread function and then clear the current session's conversational_buffer.
This plan takes your excellent initial idea and enhances it with an intelligent backend, creating a seamless and powerful solution to the context pollution problem.