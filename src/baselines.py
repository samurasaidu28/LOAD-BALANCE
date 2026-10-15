"""
Baseline peer-selection methods:
- Random selection
- Round-robin scheduling
"""

from __future__ import annotations
import random
from typing import List, Optional, Dict
from src.nodes import PeerNode


class RandomSelector:
    def select_peer(
        self, candidates: List[PeerNode], exclude: Optional[str] = None
    ) -> Optional[PeerNode]:
        eligible = [
            n for n in candidates
            if n.can_forward() and (exclude is None or n.node_id != exclude)
        ]
        if not eligible:
            return None
        return random.choice(eligible)


class RoundRobinSelector:
    def __init__(self):
        self.last_index: Dict[str, int] = {}  # source_id -> last chosen index

    def select_peer(
        self,
        candidates: List[PeerNode],
        source_id: str = "global",
        exclude: Optional[str] = None,
    ) -> Optional[PeerNode]:
        eligible = [
            n for n in candidates
            if n.can_forward() and (exclude is None or n.node_id != exclude)
        ]
        if not eligible:
            return None

        idx = self.last_index.get(source_id, -1)
        idx = (idx + 1) % len(eligible)
        self.last_index[source_id] = idx
        return eligible[idx]