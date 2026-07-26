"""Civilisation.One Global Intelligence Router (stub).

This package is the future ``intelligence-router`` boundary.
Hard-rule enforcers are stubs: they enforce contract shape and fail-closed
policy, not production cryptography or live identity systems.
"""

from .local_adapter import adapt_local_payload
from .pipeline import PipelineResult, run_scientific_pipeline

__all__ = ["PipelineResult", "run_scientific_pipeline", "adapt_local_payload"]
__version__ = "0.1.0-stub"
