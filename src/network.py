"""
Network topology and mobility management.
Uses NetworkX for graph representation and simple Random Waypoint mobility.
"""

from __future__ import annotations
import random
import math
from typing import List, Dict, Tuple
import networkx as nx
import config
from src.nodes import PeerNode


class Network:
    def __init__(self, nodes: List[PeerNode]):
        self.nodes: Dict[str, PeerNode] = {n.node_id: n for n in nodes}
        self.graph = nx.Graph()
        self.graph.add_nodes_from(self.nodes.keys())
        self.time = 0.0

    def update_positions(self, dt: float):
        """Move nodes according to Random Waypoint model."""
        for node in self.nodes.values():
            if not node.is_alive():
                continue

            # Still pausing?
            if self.time < node.pause_until:
                continue

            # Need a new destination?
            if node.destination is None:
                node.destination = (
                    random.uniform(0, config.AREA_SIZE),
                    random.uniform(0, config.AREA_SIZE),
                )
                node.speed = random.uniform(config.MIN_SPEED, config.MAX_SPEED)

            dx = node.destination[0] - node.x
            dy = node.destination[1] - node.y
            dist = math.hypot(dx, dy)

            if dist < 1.0:  # arrived
                node.x, node.y = node.destination
                node.destination = None
                node.pause_until = self.time + random.uniform(0, config.PAUSE_TIME)
                node.speed = 0.0
            else:
                # Move towards destination
                step = min(node.speed * dt, dist)
                node.x += (dx / dist) * step
                node.y += (dy / dist) * step

            # Small random signal fluctuation
            node.signal_strength = max(
                0.2,
                min(1.0, node.signal_strength + random.uniform(-0.05, 0.05)),
            )
            node.available_bandwidth = max(
                0.5,
                config.BASE_BANDWIDTH
                * node.signal_strength
                * random.uniform(0.8, 1.2),
            )

    def update_neighbours(self):
        """Rebuild neighbour lists based on current positions and transmission range."""
        node_list = list(self.nodes.values())
        for node in node_list:
            node.neighbours.clear()

        for i, a in enumerate(node_list):
            if not a.is_alive():
                continue
            for b in node_list[i + 1 :]:
                if not b.is_alive():
                    continue
                dist = a.distance_to(b)
                if dist <= config.TRANSMISSION_RANGE:
                    a.neighbours[b.node_id] = dist
                    b.neighbours[a.node_id] = dist

        # Update NetworkX graph edges
        self.graph.clear_edges()
        for node in node_list:
            for neigh_id in node.neighbours:
                self.graph.add_edge(node.node_id, neigh_id)

    def get_neighbours(self, node_id: str) -> List[PeerNode]:
        node = self.nodes.get(node_id)
        if not node:
            return []
        return [self.nodes[nid] for nid in node.neighbours if nid in self.nodes]

    def step(self, dt: float):
        """Advance the network by dt seconds."""
        self.time += dt
        self.update_positions(dt)
        self.update_neighbours()

        # Idle battery drain
        for node in self.nodes.values():
            if node.is_alive():
                node.idle_drain(dt)