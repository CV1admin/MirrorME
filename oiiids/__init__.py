"""Origin Irreducible Intelligence Information Distribution System.

OIIIDS provides a resource-centric exchange boundary between local MirrorME
member nodes and the Civilisation.One platform. The package deliberately keeps
identity, authorisation, transport, and persistence behind explicit interfaces.
"""

from .models import (
    AccessScope,
    ResourceEnvelope,
    ResourceManifest,
    ResourcePayload,
    ResourceStatus,
)
from .service import ExchangeResult, ResourceExchangeService
from .store import InMemoryResourceStore, ResourceStore

__all__ = [
    "AccessScope",
    "ExchangeResult",
    "InMemoryResourceStore",
    "ResourceEnvelope",
    "ResourceExchangeService",
    "ResourceManifest",
    "ResourcePayload",
    "ResourceStatus",
    "ResourceStore",
]
