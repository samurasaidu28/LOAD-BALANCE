"""
Network Monitoring Module
Collects real-time metrics from nodes for the AI balancer and evaluation.
"""

from __future__ import annotations
from typing import Dict, List, Any
from src.nodes import PeerNode
from src.network import Network
import config


class NetworkMonitor:
    def __init__(self, network: Network):
        self.network = network
        self.history: List[Dict[str, Any]] = []

    def snapshot(self) -> Dict[str, Any]:
        """Take a snapshot of the entire network state."""
        alive = [n for n in self.network.nodes.values() if n.is_alive()]
        total_energy = sum(n.energy_used for n in self.network.nodes.values())
        avg_battery = sum(n.battery for n in alive) / len(alive) if alive else 0

        snap = {
            "time": self.network.time,
            "alive_nodes": len(alive),
            "total_nodes": len(self.network.nodes),
            "avg_battery": avg_battery,
            "total_energy_used": total_energy,
            "edges": self.network.graph.number_of_edges(),
        }
        self.history.append(snap)
        return snap

    def get_node_features(self, node_ids: List[str]) -> List[Dict[str, float]]:
        """Collect feature vectors for a list of candidate nodes."""
        features = []
        for nid in node_ids:
            node = self.network.nodes.get(nid)
            if node and node.can_forward():
                features.append(node.get_features())
        return features

    def log_event(self, event_type: str, details: Dict):
        """Simple event logger (can be extended to write to CSV)."""
        record = {
            "time": self.network.time,
            "event": event_type,
            **details,
        }
        pass