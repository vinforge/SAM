# Phase 5 Integration Guide: Reflective Meta-Reasoning for SAM

This guide shows how to integrate Phase 5 reflective meta-reasoning capabilities into SAM's existing response generation system.

## 🚀 Quick Start

### Basic Integration

```python
from reasoning.phase5_integration import enhance_sam_response, CritiqueLevel

# Enhance any SAM response with meta-reasoning
enhanced = enhance_sam_response(
    query="How should we implement AI safety measures?",
    initial_response="We should implement multiple layers of protection...",
    context={"domain": "ai_safety", "memory_results": [...]},
    profile="researcher",
    critique_level=CritiqueLevel.MODERATE
)

print(enhanced.enhanced_response)
print(f"Meta-confidence: {enhanced.reflective_result.meta_confidence}")
```

### Advanced Integration

```python
from reasoning.phase5_integration import Phase5ResponseEnhancer
from reasoning.reflective_meta_reasoning import CritiqueLevel

# Create persistent enhancer
enhancer = Phase5ResponseEnhancer(
    critique_level=CritiqueLevel.RIGOROUS,
    profile="business",
    enable_dimension_conflicts=True,
    enable_confidence_justification=True
)

# Enhance response
result = enhancer.enhance_response(query, response, context)

# Access detailed analysis
print(f"Alternative perspectives: {len(result.reflective_result.alternative_perspectives)}")
print(f"Dimension conflicts: {len(result.dimension_conflicts)}")
print(f"Confidence level: {result.confidence_justification.confidence_level.value}")
```

## 🔧 Integration with SAM's Response Generation

### Method 1: Wrapper Integration

```python
def enhanced_sam_response(query: str, context: Dict[str, Any]) -> str:
    """Enhanced SAM response with Phase 5 meta-reasoning."""
    
    # Generate initial response using existing SAM logic
    initial_response = generate_sam_response(query, context)
    
    # Apply Phase 5 enhancement
    enhanced = enhance_sam_response(
        query=query,
        initial_response=initial_response,
        context=context,
        profile=context.get("profile", "general"),
        critique_level=CritiqueLevel.MODERATE
    )
    
    return enhanced.enhanced_response
```

### Method 2: Pipeline Integration

```python
class EnhancedSAMPipeline:
    def __init__(self):
        self.sam_core = SAMCore()
        self.phase5_enhancer = Phase5ResponseEnhancer()
    
    def process_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Stage 1: Core SAM processing
        initial_result = self.sam_core.process(query, context)
        
        # Stage 2: Phase 5 enhancement
        enhanced_result = self.phase5_enhancer.enhance_response(
            query, initial_result["response"], context
        )
        
        return {
            "response": enhanced_result.enhanced_response,
            "meta_reasoning": enhanced_result.meta_reasoning_summary,
            "confidence": enhanced_result.confidence_justification,
            "conflicts": enhanced_result.dimension_conflicts
        }
```

## 🎛️ Configuration Options

### Critique Levels

```python
from reasoning.reflective_meta_reasoning import CritiqueLevel

# Available critique levels
CritiqueLevel.GENTLE      # Mild suggestions and alternatives
CritiqueLevel.MODERATE    # Balanced critique with counter-arguments
CritiqueLevel.RIGOROUS    # Strong challenges and evidence requirements
CritiqueLevel.ADVERSARIAL # Maximum critique intensity
```

### Reasoning Profiles

```python
# Available profiles with different evidence weighting
profiles = {
    "general": "Balanced approach for general use",
    "researcher": "Emphasizes peer review and empirical support",
    "business": "Focuses on ROI and expert validation",
    "legal": "Prioritizes source credibility and expert validation"
}
```

### Component Configuration

```python
enhancer = Phase5ResponseEnhancer(
    critique_level=CritiqueLevel.MODERATE,
    profile="researcher",
    enable_dimension_conflicts=True,    # Detect conceptual tensions
    enable_confidence_justification=True  # Provide evidence-based confidence
)

# Dynamic reconfiguration
enhancer.configure_critique_level(CritiqueLevel.RIGOROUS)
enhancer.configure_profile("business")
```

## 📊 Accessing Meta-Reasoning Results

### Basic Results

```python
enhanced = enhance_sam_response(query, response, context)

# Enhanced response with meta-reasoning
print(enhanced.enhanced_response)

# Processing metadata
print(f"Processing time: {enhanced.processing_time_ms}ms")
print(f"Meta-reasoning summary: {enhanced.meta_reasoning_summary}")
```

### Detailed Analysis

```python
# Alternative perspectives
for perspective in enhanced.reflective_result.alternative_perspectives:
    print(f"{perspective.perspective_name}: {perspective.reasoning}")
    print(f"Trade-offs: {perspective.trade_offs}")

# Adversarial critiques
for critique in enhanced.reflective_result.adversarial_critiques:
    print(f"Critique (severity {critique.severity}): {critique.critique_text}")
    print(f"Counter-arguments: {critique.counter_arguments}")

# Dimension conflicts
for conflict in enhanced.dimension_conflicts:
    print(f"Conflict: {conflict.conflict_type.value}")
    print(f"Description: {conflict.description}")
    print(f"Recommendation: {conflict.recommendation}")

# Confidence justification
if enhanced.confidence_justification:
    conf = enhanced.confidence_justification
    print(f"Confidence: {conf.confidence_level.value} ({conf.confidence_score:.2f})")
    print(f"Primary factors: {conf.primary_factors}")
    print(f"Limiting factors: {conf.limiting_factors}")
```

## 🔍 Error Handling and Fallbacks

### Graceful Degradation

```python
# Phase 5 includes robust fallback mechanisms
enhanced = enhance_sam_response(query, response, context)

if not enhanced.phase5_enabled:
    print("Phase 5 temporarily unavailable - using fallback")
    print(enhanced.enhanced_response)  # Still includes original response
else:
    print("Full Phase 5 meta-reasoning applied")
    print(enhanced.enhanced_response)
```

### Status Monitoring

```python
enhancer = Phase5ResponseEnhancer()
status = enhancer.get_phase5_status()

print(f"Phase 5 available: {status['phase5_available']}")
print(f"Components: {status}")

# Check individual components
if not status['reflective_engine']:
    print("Reflective engine unavailable")
if not status['conflict_detector']:
    print("Conflict detector unavailable")
```

## 🎯 Use Case Examples

### Academic Research

```python
# Configure for research context
enhanced = enhance_sam_response(
    query="What are the implications of this research finding?",
    initial_response=research_response,
    context={"domain": "research", "memory_results": papers},
    profile="researcher",
    critique_level=CritiqueLevel.RIGOROUS
)

# Access research-specific analysis
print("Research perspectives:", enhanced.reflective_result.alternative_perspectives)
print("Methodological critiques:", enhanced.reflective_result.adversarial_critiques)
```

### Business Decision Making

```python
# Configure for business context
enhanced = enhance_sam_response(
    query="Should we invest in this technology?",
    initial_response=business_response,
    context={"domain": "business", "roi_data": financial_data},
    profile="business",
    critique_level=CritiqueLevel.MODERATE
)

# Access business-specific analysis
for conflict in enhanced.dimension_conflicts:
    if "market" in conflict.conflict_type.value:
        print(f"Market risk: {conflict.description}")
        print(f"Mitigation: {conflict.recommendation}")
```

### Legal Analysis

```python
# Configure for legal context
enhanced = enhance_sam_response(
    query="What are the legal implications of this action?",
    initial_response=legal_response,
    context={"domain": "legal", "precedents": case_law},
    profile="legal",
    critique_level=CritiqueLevel.RIGOROUS
)

# Access legal-specific analysis
print("Legal perspectives:", enhanced.reflective_result.alternative_perspectives)
print("Compliance conflicts:", enhanced.dimension_conflicts)
```

## 🧪 Testing Integration

### Unit Testing

```python
def test_sam_phase5_integration():
    """Test Phase 5 integration with SAM."""
    query = "Test query"
    response = "Test response"
    context = {"domain": "test"}
    
    enhanced = enhance_sam_response(query, response, context)
    
    assert enhanced.original_response == response
    assert len(enhanced.enhanced_response) > len(response)
    assert enhanced.processing_time_ms > 0
    assert enhanced.phase5_enabled
```

### Performance Testing

```python
import time

def benchmark_phase5_performance():
    """Benchmark Phase 5 performance."""
    start_time = time.time()
    
    enhanced = enhance_sam_response(
        query="Complex analysis query",
        initial_response="Detailed response...",
        context={"memory_results": large_dataset}
    )
    
    processing_time = time.time() - start_time
    print(f"Total processing time: {processing_time*1000:.1f}ms")
    print(f"Phase 5 processing: {enhanced.processing_time_ms}ms")
```

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all Phase 5 components are in the Python path
2. **Performance**: Use appropriate critique levels for your use case
3. **Memory Usage**: Consider disabling unused components for resource-constrained environments

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging for Phase 5 components
enhanced = enhance_sam_response(query, response, context)
# Check logs for detailed processing information
```

## 📈 Performance Optimization

### Selective Enhancement

```python
# Only enable specific components for better performance
enhancer = Phase5ResponseEnhancer(
    enable_dimension_conflicts=False,  # Disable if not needed
    enable_confidence_justification=True
)
```

### Caching

```python
# Cache enhancer instance for better performance
_cached_enhancer = None

def get_enhancer():
    global _cached_enhancer
    if _cached_enhancer is None:
        _cached_enhancer = Phase5ResponseEnhancer()
    return _cached_enhancer
```

## 🎉 Next Steps

1. **Integrate with SAM Core**: Add Phase 5 to your main response pipeline
2. **Configure for Your Domain**: Choose appropriate profiles and critique levels
3. **Monitor Performance**: Track processing times and adjust configuration
4. **Collect Feedback**: Use meta-reasoning insights to improve responses
5. **Explore Advanced Features**: Experiment with different critique levels and profiles

The Phase 5 system is designed to seamlessly integrate with existing SAM functionality while providing revolutionary meta-cognitive capabilities. Start with basic integration and gradually explore the advanced features as you become familiar with the system.
