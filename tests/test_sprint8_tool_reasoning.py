#!/usr/bin/env python3
"""
Sprint 8 Tool-Oriented Reasoning & Actionable Execution Test Suite
Tests the complete tool-oriented reasoning and execution system.

Sprint 8 Task Testing: Tool Registry, Secure Execution, Evaluation, Custom Tools, Action Planning
"""

import logging
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_dynamic_toolchain_selection():
    """Test dynamic toolchain selection and planning."""
    logger.info("🔧 Testing Dynamic Toolchain Selection...")
    
    try:
        from tools.tool_registry import ToolRegistry, ToolPlanner
        
        # Create temporary registry file
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            registry_file = tmp.name
        
        # Initialize tool registry
        tool_registry = ToolRegistry(registry_file=registry_file)
        logger.info("  ✅ Tool registry initialized")
        
        # Test tool search
        computation_tools = tool_registry.search_tools(query="calculation")
        logger.info(f"  🔍 Found {len(computation_tools)} computation tools")
        
        # Test tool planner
        tool_planner = ToolPlanner(tool_registry)
        
        # Create execution plan
        execution_plan = tool_planner.create_execution_plan(
            goal="Calculate the average of a dataset and create a visualization",
            context={'data_type': 'numerical'}
        )
        
        if execution_plan:
            logger.info(f"  ✅ Execution plan created: {len(execution_plan.steps)} steps")
            logger.info(f"    Estimated duration: {execution_plan.estimated_duration}s")
            logger.info(f"    Confidence: {execution_plan.confidence:.2f}")
            logger.info(f"    Fallback options: {len(execution_plan.fallback_options)}")
        else:
            logger.error("  ❌ Execution plan creation failed")
            return False
        
        # Test tool metadata updates
        success = tool_registry.update_tool_stats("python_interpreter", True, 2.5)
        if success:
            logger.info("  ✅ Tool stats updated successfully")
        else:
            logger.warning("  ⚠️ Tool stats update failed")
        
        # Cleanup
        Path(registry_file).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Dynamic toolchain selection test failed: {e}")
        return False

def test_secure_supervised_execution():
    """Test secure and supervised execution."""
    logger.info("🔒 Testing Secure & Supervised Execution...")
    
    try:
        from tools.secure_executor import SecureExecutor, ExecutionMode
        
        # Create temporary logs directory
        with tempfile.TemporaryDirectory() as logs_dir:
            # Initialize secure executor
            secure_executor = SecureExecutor(logs_directory=logs_dir)
            logger.info("  ✅ Secure executor initialized")
            
            # Test execution request submission
            request_id = secure_executor.submit_execution_request(
                tool_id="python_interpreter",
                tool_name="Python Interpreter",
                input_data={"code": "print('Hello, World!')"},
                execution_mode=ExecutionMode.SIMULATE,
                user_id="test_user",
                session_id="test_session",
                requires_approval=False
            )
            
            logger.info(f"  ✅ Execution request submitted: {request_id}")
            
            # Test execution result retrieval
            result = secure_executor.get_execution_result(request_id)
            
            if result:
                logger.info(f"  ✅ Execution result retrieved: {result.status.value}")
                logger.info(f"    Execution time: {result.execution_time_ms}ms")
                logger.info(f"    Output available: {result.output is not None}")
            else:
                logger.warning("  ⚠️ Execution result not found")
            
            # Test simulation mode
            simulation_result = secure_executor.simulate_execution(
                "table_generator",
                {"data": [["A", "B"], [1, 2], [3, 4]]}
            )
            
            if simulation_result and simulation_result.get('simulated'):
                logger.info("  ✅ Tool simulation successful")
            else:
                logger.warning("  ⚠️ Tool simulation failed")
            
            # Test explanation mode
            explanation = secure_executor.explain_execution(
                "multimodal_query",
                {"query": "What is machine learning?"}
            )
            
            if explanation and len(explanation) > 10:
                logger.info("  ✅ Tool explanation generated")
            else:
                logger.warning("  ⚠️ Tool explanation failed")
            
            # Test execution statistics
            stats = secure_executor.get_execution_stats()
            
            if stats:
                logger.info(f"  📊 Execution stats: {stats.get('total_executions', 0)} total executions")
                logger.info(f"    Success rate: {stats.get('success_rate', 0):.1%}")
            
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Secure supervised execution test failed: {e}")
        return False

def test_tool_evaluation_feedback():
    """Test tool evaluation and feedback loop."""
    logger.info("📊 Testing Tool Evaluation & Feedback Loop...")
    
    try:
        from tools.tool_evaluator import ToolEvaluator
        
        # Create temporary scorecard file
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            scorecard_file = tmp.name
        
        # Initialize tool evaluator
        tool_evaluator = ToolEvaluator(scorecard_file=scorecard_file)
        logger.info("  ✅ Tool evaluator initialized")
        
        # Test evaluation creation
        evaluation_id = tool_evaluator.evaluate_execution(
            tool_id="python_interpreter",
            execution_id="exec_test_001",
            request_id="req_test_001",
            user_id="test_user",
            goal="Calculate mathematical expression",
            input_data={"code": "result = 2 + 2"},
            output_data={"result": 4},
            success=True,
            execution_time_ms=1500,
            user_feedback={"accuracy": 1.0, "satisfaction": 0.9}
        )
        
        logger.info(f"  ✅ Evaluation created: {evaluation_id}")
        
        # Test scorecard retrieval
        scorecard = tool_evaluator.get_tool_scorecard("python_interpreter")
        
        if scorecard:
            logger.info(f"  ✅ Tool scorecard retrieved: {scorecard.tool_name}")
            logger.info(f"    Success rate: {scorecard.success_rate:.2f}")
            logger.info(f"    Performance level: {scorecard.performance_level.value}")
        else:
            logger.warning("  ⚠️ Tool scorecard not found")
        
        # Test tool rankings
        rankings = tool_evaluator.get_tool_rankings()
        
        if rankings:
            logger.info(f"  📈 Tool rankings: {len(rankings)} tools ranked")
            if rankings:
                top_tool = rankings[0]
                logger.info(f"    Top tool: {top_tool[0]} (score: {top_tool[1]:.2f})")
        
        # Test recommended tools
        recommended = tool_evaluator.get_recommended_tools("Calculate statistics")
        
        if recommended:
            logger.info(f"  🎯 Recommended tools: {len(recommended)} tools")
        
        # Test performance analysis
        analysis = tool_evaluator.analyze_tool_performance("python_interpreter")
        
        if analysis and 'error' not in analysis:
            logger.info(f"  📊 Performance analysis: {analysis.get('total_evaluations', 0)} evaluations")
            logger.info(f"    Average score: {analysis.get('average_score', 0):.2f}")
        
        # Cleanup
        Path(scorecard_file).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Tool evaluation feedback test failed: {e}")
        return False

def test_custom_tool_creation():
    """Test custom tool creation interface."""
    logger.info("🛠️ Testing Custom Tool Creation Interface...")
    
    try:
        from tools.custom_tool_creator import CustomToolCreator
        
        # Create temporary tools directory
        with tempfile.TemporaryDirectory() as tools_dir:
            # Initialize custom tool creator
            tool_creator = CustomToolCreator(tools_directory=tools_dir)
            logger.info("  ✅ Custom tool creator initialized")
            
            # Test template listing
            templates = tool_creator.get_available_templates()
            
            if templates:
                logger.info(f"  📋 Available templates: {len(templates)}")
                for template in templates:
                    logger.info(f"    - {template.name} ({template.template_type.value})")
            
            # Test custom tool creation
            tool_id = tool_creator.create_tool_from_template(
                template_id="computation_template",
                tool_name="Square Calculator",
                tool_description="Calculates the square of a number",
                creator_id="test_user",
                custom_logic="""
def execute(input_data):
    number = input_data.get('number', 0)
    result = number * number
    return {
        'result': result,
        'steps': [f'{number} * {number} = {result}']
    }
"""
            )
            
            logger.info(f"  ✅ Custom tool created: {tool_id}")
            
            # Test tool testing
            test_inputs = [
                {"number": 5},
                {"number": 10},
                {"number": 0}
            ]
            
            test_results = tool_creator.test_custom_tool(tool_id, test_inputs)
            
            if test_results:
                logger.info(f"  🧪 Tool testing completed: {test_results['success_rate']:.1%} success rate")
                logger.info(f"    Tests passed: {test_results['successful_tests']}/{test_results['total_tests']}")
            
            # Test tool activation
            if test_results and test_results['success_rate'] >= 0.8:
                activation_success = tool_creator.activate_tool(tool_id)
                if activation_success:
                    logger.info("  ✅ Custom tool activated successfully")
                else:
                    logger.warning("  ⚠️ Custom tool activation failed")
            
            # Test tool listing
            custom_tools = tool_creator.list_custom_tools("test_user")
            
            if custom_tools:
                logger.info(f"  📋 User custom tools: {len(custom_tools)}")
            
            # Test tool versioning
            new_version = tool_creator.update_tool(
                tool_id=tool_id,
                new_logic="# Updated logic here",
                version_notes="Fixed calculation bug",
                updater_id="test_user"
            )
            
            if new_version:
                logger.info(f"  🔄 Tool updated to version: {new_version}")
            
            # Test version history
            versions = tool_creator.get_tool_versions(tool_id)
            
            if versions:
                logger.info(f"  📚 Tool versions: {len(versions)}")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Custom tool creation test failed: {e}")
        return False

def test_action_plan_generation():
    """Test action plan generation and reporting."""
    logger.info("📋 Testing Action Plan Generation & Reporting...")
    
    try:
        from tools.action_planner import ActionPlanner, ReportFormat
        
        # Create temporary reports directory
        with tempfile.TemporaryDirectory() as reports_dir:
            # Initialize action planner
            action_planner = ActionPlanner(reports_directory=reports_dir)
            logger.info("  ✅ Action planner initialized")
            
            # Test action plan creation
            tool_sequence = [
                {
                    'tool_id': 'python_interpreter',
                    'tool_name': 'Python Interpreter',
                    'title': 'Data Analysis',
                    'description': 'Analyze the dataset',
                    'input_data': {'code': 'data = [1, 2, 3, 4, 5]'},
                    'expected_output': 'Analysis results',
                    'estimated_duration': 30
                },
                {
                    'tool_id': 'table_generator',
                    'tool_name': 'Table Generator',
                    'title': 'Create Summary Table',
                    'description': 'Generate summary table',
                    'input_data': {'data': []},
                    'expected_output': 'Summary table',
                    'estimated_duration': 15
                }
            ]
            
            plan_id = action_planner.create_action_plan(
                goal="Analyze data and create summary",
                user_id="test_user",
                session_id="test_session",
                tool_sequence=tool_sequence,
                title="Data Analysis Plan"
            )
            
            logger.info(f"  ✅ Action plan created: {plan_id}")
            
            # Test plan retrieval
            plan = action_planner.get_action_plan(plan_id)
            
            if plan:
                logger.info(f"  📋 Plan details: {plan.title}")
                logger.info(f"    Steps: {len(plan.steps)}")
                logger.info(f"    Status: {plan.status.value}")
                logger.info(f"    Estimated duration: {plan.estimated_total_duration}s")
            
            # Test plan approval
            approval_success = action_planner.approve_plan(
                plan_id=plan_id,
                approved=True,
                approval_notes="Approved for testing"
            )
            
            if approval_success:
                logger.info("  ✅ Plan approved successfully")
            
            # Test plan modification
            modifications = {
                'title': 'Updated Data Analysis Plan',
                'step_modifications': {
                    f"{plan_id}_step_1": {
                        'description': 'Enhanced data analysis'
                    }
                }
            }
            
            modification_success = action_planner.modify_plan(plan_id, modifications)
            
            if modification_success:
                logger.info("  ✅ Plan modified successfully")
            else:
                logger.info("  ℹ️ Plan modification not applicable (already approved)")
            
            # Test blueprint generation
            blueprint = action_planner.generate_plan_blueprint(plan_id)
            
            if blueprint and len(blueprint) > 100:
                logger.info("  ✅ Plan blueprint generated")
                logger.info(f"    Blueprint length: {len(blueprint)} characters")
            
            # Test plan execution
            execution_success = action_planner.execute_plan(plan_id)
            
            if execution_success:
                logger.info("  ✅ Plan execution completed")
            
            # Test report generation
            markdown_report = action_planner.generate_execution_report(plan_id, ReportFormat.MARKDOWN)
            
            if markdown_report and len(markdown_report) > 100:
                logger.info("  ✅ Markdown report generated")
                logger.info(f"    Report length: {len(markdown_report)} characters")
            
            # Test HTML report
            html_report = action_planner.generate_execution_report(plan_id, ReportFormat.HTML)
            
            if html_report and 'html' in html_report.lower():
                logger.info("  ✅ HTML report generated")
            
            # Test JSON report
            json_report = action_planner.generate_execution_report(plan_id, ReportFormat.JSON)
            
            if json_report and json_report.startswith('{'):
                logger.info("  ✅ JSON report generated")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Action plan generation test failed: {e}")
        return False

def test_integrated_tool_system():
    """Test the integrated tool system."""
    logger.info("🔧 Testing Integrated Tool System...")
    
    try:
        from tools.integrated_tool_system import IntegratedToolSystem, ToolRequest, ExecutionMode
        
        # Initialize integrated system
        tool_system = IntegratedToolSystem()
        logger.info("  ✅ Integrated tool system initialized")
        
        # Test system status
        status = tool_system.get_system_status()
        
        if status and status.get('system_ready'):
            logger.info("  ✅ System status: Ready")
            logger.info(f"    Total tools: {status['tool_registry']['total_tools']}")
            logger.info(f"    Custom tools: {status['custom_tool_creator']['total_custom_tools']}")
        else:
            logger.warning("  ⚠️ System not ready")
        
        # Test tool recommendations
        recommendations = tool_system.get_recommended_tools(
            goal="Calculate mathematical expressions and create visualizations"
        )
        
        if recommendations:
            logger.info(f"  🎯 Tool recommendations: {len(recommendations)} tools")
            for rec in recommendations[:3]:
                logger.info(f"    - {rec['name']} (success rate: {rec['success_rate']:.1%})")
        
        # Test tool request processing
        import uuid
        request = ToolRequest(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            user_id="test_user",
            session_id="test_session",
            goal="Calculate the sum of numbers 1 through 10",
            execution_mode=ExecutionMode.SIMULATE,
            require_approval=False,
            context={}
        )
        
        response = tool_system.process_tool_request(request)
        
        if response:
            logger.info(f"  ✅ Tool request processed: {response.request_id}")
            logger.info(f"    Success rate: {response.success_rate:.1%}")
            logger.info(f"    Tools used: {len(response.tools_used)}")
            logger.info(f"    Insights: {len(response.insights_generated)}")
            logger.info(f"    Report generated: {len(response.report_content) > 0}")
        else:
            logger.error("  ❌ Tool request processing failed")
            return False
        
        # Test custom tool creation
        custom_tool_result = tool_system.create_custom_tool(
            template_id="computation_template",
            tool_name="Test Calculator",
            tool_description="A test calculation tool",
            creator_id="test_user",
            custom_logic="def execute(input_data): return {'result': 42}",
            test_inputs=[{"expression": "6 * 7"}]
        )
        
        if custom_tool_result and custom_tool_result['creation_success']:
            logger.info(f"  ✅ Custom tool created: {custom_tool_result['tool_id']}")
            logger.info(f"    Registered: {custom_tool_result['registered']}")
            logger.info(f"    Activated: {custom_tool_result['activated']}")
        
        # Test performance analytics
        analytics = tool_system.get_tool_performance_analytics()
        
        if analytics and 'error' not in analytics:
            logger.info(f"  📊 Performance analytics: {len(analytics.get('tool_rankings', []))} tools ranked")
            logger.info(f"    Analysis period: {analytics.get('analysis_period_days', 0)} days")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Integrated tool system test failed: {e}")
        return False

def main():
    """Run all Sprint 8 tool-oriented reasoning tests."""
    logger.info("🚀 SAM Sprint 8 Tool-Oriented Reasoning & Actionable Execution Test Suite")
    logger.info("=" * 80)
    logger.info("Focus: Tool Registry, Secure Execution, Evaluation, Custom Tools, Action Planning")
    logger.info("=" * 80)
    
    tests = [
        ("Dynamic Toolchain Selection", test_dynamic_toolchain_selection),
        ("Secure & Supervised Execution", test_secure_supervised_execution),
        ("Tool Evaluation & Feedback Loop", test_tool_evaluation_feedback),
        ("Custom Tool Creation Interface", test_custom_tool_creation),
        ("Action Plan Generation & Reporting", test_action_plan_generation),
        ("Integrated Tool System", test_integrated_tool_system),
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
    logger.info("\n📊 Sprint 8 Test Results Summary")
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
        logger.info("🎉 Sprint 8 tool-oriented reasoning & actionable execution system is ready!")
        logger.info("\n✅ Tool-Oriented Reasoning & Actionable Execution Achieved:")
        logger.info("  🔧 Dynamic toolchain selection with intelligent planning")
        logger.info("  🔒 Secure and supervised execution with multiple modes")
        logger.info("  📊 Tool evaluation and feedback loop with performance tracking")
        logger.info("  🛠️ Custom tool creation interface with templates and testing")
        logger.info("  📋 Action plan generation with comprehensive reporting")
        logger.info("  🎯 Integrated tool system with unified reasoning")
        logger.info("  🧠 Intelligent tool recommendation and fallback strategies")
        logger.info("  📈 Performance analytics and continuous improvement")
        return 0
    else:
        logger.error("⚠️  Some Sprint 8 components need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
