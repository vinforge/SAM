# Technical Web Search Flow Reference

## Flow States & Transitions

```
CHAT_QUERY → CONFIDENCE_CHECK → ESCALATION_TRIGGER → USER_DECISION → WEB_SEARCH → QUARANTINE_SAVE → VETTING_DISPLAY → APPROVAL → KNOWLEDGE_INTEGRATION → ENHANCED_RESPONSE
```

## Critical Integration Points

### 1. Chat → Confidence Assessment
**Trigger**: `web_ui/app.py:chat()` → `reasoning/confidence_assessor.py:assess_retrieval_quality()`
**Condition**: `assessment.status == "NOT_CONFIDENT"`
**Output**: `{'type': 'web_search_escalation'}`

### 2. UI Escalation → Web Search Trigger
**Trigger**: User clicks "Yes, Search Online"
**Endpoint**: `POST /api/trigger-web-search`
**Handler**: `web_ui/app.py:trigger_web_search()`

### 3. Web Search → Quarantine Save
**Function**: `intelligent_web_system.process_query(search_query)`
**Save**: `save_intelligent_web_to_quarantine(result, search_query)`
**File**: `quarantine/intelligent_web_YYYYMMDD_HHMMSS_[hash].json`

### 4. Quarantine → Vetting Display
**Load**: `secure_streamlit_app.py:load_quarantined_content()`
**Display**: Content Vetting Dashboard
**Filter**: Skip metadata files, process `intelligent_web_*` files

### 5. Vetting → Approval
**Process**: Manual review via vetting dashboard
**Action**: "Vet All Content" or individual approval
**Move**: `quarantine/` → `approved/` or `archive/`

### 6. Approval → Knowledge Integration
**Process**: `knowledge_consolidation/` modules
**Integration**: Vector database + memory store
**Status**: ❓ NEEDS VERIFICATION

### 7. Knowledge → Enhanced Response
**Process**: Re-query with enhanced knowledge base
**Output**: Updated response with web information
**Status**: ❓ NEEDS VERIFICATION

## Current Issue Analysis

### Problem: Web Search Results Not Appearing in Vetting Page

**Symptoms**:
- Chat web searches execute successfully
- No new content appears in "Content Awaiting Analysis"
- Vetting statistics missing/incorrect
- Security analysis dashboard empty

**Potential Causes**:
1. **Quarantine Save Failure**: `save_intelligent_web_to_quarantine()` not called
2. **File Path Issues**: Wrong directory or permissions
3. **Load Function Issues**: `load_quarantined_content()` not finding files
4. **UI State Issues**: Streamlit not refreshing/detecting new files
5. **Process Isolation**: Chat and vetting running in different contexts

## Diagnostic Checkpoints

### Checkpoint 1: Verify Web Search Execution
```python
# Check if web search actually executes
POST /api/trigger-web-search
{
    "search_query": "test query",
    "original_query": "test query"
}
```

### Checkpoint 2: Verify Quarantine Save
```bash
# Check if files are created
ls -la quarantine/intelligent_web_*
```

### Checkpoint 3: Verify Load Function
```python
# Test load function directly
from secure_streamlit_app import load_quarantined_content
content = load_quarantined_content()
print(f"Loaded {len(content)} items")
```

### Checkpoint 4: Verify UI Refresh
```python
# Check if Streamlit detects file changes
st.rerun()  # Force refresh
```

## Integration Verification Commands

### Test Complete Flow
```python
# 1. Trigger web search
result = intelligent_web_system.process_query("test query")

# 2. Save to quarantine
save_intelligent_web_to_quarantine(result, "test query")

# 3. Verify file exists
assert Path("quarantine/intelligent_web_*.json").exists()

# 4. Load in vetting interface
content = load_quarantined_content()
assert len(content) > 0

# 5. Check vetting statistics
status = get_vetting_status()
assert status['quarantine_files'] > 0
```

## Missing Statistics Investigation

**Expected Vetting Statistics**:
- Critical Risk Counter
- High Risk Counter  
- Average Credibility Score
- Average Purity Score
- Security Status Indicators

**Potential Issues**:
1. **No Content to Analyze**: Empty quarantine directory
2. **Analysis Function Broken**: Security analysis not running
3. **Statistics Calculation Error**: Aggregation functions failing
4. **UI Display Issues**: Statistics calculated but not shown

## File System State Check

### Required Directories
```bash
quarantine/          # Incoming content
approved/           # Vetted content
archive/            # Processed content
vetted/             # Alternative vetted location
```

### Required Files Pattern
```bash
quarantine/intelligent_web_YYYYMMDD_HHMMSS_[hash].json
quarantine/scrapy_search_YYYYMMDD_HHMMSS_[hash].json
```

## Process Flow Verification

### Chat Process (Port 5001)
```python
# web_ui/app.py
@app.route('/api/trigger-web-search')
def trigger_web_search():
    # Execute web search
    # Save to quarantine
    # Return success
```

### Vetting Process (Port 8502)
```python
# secure_streamlit_app.py
def load_quarantined_content():
    # Scan quarantine directory
    # Load JSON files
    # Return content list
```

**Potential Issue**: Process isolation - files saved by one process not visible to another

## Debug Action Plan

### Phase 1: Verify Basic Flow
1. Test web search execution
2. Check quarantine file creation
3. Verify file permissions
4. Test load function directly

### Phase 2: Diagnose Integration
1. Check process isolation issues
2. Verify file system synchronization
3. Test cross-process file visibility
4. Check Streamlit refresh behavior

### Phase 3: Fix Missing Components
1. Repair quarantine → vetting integration
2. Fix statistics calculation
3. Restore security analysis display
4. Verify end-to-end flow

## Expected vs Actual State

### Expected State After Web Search
```
quarantine/
├── intelligent_web_20250612_HHMMSS_[hash].json  ← NEW FILE
├── metadata.json
└── scrapy_metadata.json

Vetting Dashboard:
├── Content Awaiting Analysis: 1 file
├── Security Statistics: Calculated
└── Analysis Dashboard: Populated
```

### Actual State (Broken)
```
quarantine/
├── metadata.json
└── scrapy_metadata.json

Vetting Dashboard:
├── Content Awaiting Analysis: 0 files
├── Security Statistics: Missing
└── Analysis Dashboard: Empty
```

## Critical Functions to Test

1. `trigger_web_search()` - Web search execution
2. `save_intelligent_web_to_quarantine()` - File creation
3. `load_quarantined_content()` - File loading
4. `get_vetting_status()` - Statistics calculation
5. `calculate_security_overview()` - Security metrics

## Success Criteria

**Fixed State Should Show**:
1. Web search results appear in quarantine
2. Vetting page displays new content
3. Security statistics calculated correctly
4. Analysis dashboard populated
5. End-to-end flow functional

## Next Actions

1. **Immediate**: Test web search → quarantine save
2. **Diagnostic**: Check file system state after web search
3. **Integration**: Verify vetting page can load new files
4. **Statistics**: Fix missing security analysis metrics
5. **End-to-End**: Complete flow verification
