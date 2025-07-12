Phase 4: Synergy Integration & Self-Improving Planning
Project Goal: To interconnect the new A* Planner with SAM's advanced cognitive systems (TPV, Episodic Memory, and Meta-Reasoning) to create a self-regulating, self-improving, and self-aware planning agent.
Task 1: Integrate TPV for Planning Time Control (The "Governor")
Objective: To prevent the A* planner from spending too much time on planning for exceptionally complex or open-ended tasks.
1a. Identify the "Thinking" Loop: The primary target is the while not frontier.is_empty(): loop within the AStarPlanner class. This is the "planning thought process."
1b. Implement TPV Monitoring: For each node expanded in the A* loop, generate a "planning state" embedding. This might be an embedding of the action_history string. Feed this vector to the TPV monitor to get a "planning progress" score.
1c. Integrate the TPV Controller: Wrap the A* loop with the TPV controller. The should_continue() logic will now be based on the improvement of the best f_score in the frontier. If the best plan's score isn't improving (i.e., the planner is stagnating), the TPV controller will halt the planning process.
Outcome: The A* planner will now have a "patience" limit. It will stop planning and return the best plan found so far if it determines it's no longer making meaningful progress.
Task 2: Integrate Episodic Memory for Heuristic Enhancement (The "Experience Engine")
Objective: To make the planner's cost estimations more accurate by learning from past successes and failures.
2a. Modify the Heuristic Estimator: Enhance the HeuristicEstimator.estimate_cost_to_go() method.
2b. The "Experience" Query: Before returning the LLM's raw estimate, the function will query SAM's Phase 6 Episodic Memory. The query will be something like: "Find past tasks where the action [current_action] was used. What was the average success rate or step count?"
2c. Heuristic Adjustment: The estimator will then adjust the LLM's raw score based on historical data.
If past data shows the action search_web() often fails or leads to long paths, the h_score will be artificially increased.
If an action has historically been very successful, the score could be slightly decreased.
Outcome: The planner will become dynamically "biased" by its own experience. It will learn to prefer tools that have worked well in the past and be wary of those that have failed, making it smarter over time.
Task 3: Integrate Meta-Reasoning for Plan Validation (The "Sanity Check")
Objective: To add a final layer of qualitative, self-aware critique to the quantitatively optimal plan.
3a. Create a New Integration Point: After the AStarPlanner returns its optimal plan, but before the execution engine starts, insert a new step.
3b. The "Plan Review": Pass the entire proposed action sequence (e.g., ["search_web(...)","analyze_document(...)","generate_summary(...)"]) to the Phase 5 Reflective Meta-Reasoning Engine.
3c. The Critique: The Meta-Reasoning Engine will analyze the plan against its internal dimensions:
"Does this plan have a high risk_score?"
"Does it introduce any ethical concerns (ethical_considerations_score)?"
"Is there a conflict between the efficiency of this plan and its potential for error (utility-risk_conflict)?"
Outcome: The system can now present the user with a warning or ask for confirmation before executing a plan that is efficient but potentially risky. For example: Warning: This plan is the fastest but involves using an unverified web source. Do you wish to proceed?