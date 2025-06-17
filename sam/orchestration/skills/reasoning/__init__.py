"""
SAM Orchestration Framework - Reasoning Skills Module
====================================================

This module contains reasoning-related skills for the SAM Orchestration Framework.
These skills implement advanced cognitive capabilities like implicit knowledge
generation, conceptual understanding, and multi-hop reasoning.

Reasoning Skills:
- ImplicitKnowledgeSkill: Generates implicit connections between explicit knowledge chunks
"""

from .implicit_knowledge import ImplicitKnowledgeSkill

__all__ = [
    'ImplicitKnowledgeSkill',
]
