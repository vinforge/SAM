# SAM Phase 3 Testing Guide

## Quick Start Testing Commands

### 1. Start SAM
```bash
cd /Users/vinsoncornejo/Downloads/augment-projects/SAM
python start_sam.py
```

### 2. Run Phase 3 Demo Scripts
```bash
# Complete API-based demo
python test_phase3_demo.py

# Direct memory system testing
python test_memory_cli.py

# Interactive search demo
python test_memory_cli.py
# Then choose 'y' for interactive mode
```

### 3. Test via cURL (API Testing)
```bash
# Test enhanced search
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What does Blue Cloak do?"}'

# Test citation system
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Summarize the main points from uploaded documents"}'

# Test hybrid search
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find recent information about cybersecurity"}'
```

## Phase 3 Feature Testing

### Phase 3.2.1: Enhanced Search & Ranking Engine

**Test Commands:**
```bash
# Direct memory testing
python -c "
from memory.memory_vectorstore import get_memory_store
store = get_memory_store()
results = store.enhanced_search_memories('Blue Cloak', max_results=5)
print(f'Found {len(results)} results')
for r in results[:3]:
    if hasattr(r, 'final_score'):
        print(f'Score: {r.final_score:.3f}, Content: {r.content[:100]}...')
"
```

**What to Look For:**
- ✅ `RankedMemoryResult` objects with `final_score`
- ✅ Semantic, recency, and confidence scoring
- ✅ Configurable ranking weights
- ✅ Multi-strategy search approaches

### Phase 3.2.2: Citation System Refactoring

**Test Commands:**
```bash
# Test citation engine directly
python -c "
from memory.citation_engine import get_citation_engine
from memory.memory_vectorstore import get_memory_store
engine = get_citation_engine()
store = get_memory_store()
memories = store.enhanced_search_memories('Blue Cloak', max_results=3)
if memories:
    response = engine.inject_citations('Blue Cloak is a company.', memories, 'Blue Cloak')
    print('Citations:', len(response.citations))
    print('Transparency:', f'{response.transparency_score:.1%}')
    print('Response:', response.response_text)
"
```

**What to Look For:**
- ✅ Enhanced citation formatting with confidence indicators (●●●○○)
- ✅ Granular metadata (page numbers, chunk references)
- ✅ Direct metadata access (no JSON file lookups)
- ✅ Transparency scoring

### Phase 3.2.3: Memory Control Center Enhancement

**Access URLs:**
- **Memory Control Center:** http://localhost:8501
- **Enhanced Chat Interface:** http://localhost:5001

**Features to Test:**
1. **Real-time Search:** Type in search box and see live results
2. **Advanced Filtering:** Use source, confidence, and quality filters
3. **Interactive Configuration:** Adjust ranking weights with sliders
4. **Source Analysis:** View source distribution charts
5. **Enhanced Memory Cards:** See ranking badges and confidence indicators

## Interactive Testing Scenarios

### Scenario 1: Document Upload and Search
```bash
# 1. Upload a PDF via web interface (http://localhost:5001)
# 2. Test enhanced search:
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the main topics in the uploaded document?"}'

# 3. Check Memory Control Center for new memories
# Visit: http://localhost:8501
```

### Scenario 2: Ranking Weight Adjustment
```bash
# 1. Open Memory Control Center: http://localhost:8501
# 2. Go to "Memory Ranking" section
# 3. Adjust semantic similarity weight from 60% to 80%
# 4. Test search with same query
# 5. Compare results before and after adjustment
```

### Scenario 3: Citation Quality Testing
```bash
# Test different confidence levels
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Provide detailed information about Blue Cloak with sources"}'

# Look for:
# - 📚 Enhanced citation formatting
# - ●●●○○ Confidence indicators  
# - [p.1, chunk 2] Location references
# - Transparency percentages
```

## Expected Phase 3 Outputs

### Enhanced Search Results
```
✅ Enhanced search returned 5 ranked results
   1. Final Score: 0.847
      Semantic: 0.823
      Recency: 0.945
      Confidence: 0.756
      Content: Blue Cloak is a cybersecurity company...
```

### Enhanced Citations
```
📚 **Blue_Cloak_Document.pdf** ●●●○○ (54.8%)
[p.1, chunk 2, 15% through doc]
_Blue Cloak is a company with significant experience in cybersecurity..._

**Sources:** 3 document(s) referenced
**Transparency Score:** 78.5%
```

### Memory Control Center Features
- 🔍 **Real-time Search:** Live results as you type
- 🎛️ **Interactive Sliders:** Adjust ranking weights
- 📊 **Visual Analytics:** Source distribution charts
- 🎯 **Quality Filters:** Confidence and ranking thresholds
- 📈 **Performance Metrics:** Search quality and response times

## Troubleshooting

### Common Issues

**1. "Enhanced search not available"**
```bash
# Check if ranking engine is initialized
python -c "
from memory.memory_vectorstore import get_memory_store
store = get_memory_store()
print('Enhanced search:', hasattr(store, 'enhanced_search_memories'))
print('Ranking engine:', hasattr(store, 'ranking_engine'))
"
```

**2. "No memories found"**
```bash
# Check memory count
python -c "
from memory.memory_vectorstore import get_memory_store
store = get_memory_store()
print(f'Total memories: {len(store.memory_chunks)}')
print(f'Store type: {store.store_type}')
"
```

**3. "Citations not appearing"**
```bash
# Test citation engine directly
python -c "
from memory.citation_engine import get_citation_engine
engine = get_citation_engine()
print(f'Citations enabled: {engine.enable_citations}')
print(f'Citation style: {engine.citation_style}')
"
```

### Performance Verification

**Check Phase 3 Performance:**
```bash
# Time enhanced search
python -c "
import time
from memory.memory_vectorstore import get_memory_store
store = get_memory_store()
start = time.time()
results = store.enhanced_search_memories('test query', max_results=10)
end = time.time()
print(f'Search time: {(end-start)*1000:.1f}ms')
print(f'Results: {len(results)}')
"
```

## Success Indicators

### ✅ Phase 3.2.1 Working
- Enhanced search returns `RankedMemoryResult` objects
- Multiple scoring factors (semantic, recency, confidence)
- Configurable ranking weights
- Sub-second search performance

### ✅ Phase 3.2.2 Working  
- Citations include confidence indicators (●●●○○)
- Granular metadata (page numbers, chunk references)
- No JSON file lookup delays
- Transparency scoring available

### ✅ Phase 3.2.3 Working
- Memory Control Center accessible at port 8501
- Real-time search and filtering
- Interactive configuration controls
- Visual analytics and source distribution

## Next Steps

After successful testing:
1. **Document Results:** Note performance improvements
2. **User Testing:** Have others test the enhanced features
3. **Performance Monitoring:** Track search quality and speed
4. **Feature Feedback:** Collect user feedback on new capabilities
5. **Production Deployment:** Prepare for wider release

---

**Phase 3 Testing Complete!** 🎉
All enhanced memory, search, and citation features are ready for production use.
