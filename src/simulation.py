"""
Main Simulation Engine
Uses a discrete-event style loop.
"""

from __future__ import annotations
import random
from typing import Dict, List, Optional
import config
from src.nodes import create_nodes, PeerNode, Message
from src.network import Network
from src.discovery import PeerDiscovery
from src.monitoring import NetworkMonitor
from src.ai_balancer import AILoadBalancer
from src.baselines import RandomSelector, RoundRobinSelector
from src.communication import CommunicationLayer


class Simulation:
    def __init__(self, strategy: str = "ai"):
        """
        strategy: "ai" | "random" | "round_robin"
        """
        self.strategy = strategy
        self.nodes = create_nodes(config.NUM_NODES)
        self.network = Network(self.nodes)
        self.discovery = PeerDiscovery(self.network)
        self.monitor = NetworkMonitor(self.network)
        self.comm = CommunicationLayer(self.network)

        # Selector
        if strategy == "ai":
            self.selector = AILoadBalancer()
            self.selector.train()
        elif strategy == "random":
            self.selector = RandomSelector()
        elif strategy == "round_robin":
            self.selector = RoundRobinSelector()
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        self.messages_generated = 0
        self.dt = 1.0  # simulation step in seconds

    def _generate_traffic(self):
        """Generate new messages according to the configured rate."""
        if self.messages_generated >= config.NUM_MESSAGES:
            return

        # Higher chance so that messages appear reliably
        if random.random() > min(0.95, config.MESSAGE_GENERATION_RATE * self.dt * 3):
            return

        alive = [n for n in self.nodes if n.is_alive()]
        if len(alive) < 2:
            return

        source = random.choice(alive)
        dest_candidates = [n for n in alive if n.node_id != source.node_id]
        if not dest_candidates:
            return
        dest = random.choice(dest_candidates)

        msg = self.comm.create_message(source, dest.node_id)
        source.queue.append(msg)
        self.messages_generated += 1

    def _process_node_queues(self):
        """Each node tries to forward messages in its queue."""
        for node in self.nodes:
            if not node.is_alive() or not node.queue:
                continue

            # Process one message per step (simple)
            msg = node.queue[0]

            # Already at destination?
            if node.node_id == msg.dest_id:
                self.comm.delivered.append(msg)
                node.queue.pop(0)
                continue

            # Discover neighbours
            candidates = self.discovery.discover(node.node_id)
            if not candidates:
                # No neighbours – keep in queue (store-and-forward)
                continue

            # Select next hop
            if self.strategy == "ai":
                next_hop = self.selector.select_peer(candidates, exclude=node.node_id)
            elif self.strategy == "round_robin":
                next_hop = self.selector.select_peer(
                    candidates, source_id=node.node_id, exclude=node.node_id
                )
            else:
                next_hop = self.selector.select_peer(candidates, exclude=node.node_id)

            if next_hop is None:
                continue

            # Attempt forward
            success = self.comm.try_forward(node, msg, next_hop)
            if success:
                node.queue.pop(0)
            else:
                # Failed – leave in queue, update reliability negatively
                node.update_reliability(success=False)

    def run(self) -> Dict:
        print(f"\n=== Starting simulation with strategy: {self.strategy.upper()} ===")
        print(f"Nodes: {config.NUM_NODES} | Duration: {config.SIMULATION_TIME}s | Messages: {config.NUM_MESSAGES}")

        steps = int(config.SIMULATION_TIME / self.dt)
        for step in range(steps):
            self.network.step(self.dt)
            self._generate_traffic()
            self._process_node_queues()

            if step % 300 == 0:  # every 5 minutes
                snap = self.monitor.snapshot()
                print(
                    f"  t={snap['time']:6.0f}s | "
                    f"alive={snap['alive_nodes']:2d} | "
                    f"avg_batt={snap['avg_battery']:5.1f}% | "
                    f"delivered={len(self.comm.delivered):3d}"
                )

        # Final stats
        stats = self.comm.get_stats()
        total_energy = sum(n.energy_used for n in self.nodes)
        load_per_node = [n.total_forwarded for n in self.nodes]

        # Jain's fairness index
        if load_per_node and sum(load_per_node) > 0:
            s = sum(load_per_node)
            s2 = sum(x * x for x in load_per_node)
            fairness = (s * s) / (len(load_per_node) * s2)
        else:
            fairness = 0.0

        results = {
            "strategy": self.strategy,
            "delivered": stats["delivered"],
            "dropped": stats["dropped"],
            "packet_delivery_ratio": stats["packet_delivery_ratio"],
            "avg_latency": stats["avg_latency"],
            "avg_hops": stats["avg_hops"],
            "total_energy": total_energy,
            "load_fairness": fairness,
            "final_alive_nodes": sum(1 for n in self.nodes if n.is_alive()),
        }
        return results