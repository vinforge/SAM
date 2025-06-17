# MEMOIR: Lifelong Knowledge Editor for SAM

## Overview

MEMOIR (Memory-Efficient Model Editing with Localized Updates and Retrieval) is SAM's lifelong learning system that enables continuous knowledge updates without catastrophic forgetting. This implementation follows the MEMOIR paper's approach to localized model editing through sparse residual connections.

## 🎯 Key Features

- **Non-Destructive Learning**: Updates knowledge without affecting existing capabilities
- **Localized Edits**: Changes are isolated to specific neural pathways
- **Deterministic Retrieval**: Consistent activation of relevant memories
- **Scalable Storage**: Efficient storage and retrieval of thousands of edits
- **Zero-Impact Initialization**: No effect on model performance before edits

## 📁 Architecture Overview

```
sam/
├── core/
│   ├── model_layers.py      # ResidualMemoryLayer & MEMOIRTransformerBlock
│   ├── fingerprinter.py     # TopHashFingerprinter for mask generation
│   └── __init__.py          # Core module exports
├── memory/
│   └── edit_mask_db.py      # EditMaskDatabase for mask storage/retrieval
├── orchestration/
│   ├── skills/internal/
│   │   └── memoir_edit.py   # MEMOIR_EditSkill (Phase B)
│   ├── skills/autonomous/
│   │   └── factual_correction.py  # Autonomous correction skill (Phase C)
│   └── memoir_sof_integration.py  # SOF integration (Phase C)
├── learning/
│   └── feedback_handler.py  # Automatic learning from feedback (Phase C)
└── reasoning/
    └── memoir_reasoning_integration.py  # TPV & SLP integration (Phase C)

scripts/
├── generate_permutation.py         # Generate fingerprinter permutation matrix
├── install_memoir_dependencies.py  # Install required packages
├── verify_memoir_phase_a.py        # Phase A verification script
├── verify_memoir_phase_b.py        # Phase B verification script
├── verify_memoir_phase_c.py        # Phase C verification script
├── demo_memoir_system.py           # Phase A & B demonstration
└── demo_complete_memoir_system.py  # Complete system demonstration

tests/
├── test_memoir_components.py       # Phase A unit tests
├── test_memoir_phase_b.py          # Phase B integration tests
└── test_memoir_phase_c.py          # Phase C integration tests
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
python scripts/install_memoir_dependencies.py
```

### 2. Generate Permutation Matrix

```bash
python scripts/generate_permutation.py --hidden_size 4096 --output data/memoir_permutation.pkl
```

### 3. Verify Installation

```bash
python scripts/verify_memoir_phase_a.py
```

### 4. Run Unit Tests

```bash
# Phase A tests
python tests/test_memoir_components.py

# Phase B integration tests
python tests/test_memoir_phase_b.py
```

### 5. Run System Demonstration

```bash
python scripts/demo_memoir_system.py
```

## 🧠 Core Components

### ResidualMemoryLayer

The heart of MEMOIR's editing capability. Provides sparse residual connections that can be activated based on input patterns.

```python
from sam.core.model_layers import ResidualMemoryLayer

# Initialize with zero weights (no initial effect)
memory_layer = ResidualMemoryLayer(
    hidden_size=4096,
    max_edits=10000,
    sparsity_ratio=0.01
)

# Add an edit
edit_mask = torch.zeros(4096)
edit_mask[:100] = 1.0  # Activate first 100 neurons
memory_layer.add_edit("fact_correction_1", edit_mask, {"source": "user"})

# Forward pass with edit activation
hidden_states = torch.randn(1, 10, 4096)
residual_output = memory_layer(hidden_states, edit_mask=edit_mask, edit_id="fact_correction_1")
```

### TopHashFingerprinter

Generates deterministic sparse masks based on activation patterns using a fixed permutation matrix.

```python
from sam.core.fingerprinter import TopHashFingerprinter

# Initialize fingerprinter
fingerprinter = TopHashFingerprinter(
    hidden_size=4096,
    top_k=100,  # Select top 100 activations
    permutation_file="data/memoir_permutation.pkl"
)

# Generate mask from activations
activations = torch.randn(4096)
edit_mask = fingerprinter.generate_mask(activations)

# Verify determinism
is_deterministic = fingerprinter.validate_determinism(activations)
```

### EditMaskDatabase

Efficient storage and similarity-based retrieval of edit masks using FAISS.

```python
from sam.memory.edit_mask_db import EditMaskDatabase

# Initialize database
db = EditMaskDatabase(
    hidden_size=4096,
    similarity_metric='cosine',
    storage_dir='data/memoir_masks'
)

# Add mask
edit_mask = torch.zeros(4096)
edit_mask[:100] = 1.0
db.add("edit_1", edit_mask, {"description": "User correction"})

# Find similar mask
result = db.find_closest(query_mask, threshold=0.8)
if result:
    edit_id, original_mask, similarity = result
    print(f"Found similar edit: {edit_id} (similarity: {similarity:.3f})")
```

### MEMOIRTransformerBlock

Enhanced transformer block with integrated MEMOIR functionality.

```python
from sam.core.model_layers import MEMOIRTransformerBlock

# Initialize block with MEMOIR enabled
block = MEMOIRTransformerBlock(
    hidden_size=4096,
    num_attention_heads=32,
    intermediate_size=16384,
    enable_memoir=True
)

# Forward pass with MEMOIR edit
hidden_states = torch.randn(1, 10, 4096)
edit_mask = torch.zeros(4096)
edit_mask[:100] = 1.0

output, attention_weights = block(
    hidden_states,
    edit_mask=edit_mask,
    edit_id="correction_1"
)
```

### MEMOIR_EditSkill

Skill for performing localized model edits through the SAM orchestration framework.

```python
from sam.orchestration.skills.internal.memoir_edit import MEMOIR_EditSkill
from sam.orchestration.uif import SAM_UIF

# Initialize edit skill
edit_skill = MEMOIR_EditSkill(
    hidden_size=4096,
    learning_rate=1e-4,
    max_training_steps=10
)

# Create edit request
edit_uif = SAM_UIF(
    input_query="Factual correction",
    intermediate_data={
        "edit_prompt": "What is the capital of Australia?",
        "correct_answer": "Canberra",
        "edit_context": "Geography correction",
        "confidence_score": 0.95
    }
)

# Execute the edit
result_uif = edit_skill.execute(edit_uif)

# Check results
if result_uif.intermediate_data["edit_success"]:
    edit_id = result_uif.intermediate_data["edit_id"]
    print(f"Edit successful: {edit_id}")
```

### Enhanced Transformer with Automatic Retrieval

The enhanced transformer block automatically retrieves relevant edits during forward pass.

```python
# Forward pass with automatic retrieval
output, _ = block(
    hidden_states,
    enable_memoir_retrieval=True  # Automatically find and apply relevant edits
)

# Check what was retrieved
retrieval_info = block.get_last_retrieval_info()
if retrieval_info:
    print(f"Retrieved edit: {retrieval_info['edit_id']}")
    print(f"Similarity: {retrieval_info['similarity']:.3f}")

# Configure retrieval threshold
block.set_retrieval_threshold(0.8)  # Only retrieve edits with >80% similarity
```

## 📋 Implementation Phases

### ✅ Phase A: Foundational Architecture (COMPLETE)

**Objective**: Implement core MEMOIR components

**Components**:
- ✅ ResidualMemoryLayer with zero-weight initialization
- ✅ TopHashFingerprinter with deterministic mask generation
- ✅ EditMaskDatabase with FAISS-based similarity search
- ✅ MEMOIRTransformerBlock integration
- ✅ Comprehensive unit tests
- ✅ Verification scripts

**Definition of Done**: All components implemented, tested, and verified working correctly.

### ✅ Phase B: Edit & Retrieve Cycle (COMPLETE)

**Objective**: Implement the core read/write operations

**Components**:
- ✅ MEMOIR_EditSkill for performing localized edits
- ✅ Enhanced transformer forward pass with automatic retrieval
- ✅ Gradient isolation for targeted parameter updates
- ✅ End-to-end integration testing
- ✅ Performance optimization and monitoring
- ✅ Comprehensive error handling and validation

**Definition of Done**: Complete read/write cycle working with gradient isolation and automatic retrieval.

### ✅ Phase C: High-Level Integration (COMPLETE)

**Objective**: Connect MEMOIR to SAM's high-level systems

**Components**:
- ✅ SOF skill registration and dynamic planner integration
- ✅ FeedbackHandler integration for automatic learning from user corrections
- ✅ Autonomous FactualCorrectionSkill for self-correction capabilities
- ✅ Advanced reasoning integration with TPV and SLP systems
- ✅ End-to-end integration testing and performance optimization

**Definition of Done**: Complete integration with SAM's advanced systems enabling autonomous lifelong learning.

## 🔧 Configuration

### Environment Variables

```bash
# MEMOIR configuration
MEMOIR_HIDDEN_SIZE=4096
MEMOIR_MAX_EDITS=10000
MEMOIR_TOP_K=100
MEMOIR_SIMILARITY_THRESHOLD=0.8
MEMOIR_STORAGE_DIR=data/memoir_storage
MEMOIR_PERMUTATION_FILE=data/memoir_permutation.pkl
```

### Model Integration

To integrate MEMOIR into existing SAM models:

1. Replace standard transformer blocks with MEMOIRTransformerBlock
2. Initialize with `enable_memoir=True`
3. Configure appropriate hidden_size and max_edits
4. Set up EditMaskDatabase for persistent storage

## 🧪 Testing

### Unit Tests

```bash
# Run all MEMOIR tests
python tests/test_memoir_components.py

# Run specific test class
python -m unittest tests.test_memoir_components.TestResidualMemoryLayer
```

### Integration Tests

```bash
# Verify Phase A implementation
python scripts/verify_memoir_phase_a.py

# Test component integration
python -c "
from sam.core.model_layers import ResidualMemoryLayer
from sam.core.fingerprinter import TopHashFingerprinter
from sam.memory.edit_mask_db import EditMaskDatabase
print('✅ All components imported successfully')
"
```

## 📊 Performance Considerations

### Memory Usage

- **ResidualMemoryLayer**: ~40MB per 10,000 edits (4096D)
- **EditMaskDatabase**: ~16MB per 10,000 masks (4096D)
- **TopHashFingerprinter**: ~16KB permutation matrix (4096D)

### Computational Overhead

- **Mask Generation**: ~0.1ms per query (4096D)
- **Database Search**: ~1ms per query (10,000 masks)
- **Memory Layer Forward**: ~0.05ms per edit

### Optimization Tips

1. Use appropriate `top_k` values (1-5% of hidden_size)
2. Set reasonable similarity thresholds (0.7-0.9)
3. Periodically consolidate similar edits
4. Use GPU acceleration for large-scale deployments

## 🔍 Troubleshooting

### Common Issues

**Import Errors**:
```bash
# Install missing dependencies
python scripts/install_memoir_dependencies.py
```

**FAISS Not Available**:
- System falls back to numpy-based similarity search
- Install FAISS: `pip install faiss-cpu` or `pip install faiss-gpu`

**Permutation Matrix Missing**:
```bash
# Generate new permutation matrix
python scripts/generate_permutation.py --hidden_size 4096
```

**Memory Issues**:
- Reduce `max_edits` parameter
- Use smaller `hidden_size`
- Enable edit consolidation

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Follow the existing code style and patterns
2. Add comprehensive unit tests for new features
3. Update documentation for API changes
4. Run verification scripts before submitting changes

## 📚 References

- MEMOIR Paper: "Localized Model Editing for Lifelong Learning"
- SAM Architecture Documentation
- FAISS Documentation: https://github.com/facebookresearch/faiss

## 📄 License

This implementation is part of the SAM project and follows the same licensing terms.
