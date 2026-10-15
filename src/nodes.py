"""
Peer Node model
Represents a mobile device in the rural P2P network.
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import random
import config


@dataclass
class Message:
    msg_id: str
    source_id: str
    dest_id: str
    size_kb: float
    created_at: float
    hops: int = 0
    path: List[str] = field(default_factory=list)


@dataclass
class PeerNode:
    node_id: str
    x: float
    y: float
    battery: float = config.INITIAL_BATTERY
    speed: float = 0.0
    destination: Optional[tuple] = None
    pause_until: float = 0.0

    # Network state
    signal_strength: float = 1.0          # 0.0 – 1.0
    available_bandwidth: float = config.BASE_BANDWIDTH
    queue: List[Message] = field(default_factory=list)
    reliability: float = 0.8              # historical success rate
    recent_successes: int = 0
    recent_attempts: int = 0
    total_forwarded: int = 0
    total_received: int = 0
    energy_used: float = 0.0

    # Neighbours (updated by discovery)
    neighbours: Dict[str, float] = field(default_factory=dict)  # node_id -> distance

    def is_alive(self) -> bool:
        return self.battery > 0

    def can_forward(self) -> bool:
        return self.battery >= config.MIN_BATTERY_TO_FORWARD and self.is_alive()

    def update_battery(self, drain: float):
        self.battery = max(0.0, self.battery - drain)
        self.energy_used += drain

    def transmit(self, msg: Message):
        """Simulate transmission cost."""
        self.update_battery(config.BATTERY_DRAIN_TX)
        self.total_forwarded += 1
        msg.hops += 1
        msg.path.append(self.node_id)

    def receive(self, msg: Message):
        """Simulate reception cost."""
        self.update_battery(config.BATTERY_DRAIN_RX)
        self.total_received += 1
        self.queue.append(msg)

    def idle_drain(self, dt: float):
        self.update_battery(config.BATTERY_DRAIN_IDLE * dt)

    def update_reliability(self, success: bool):
        self.recent_attempts += 1
        if success:
            self.recent_successes += 1
        # Exponential moving average
        rate = self.recent_successes / max(1, self.recent_attempts)
        self.reliability = 0.7 * self.reliability + 0.3 * rate

    def get_features(self) -> Dict[str, float]:
        """Features used by the AI load balancer."""
        success_rate = (
            self.recent_successes / self.recent_attempts
            if self.recent_attempts > 0 else self.reliability
        )
        return {
            "battery_level": self.battery / 100.0,
            "signal_strength": self.signal_strength,
            "available_bandwidth": self.available_bandwidth / config.BASE_BANDWIDTH,
            "node_reliability": self.reliability,
            "queue_length": len(self.queue) / 20.0,  # normalised
            "recent_success_rate": success_rate,
        }

    def distance_to(self, other: "PeerNode") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


def create_nodes(num_nodes: int = config.NUM_NODES) -> List[PeerNode]:
    """Create a list of peer nodes randomly placed in the area."""
    nodes = []
    for i in range(num_nodes):
        node = PeerNode(
            node_id=f"N{i:03d}",
            x=random.uniform(0, config.AREA_SIZE),
            y=random.uniform(0, config.AREA_SIZE),
            battery=random.uniform(60, 100),
            reliability=random.uniform(0.6, 0.95),
            signal_strength=random.uniform(0.5, 1.0),
            available_bandwidth=config.BASE_BANDWIDTH * random.uniform(0.6, 1.2),
        )
        nodes.append(node)
    return nodes