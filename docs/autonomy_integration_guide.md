# SAM Autonomy Integration Guide

## 🔗 **Integrating Phase A with Main SAM System**

This guide explains how to integrate the newly implemented Goal & Motivation Engine with SAM's existing architecture.

---

## 📋 **Integration Steps**

### 1. **Update SAM's Main Imports**

Add autonomy components to SAM's main initialization:

```python
# In sam/__init__.py or main SAM initialization
from sam.autonomy import Goal, GoalStack, MotivationEngine, GoalSafetyValidator
```

### 2. **Initialize Autonomy Components in SAM Startup**

```python
# In start_sam.py or main SAM launcher
def initialize_autonomy_system():
    """Initialize SAM's autonomy components."""
    try:
        # Create safety validator
        safety_validator = GoalSafetyValidator()
        
        # Create goal stack with persistent storage
        goal_stack = GoalStack(
            db_path="memory/autonomy_goals.db",
            safety_validator=safety_validator
        )
        
        # Create motivation engine
        motivation_engine = MotivationEngine(
            goal_stack=goal_stack,
            safety_validator=safety_validator
        )
        
        # Update valid skill names from SOF registry
        from sam.autonomy.goals import update_valid_skill_names
        from sam.orchestration import get_sof_integration
        
        sof = get_sof_integration()
        if sof:
            skill_names = sof.get_available_skills()
            update_valid_skill_names(skill_names)
        
        logger.info("✅ SAM Autonomy System initialized successfully")
        return {
            'goal_stack': goal_stack,
            'motivation_engine': motivation_engine,
            'safety_validator': safety_validator
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize autonomy system: {e}")
        return None
```

### 3. **Integrate with SOF CoordinatorEngine**

Modify the CoordinatorEngine to call the MotivationEngine after plan execution:

```python
# In sam/orchestration/coordinator.py
class CoordinatorEngine:
    def __init__(self, ..., motivation_engine=None):
        # ... existing initialization ...
        self.motivation_engine = motivation_engine
    
    def execute_plan(self, plan: List[str], uif: SAM_UIF) -> ExecutionResult:
        # ... existing execution logic ...
        
        # After successful execution, generate autonomous goals
        if self.motivation_engine and uif.status == UIFStatus.SUCCESS:
            try:
                generated_goals = self.motivation_engine.generate_goals_from_uif(uif)
                if generated_goals:
                    uif.add_log_entry(f"Generated {len(generated_goals)} autonomous goals")
            except Exception as e:
                self.logger.warning(f"Goal generation failed: {e}")
        
        return result
```

### 4. **Add Autonomy Configuration**

Add autonomy settings to SAM's configuration:

```python
# In config/sam_config.json or config manager
{
    "autonomy": {
        "enabled": true,
        "goal_stack_db_path": "memory/autonomy_goals.db",
        "safety_validation": {
            "enabled": true,
            "max_goals_per_minute": 10,
            "max_goals_per_hour": 100,
            "enable_harmful_detection": true,
            "enable_loop_detection": true
        },
        "motivation_engine": {
            "enabled": true,
            "max_goals_per_analysis": 5,
            "enable_conflict_goals": true,
            "enable_inference_goals": true,
            "enable_learning_goals": true
        }
    }
}
```

---

## 🔧 **Phase B Preparation**

### **Required Modifications for Phase B:**

1. **DynamicPlanner Enhancement** (`sam/orchestration/planner.py`):
   ```python
   def create_plan(self, uif: SAM_UIF, mode: str = "user_focused") -> List[str]:
       # Add goal-informed planning mode
       if mode == "goal_informed" and self.goal_stack:
           top_goals = self.goal_stack.get_top_priority_goals(limit=1)
           if top_goals:
               # Add goal context to planning prompt
               goal_context = f"High-Priority Background Goal: {top_goals[0].description}"
               # Modify planning logic to include goal
   ```

2. **UI Integration Points**:
   - Memory Control Center: Add "Autonomy Dashboard" tab
   - Goal management interface
   - Manual goal trigger buttons
   - Statistics and monitoring displays

3. **Idle Time Processing**:
   - Background task scheduler
   - System load monitoring
   - Configurable idle thresholds

---

## 🛡️ **Safety Integration**

### **Emergency Controls:**

1. **Global Pause Mechanism**:
   ```python
   # Create persistent pause state
   AUTONOMY_PAUSE_FILE = "config/autonomy_paused.json"
   
   def is_autonomy_paused():
       try:
           with open(AUTONOMY_PAUSE_FILE, 'r') as f:
               data = json.load(f)
               return data.get('paused', False)
       except:
           return False
   
   def pause_autonomy():
       with open(AUTONOMY_PAUSE_FILE, 'w') as f:
           json.dump({'paused': True, 'timestamp': datetime.now().isoformat()}, f)
   ```

2. **Safety Monitoring**:
   - Real-time validation statistics
   - Alert system for suspicious patterns
   - Automatic pause triggers

---

## 📊 **Monitoring Integration**

### **Add to System Health Monitor**:

```python
# In services/system_health_monitor.py
def check_autonomy_health(self):
    """Check autonomy system health."""
    try:
        if not hasattr(self, 'goal_stack'):
            return {'status': 'disabled', 'message': 'Autonomy not initialized'}
        
        stats = self.goal_stack.get_statistics()
        safety_stats = self.safety_validator.get_validation_stats()
        
        return {
            'status': 'healthy',
            'active_goals': stats.get('goals_by_status', {}).get('pending', 0),
            'goals_validated': safety_stats.get('total_goals_validated', 0),
            'last_validation': safety_stats.get('last_validation')
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
```

---

## 🧪 **Testing Integration**

### **Add Autonomy Tests to SAM Test Suite**:

```python
# In main SAM test runner
def test_autonomy_integration():
    """Test autonomy system integration with main SAM."""
    # Test SOF integration
    # Test configuration loading
    # Test UI integration points
    # Test safety mechanisms
```

---

## 📝 **Logging Integration**

### **Add Autonomy Logs to SAM Logging**:

```python
# In SAM logging configuration
LOGGING_CONFIG = {
    'loggers': {
        'sam.autonomy': {
            'level': 'INFO',
            'handlers': ['file', 'console'],
            'propagate': False
        },
        'sam.autonomy.safety': {
            'level': 'WARNING',  # Higher level for safety events
            'handlers': ['file', 'console', 'audit'],
            'propagate': False
        }
    },
    'handlers': {
        'audit': {
            'class': 'logging.FileHandler',
            'filename': 'logs/autonomy_audit.log',
            'formatter': 'detailed'
        }
    }
}
```

---

## 🚀 **Deployment Checklist**

### **Before Enabling Autonomy:**

- [ ] Phase A components tested and validated
- [ ] Safety validator configured with appropriate patterns
- [ ] Database permissions and storage configured
- [ ] Logging and monitoring integrated
- [ ] Emergency pause mechanisms tested
- [ ] Configuration validated
- [ ] UI integration points prepared
- [ ] Documentation updated

### **Gradual Rollout Strategy:**

1. **Phase A**: Deploy foundation components (✅ Complete)
2. **Phase B-Lite**: Manual triggers only
3. **Phase B-Full**: Limited autonomous operation
4. **Phase C**: Full autonomy with monitoring

---

## 📞 **Support and Troubleshooting**

### **Common Integration Issues:**

1. **Database Permissions**: Ensure SAM can write to `memory/autonomy_goals.db`
2. **Skill Registry**: Verify SOF integration for skill name validation
3. **Configuration**: Check autonomy settings in SAM config
4. **Logging**: Verify log directory permissions for audit logs

### **Debugging Commands:**

```python
# Test autonomy components
python test_autonomy_phase_a.py

# Check goal stack status
from sam.autonomy import GoalStack
stack = GoalStack()
print(stack.get_statistics())

# Validate safety patterns
from sam.autonomy.safety import GoalSafetyValidator
validator = GoalSafetyValidator()
print(validator.get_validation_stats())
```

---

**Phase A integration is ready for deployment! 🎉**
