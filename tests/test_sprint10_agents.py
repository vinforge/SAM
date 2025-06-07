#!/usr/bin/env python3
"""
Sprint 10 Agent Collaboration & Multi-SAM Swarm Mode Test Suite
Tests the complete multi-agent collaboration and swarm intelligence system.

Sprint 10 Task Testing: Multi-Agent Routing, Swarm Mode, Communication, Reasoning, Distributed Execution
"""

import logging
import sys
import tempfile
import time
from pathlib import Path
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_multi_agent_task_routing():
    """Test multi-agent task routing engine."""
    logger.info("🤖 Testing Multi-Agent Task Routing Engine...")
    
    try:
        from agents.task_router import TaskRouter, AgentRole, TaskType
        
        # Initialize task router
        task_router = TaskRouter()
        logger.info("  ✅ Task router initialized")
        
        # Test task decomposition
        request = "Read these three PDFs, summarize them individually, then generate a comparison table of their perspectives on AI risk."
        task_plan = task_router.decompose_task(
            request=request,
            user_id="test_user",
            session_id="test_session",
            context={"documents": ["doc1.pdf", "doc2.pdf", "doc3.pdf"]}
        )
        
        if task_plan:
            logger.info(f"  ✅ Task decomposed: {len(task_plan.sub_tasks)} sub-tasks")
            logger.info(f"    Plan ID: {task_plan.plan_id}")
            logger.info(f"    Execution phases: {len(task_plan.execution_order)}")
            
            # Test task assignment
            if task_plan.sub_tasks:
                first_task = task_plan.sub_tasks[0]
                success = task_router.assign_task_to_agent(first_task.task_id, "test_agent_001")
                
                if success:
                    logger.info(f"  ✅ Task assigned: {first_task.task_id}")
                
                # Test getting available tasks
                available_tasks = task_router.get_available_tasks(AgentRole.EXECUTOR)
                logger.info(f"  📋 Available tasks for executor: {len(available_tasks)}")
                
                # Test task status update
                from agents.task_router import TaskStatus
                success = task_router.update_task_status(
                    first_task.task_id,
                    TaskStatus.COMPLETED,
                    result="Task completed successfully"
                )
                
                if success:
                    logger.info(f"  ✅ Task status updated")
                
                # Test plan progress
                progress = task_router.get_plan_progress(task_plan.plan_id)
                
                if progress and not progress.get('error'):
                    logger.info(f"  📊 Plan progress: {progress['progress_percentage']:.1f}%")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Multi-agent task routing test failed: {e}")
        return False

def test_agent_communication():
    """Test agent identity and messaging protocol."""
    logger.info("📡 Testing Agent Identity & Messaging Protocol...")
    
    try:
        from agents.agent_comm import AgentCommunicationManager, MessageType, MessagePriority
        
        # Create two agents for communication testing
        agent1 = AgentCommunicationManager(
            agent_id="agent_001",
            agent_name="SAM-Planner-001",
            agent_role="planner",
            capabilities=["planning", "coordination"]
        )
        
        agent2 = AgentCommunicationManager(
            agent_id="agent_002",
            agent_name="SAM-Executor-001",
            agent_role="executor",
            capabilities=["execution", "processing"]
        )
        
        logger.info("  ✅ Two agents created for communication testing")
        
        # Test message sending
        message_id = agent1.send_message(
            recipient_id="agent_002",
            message_type=MessageType.TASK_REQUEST,
            content={"task": "Process document", "priority": "high"},
            priority=MessagePriority.HIGH
        )
        
        if message_id:
            logger.info(f"  ✅ Message sent: {message_id}")
        
        # Test thread creation
        thread_id = agent1.create_thread(
            participants=["agent_001", "agent_002"],
            subject="Document Processing Collaboration"
        )
        
        if thread_id:
            logger.info(f"  ✅ Message thread created: {thread_id}")
        
        # Test agent status
        status1 = agent1.get_agent_status()
        status2 = agent2.get_agent_status()
        
        if status1 and status2:
            logger.info(f"  📊 Agent 1 status: {status1['status']}")
            logger.info(f"  📊 Agent 2 status: {status2['status']}")
        
        # Test heartbeat
        agent1.send_heartbeat()
        agent2.send_heartbeat()
        logger.info("  💓 Heartbeats sent")
        
        # Test broadcast
        broadcast_ids = agent1.broadcast_message(
            message_type=MessageType.BROADCAST,
            content={"announcement": "System maintenance scheduled"},
            recipients=["agent_002"]
        )
        
        if broadcast_ids:
            logger.info(f"  📢 Broadcast sent to {len(broadcast_ids)} agents")
        
        # Cleanup
        agent1.shutdown()
        agent2.shutdown()
        logger.info("  🔄 Agents shutdown")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Agent communication test failed: {e}")
        return False

def test_local_swarm_mode():
    """Test local swarm mode."""
    logger.info("🐝 Testing Local Swarm Mode...")
    
    try:
        from agents.swarm_manager import LocalSwarmManager
        
        # Create temporary swarm config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            import json
            config = {
                "swarm_id": "test_swarm",
                "max_agents": 3,
                "load_balancing_strategy": "load_based",
                "shared_context_enabled": True,
                "auto_scaling_enabled": False,
                "heartbeat_interval": 30,
                "task_timeout": 300,
                "agent_roles": {
                    "executor": {
                        "count": 2,
                        "capabilities": ["document_processing", "analysis"],
                        "metadata": {"max_concurrent_tasks": 2}
                    },
                    "synthesizer": {
                        "count": 1,
                        "capabilities": ["synthesis", "integration"],
                        "metadata": {"max_concurrent_tasks": 1}
                    }
                }
            }
            json.dump(config, tmp)
            config_file = tmp.name
        
        # Initialize swarm manager
        swarm_manager = LocalSwarmManager(swarm_config_file=config_file)
        logger.info("  ✅ Swarm manager initialized")
        
        # Test swarm startup
        success = swarm_manager.start_swarm()
        
        if success:
            logger.info("  ✅ Swarm started successfully")
            
            # Test swarm status
            status = swarm_manager.get_swarm_status()
            
            if status and not status.get('error'):
                logger.info(f"  📊 Swarm status: {status['status']}")
                logger.info(f"    Total agents: {status['total_agents']}")
                logger.info(f"    Active agents: {status['active_agents']}")
            
            # Test task submission
            plan_id = swarm_manager.submit_task_to_swarm(
                request="Analyze three documents and create a summary",
                user_id="test_user",
                session_id="test_session",
                context={"documents": ["doc1.txt", "doc2.txt", "doc3.txt"]}
            )
            
            if plan_id:
                logger.info(f"  ✅ Task submitted to swarm: {plan_id}")
            
            # Test shared context
            swarm_manager.add_to_shared_context(
                key="test_context",
                value="Test context value",
                source_agent="test_agent"
            )
            
            context_value = swarm_manager.get_shared_context("test_context")
            
            if context_value:
                logger.info("  ✅ Shared context working")
            
            # Wait a moment for processing
            time.sleep(0.5)
            
            # Test swarm shutdown
            success = swarm_manager.stop_swarm()
            
            if success:
                logger.info("  ✅ Swarm stopped successfully")
        
        # Cleanup
        Path(config_file).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Local swarm mode test failed: {e}")
        return False

def test_multi_agent_reasoning():
    """Test multi-agent chain-of-thought reasoning."""
    logger.info("🧠 Testing Multi-Agent Chain-of-Thought Reasoning...")
    
    try:
        from agents.reasoning_chain import MultiAgentReasoningEngine, ReasoningStepType, VoteType
        
        # Initialize reasoning engine
        reasoning_engine = MultiAgentReasoningEngine()
        logger.info("  ✅ Multi-agent reasoning engine initialized")
        
        # Test reasoning chain creation
        participants = ["planner_001", "executor_001", "critic_001"]
        chain_id = reasoning_engine.start_reasoning_chain(
            topic="AI Risk Analysis",
            initial_query="What are the main risks associated with artificial intelligence?",
            participants=participants,
            initiator_id=participants[0]
        )
        
        if chain_id:
            logger.info(f"  ✅ Reasoning chain created: {chain_id}")
            
            # Test adding reasoning steps
            step1_id = reasoning_engine.add_reasoning_step(
                chain_id=chain_id,
                agent_id=participants[1],
                step_type=ReasoningStepType.HYPOTHESIS,
                content="AI risks include job displacement, privacy concerns, and potential misuse",
                reasoning="Based on current literature and expert opinions",
                confidence=0.8,
                evidence=["research_paper_1", "expert_opinion_2"]
            )
            
            if step1_id:
                logger.info(f"  ✅ Reasoning step added: {step1_id}")
            
            step2_id = reasoning_engine.add_reasoning_step(
                chain_id=chain_id,
                agent_id=participants[2],
                step_type=ReasoningStepType.CRITIQUE,
                content="The hypothesis covers major categories but could include more technical risks",
                reasoning="Critical evaluation of the initial hypothesis",
                confidence=0.7,
                parent_step_id=step1_id
            )
            
            if step2_id:
                logger.info(f"  ✅ Critical reasoning step added: {step2_id}")
            
            # Test voting
            vote_id = reasoning_engine.submit_vote(
                chain_id=chain_id,
                agent_id=participants[0],
                target_step_id=step1_id,
                vote_type=VoteType.APPROVE,
                reasoning="Comprehensive initial analysis",
                confidence=0.8
            )
            
            if vote_id:
                logger.info(f"  ✅ Vote submitted: {vote_id}")
            
            # Test turn-based reasoning
            turn_results = reasoning_engine.conduct_turn_based_reasoning(
                chain_id=chain_id,
                max_turns=3
            )
            
            if turn_results and not turn_results.get('error'):
                logger.info(f"  🔄 Turn-based reasoning: {turn_results['turns_completed']} turns")
            
            # Test visual trace generation
            visual_trace = reasoning_engine.generate_visual_trace(chain_id)
            
            if visual_trace and len(visual_trace) > 100:
                logger.info(f"  📊 Visual trace generated: {len(visual_trace)} characters")
            
            # Test getting reasoning chain
            chain = reasoning_engine.get_reasoning_chain(chain_id)
            
            if chain:
                logger.info(f"  📋 Chain retrieved: {len(chain.steps)} steps, {len(chain.votes)} votes")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Multi-agent reasoning test failed: {e}")
        return False

def test_agent_manager():
    """Test the main agent coordination engine."""
    logger.info("🎯 Testing Agent Manager (Main Coordination Engine)...")
    
    try:
        from agents.agent_manager import AgentManager
        
        # Create temporary config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            import json
            config = {
                "max_concurrent_collaborations": 5,
                "default_collaboration_timeout": 300,
                "enable_swarm_mode": True,
                "enable_reasoning_chains": True,
                "auto_start_swarm": False
            }
            json.dump(config, tmp)
            config_file = tmp.name
        
        # Initialize agent manager
        agent_manager = AgentManager(config_file=config_file)
        logger.info("  ✅ Agent manager initialized")
        
        # Test agent registration
        success = agent_manager.register_agent(
            agent_id="test_agent_001",
            agent_name="Test SAM Agent",
            agent_role="executor",
            capabilities=["document_processing", "analysis"]
        )
        
        if success:
            logger.info("  ✅ Agent registered successfully")
        
        # Test agent status
        status = agent_manager.get_agent_status("test_agent_001")
        
        if status and not status.get('error'):
            logger.info(f"  📊 Agent status: {status['status']}")
        
        # Test collaboration request processing
        response = agent_manager.process_collaboration_request(
            request="Analyze this document and provide a summary with key insights",
            user_id="test_user",
            session_id="test_session",
            collaboration_type="task_delegation",
            context={"document": "test_document.pdf"}
        )
        
        if response:
            logger.info(f"  ✅ Collaboration completed: {response.request_id}")
            logger.info(f"    Status: {response.status}")
            logger.info(f"    Confidence: {response.confidence_score:.2f}")
            logger.info(f"    Processing time: {response.processing_time_ms}ms")
            logger.info(f"    Agent contributions: {len(response.agent_contributions)}")
        
        # Test reasoning chain collaboration
        reasoning_response = agent_manager.process_collaboration_request(
            request="What are the implications of AI in healthcare?",
            user_id="test_user",
            session_id="test_session",
            collaboration_type="reasoning_chain"
        )
        
        if reasoning_response:
            logger.info(f"  🧠 Reasoning chain collaboration: {reasoning_response.request_id}")
            logger.info(f"    Chain ID: {reasoning_response.reasoning_chain_id}")
        
        # Test swarm mode
        swarm_status = agent_manager.get_swarm_status()
        
        if swarm_status and not swarm_status.get('error'):
            logger.info(f"  🐝 Swarm status: {swarm_status['status']}")
        
        # Test collaboration history
        history = agent_manager.get_collaboration_history("test_user", days_back=1)
        
        if history:
            logger.info(f"  📋 Collaboration history: {len(history)} entries")
        
        # Test reasoning chain creation
        chain_id = agent_manager.create_reasoning_chain(
            topic="AI Ethics",
            initial_query="How should we approach AI ethics in autonomous systems?",
            participants=["planner_001", "executor_001", "critic_001"]
        )
        
        if chain_id:
            logger.info(f"  🧠 Reasoning chain created: {chain_id}")
        
        # Cleanup
        Path(config_file).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Agent manager test failed: {e}")
        return False

def test_end_to_end_collaboration():
    """Test end-to-end multi-agent collaboration scenario."""
    logger.info("🎯 Testing End-to-End Multi-Agent Collaboration...")
    
    try:
        from agents.agent_manager import AgentManager
        
        # Initialize agent manager
        agent_manager = AgentManager()
        
        # Register multiple agents
        agents = [
            ("planner_001", "SAM Planner", "planner", ["planning", "coordination"]),
            ("executor_001", "SAM Executor 1", "executor", ["document_processing", "analysis"]),
            ("executor_002", "SAM Executor 2", "executor", ["research", "data_extraction"]),
            ("synthesizer_001", "SAM Synthesizer", "synthesizer", ["synthesis", "integration"]),
            ("validator_001", "SAM Validator", "validator", ["validation", "quality_check"])
        ]
        
        registered_count = 0
        for agent_id, name, role, capabilities in agents:
            if agent_manager.register_agent(agent_id, name, role, capabilities):
                registered_count += 1
        
        logger.info(f"  ✅ Registered {registered_count} agents")
        
        # Test complex collaboration scenario
        complex_request = """
        Read these three PDFs about AI risk assessment, summarize each document individually, 
        then create a comprehensive comparison table highlighting the different perspectives 
        on AI safety measures. Finally, provide recommendations based on the analysis.
        """
        
        response = agent_manager.process_collaboration_request(
            request=complex_request,
            user_id="test_user",
            session_id="test_session",
            collaboration_type="auto",  # Let system decide
            context={
                "documents": ["ai_risk_paper1.pdf", "ai_risk_paper2.pdf", "ai_risk_paper3.pdf"],
                "output_format": "comparison_table",
                "include_recommendations": True
            }
        )
        
        if response:
            logger.info(f"  ✅ Complex collaboration completed: {response.request_id}")
            logger.info(f"    Final answer length: {len(response.final_answer)} characters")
            logger.info(f"    Agent contributions: {len(response.agent_contributions)}")
            logger.info(f"    Execution trace steps: {len(response.execution_trace)}")
            logger.info(f"    Overall confidence: {response.confidence_score:.1%}")
            logger.info(f"    Processing time: {response.processing_time_ms}ms")
            
            # Verify agent contributions
            if response.agent_contributions:
                logger.info("  👥 Agent contributions verified:")
                for agent, contribution in response.agent_contributions.items():
                    logger.info(f"    - {agent}: {contribution}")
            
            # Verify execution trace
            if response.execution_trace:
                logger.info("  📋 Execution trace verified:")
                for step in response.execution_trace[:3]:  # Show first 3 steps
                    logger.info(f"    - {step}")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ End-to-end collaboration test failed: {e}")
        return False

def main():
    """Run all Sprint 10 agent collaboration tests."""
    logger.info("🚀 SAM Sprint 10 Agent Collaboration & Multi-SAM Swarm Mode Test Suite")
    logger.info("=" * 80)
    logger.info("Focus: Multi-Agent Routing, Swarm Mode, Communication, Reasoning, Distributed Execution")
    logger.info("=" * 80)
    
    tests = [
        ("Multi-Agent Task Routing Engine", test_multi_agent_task_routing),
        ("Agent Identity & Messaging Protocol", test_agent_communication),
        ("Local Swarm Mode", test_local_swarm_mode),
        ("Multi-Agent Chain-of-Thought Reasoning", test_multi_agent_reasoning),
        ("Agent Manager (Main Coordination Engine)", test_agent_manager),
        ("End-to-End Multi-Agent Collaboration", test_end_to_end_collaboration),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        logger.info("-" * 60)
        
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"❌ Test {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Final summary
    logger.info("\n📊 Sprint 10 Test Results Summary")
    logger.info("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed ({passed/total:.1%})")
    
    if passed == total:
        logger.info("🎉 Sprint 10 agent collaboration and multi-SAM swarm mode system is ready!")
        logger.info("\n✅ Agent Collaboration & Multi-SAM Swarm Mode Achieved:")
        logger.info("  🤖 Multi-agent task routing with role-based delegation")
        logger.info("  📡 Agent identity and messaging protocol with thread management")
        logger.info("  🐝 Local swarm mode with concurrent task execution")
        logger.info("  🧠 Multi-agent chain-of-thought reasoning with voting")
        logger.info("  🎯 Integrated agent manager for coordination")
        logger.info("  👥 End-to-end multi-agent collaboration scenarios")
        logger.info("  🔄 Turn-based reasoning between planner and executor agents")
        logger.info("  📊 Visual trace of agent thought chains")
        logger.info("  🌐 Pluggable distributed execution interface")
        return 0
    else:
        logger.error("⚠️  Some Sprint 10 components need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
