# SAM Pro Activation Key Generation Guide

This guide explains how to generate SAM Pro activation keys for distribution to authorized users.

## Overview

SAM Pro uses a secure activation system based on:
- **UUID-format activation keys** (e.g., `12345678-1234-1234-1234-123456789abc`)
- **SHA-256 hash validation** stored in `sam/config/entitlements.json`
- **One-time use** - each key can only be activated once

## Key Generation Script

### Location
```
scripts/generate_pro_activation_key.py
```

### Basic Usage

#### Generate a single key:
```bash
python scripts/generate_pro_activation_key.py --output-keys
```

#### Generate multiple keys:
```bash
python scripts/generate_pro_activation_key.py --count 5 --output-keys
```

#### Generate keys without displaying them:
```bash
python scripts/generate_pro_activation_key.py --count 10
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--count`, `-c` | Number of keys to generate | 1 |
| `--output-keys`, `-o` | Display generated keys (security sensitive) | False |

### Examples

#### Example 1: Generate one key for testing
```bash
cd /path/to/SAM
python scripts/generate_pro_activation_key.py --output-keys
```

Output:
```
🚀 SAM Pro Activation Key Generator
==================================================
🔑 Generating 1 SAM Pro activation key(s)...
  Generated key 1/1

📝 Updating entitlements configuration...
📋 Backup created: sam/config/entitlements.json.backup
✅ Entitlements configuration updated successfully

✅ Successfully generated 1 activation key(s)
📊 Statistics:
  • Keys generated: 1
  • Hash algorithm: SHA-256
  • Generated at: 2025-06-17 14:30:45

🔑 Generated Activation Keys:
============================================================
Key  1: a1b2c3d4-e5f6-7890-abcd-ef1234567890
Hash  : 93e6a9a06e1a82a52091c370710cb3b1b2cafe6792bc3ee4c7daf141564ffeda
------------------------------------------------------------

⚠️  SECURITY WARNING:
• Store these keys securely
• Distribute only to authorized users
• Keys cannot be recovered if lost
• Each key can only be used once

🎉 Key generation complete!
📁 Configuration updated: sam/config/entitlements.json
```

#### Example 2: Generate multiple keys for distribution
```bash
python scripts/generate_pro_activation_key.py --count 10 --output-keys
```

## Security Considerations

### Key Storage
- **Generated keys are NOT stored anywhere** - only their SHA-256 hashes
- **Keys are displayed only once** during generation
- **Copy keys immediately** to a secure location
- **Keys cannot be recovered** if lost

### Distribution
- **Distribute keys securely** (encrypted email, secure messaging)
- **One key per authorized user**
- **Keys are single-use** - cannot be reused
- **Track key distribution** for audit purposes

### Backup
- **Automatic backup** of `entitlements.json` is created before updates
- **Backup location**: `sam/config/entitlements.json.backup`
- **Restore if needed**: `cp sam/config/entitlements.json.backup sam/config/entitlements.json`

## How Activation Works

### User Perspective
1. User enters activation key in SAM Pro interface
2. System validates key format (UUID)
3. System checks key against valid hashes
4. Pro features are unlocked if valid

### Technical Process
1. User key is hashed with SHA-256
2. Hash is compared against `valid_key_hashes` in `entitlements.json`
3. If match found, pro features are activated
4. Activation state is saved to user's secure state

## Pro Features Unlocked

When activated, SAM Pro unlocks:

### TPV Active Control
- **Advanced reasoning control** with 48.4% efficiency gains
- **Real-time reasoning monitoring** and intervention
- **Adaptive reasoning strategies** based on query complexity

### Cognitive Automation (Bulk Processing)
- **Bulk document ingestion** from folders
- **Automated processing** of multiple file types
- **Batch operations** for large document sets

### Dream Canvas
- **Interactive memory visualization** with UMAP projections
- **Cognitive synthesis exploration** through visual interface
- **Memory landscape navigation** and cluster analysis

## Troubleshooting

### Common Issues

#### "Entitlements config not found"
- **Cause**: Script not run from SAM root directory
- **Solution**: `cd` to SAM directory before running script

#### "Invalid JSON in entitlements config"
- **Cause**: Corrupted `entitlements.json` file
- **Solution**: Restore from backup or regenerate

#### "Failed to save entitlements config"
- **Cause**: Permission issues or disk space
- **Solution**: Check file permissions and available disk space

### Validation

#### Check current valid keys count:
```bash
python -c "import json; print(f'Valid keys: {len(json.load(open(\"sam/config/entitlements.json\"))[\"valid_key_hashes\"])}')"
```

#### Verify key format:
```bash
python -c "import uuid; print('Valid UUID format:', bool(uuid.UUID('YOUR-KEY-HERE')))"
```

## Administrative Tasks

### View Current Configuration
```bash
cat sam/config/entitlements.json | jq '.metadata'
```

### Count Valid Keys
```bash
cat sam/config/entitlements.json | jq '.valid_key_hashes | length'
```

### Backup Configuration
```bash
cp sam/config/entitlements.json sam/config/entitlements.json.$(date +%Y%m%d_%H%M%S)
```

## Security Best Practices

1. **Generate keys on secure systems** only
2. **Use encrypted communication** for key distribution
3. **Maintain key distribution logs** for audit trails
4. **Regularly backup** entitlements configuration
5. **Monitor activation attempts** through SAM logs
6. **Revoke access** by removing hashes if needed

## Support

For issues with key generation or activation:
1. Check SAM logs in `logs/` directory
2. Verify entitlements configuration format
3. Ensure proper file permissions
4. Contact SAM development team if needed

---

**Note**: This key generation system is designed for authorized distribution of SAM Pro licenses. Ensure compliance with your organization's software licensing policies.
