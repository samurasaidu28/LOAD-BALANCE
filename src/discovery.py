"""
Peer Discovery Module
Discovers currently reachable neighbours within transmission range.
"""

from __future__ import annotations
from typing import List
from src.nodes import PeerNode
from src.network import Network


class PeerDiscovery:
    def __init__(self, network: Network):
        self.network = network

    def discover(self, node_id: str) -> List[PeerNode]:
        """Return list of currently reachable neighbour nodes."""
        return self.network.get_neighbours(node_id)

    def discover_with_metrics(self, node_id: str) -> List[dict]:
        """Return neighbours with their current metrics (for AI / logging)."""
        neighbours = self.discover(node_id)
        result = []
        for n in neighbours:
            features = n.get_features()
            features["node_id"] = n.node_id
            features["distance"] = self.network.nodes[node_id].neighbours.get(n.node_id, 0)
            result.append(features)
        return result