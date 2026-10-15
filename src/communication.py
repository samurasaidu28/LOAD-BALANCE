"""
Peer-to-Peer Communication Module
Implements simple store-and-forward (DTN-style) message transfer.
"""

from __future__ import annotations
from typing import Optional, List, Dict
from src.nodes import PeerNode, Message
from src.network import Network
import config
import uuid
import random


class CommunicationLayer:
    def __init__(self, network: Network):
        self.network = network
        self.delivered: List[Message] = []
        self.dropped: List[Message] = []
        self.in_transit: Dict[str, Message] = {}  # msg_id -> Message

    def create_message(self, source: PeerNode, dest_id: str) -> Message:
        msg = Message(
            msg_id=str(uuid.uuid4())[:8],
            source_id=source.node_id,
            dest_id=dest_id,
            size_kb=config.PACKET_SIZE,
            created_at=self.network.time,
        )
        msg.path.append(source.node_id)
        return msg

    def try_forward(
        self,
        current: PeerNode,
        msg: Message,
        next_hop: Optional[PeerNode],
    ) -> bool:
        """
        Attempt to forward a message to the chosen next hop.
        Returns True if successful.
        """
        if next_hop is None or not next_hop.can_forward():
            return False

        # Check if still neighbours (link may have broken)
        if next_hop.node_id not in current.neighbours:
            return False

        # Simulate transmission
        current.transmit(msg)
        next_hop.receive(msg)

        # Update reliability of current node
        current.update_reliability(success=True)

        # If destination reached
        if next_hop.node_id == msg.dest_id:
            self.delivered.append(msg)
            if msg in next_hop.queue:
                next_hop.queue.remove(msg)
            return True

        return True

    def drop_message(self, msg: Message, reason: str = "no_route"):
        self.dropped.append(msg)

    def get_stats(self) -> Dict:
        total = len(self.delivered) + len(self.dropped)
        pdr = len(self.delivered) / total if total > 0 else 0.0
        avg_latency = 0.0
        avg_hops = 0.0
        if self.delivered:
            avg_latency = sum(
                (self.network.time - m.created_at) for m in self.delivered
            ) / len(self.delivered)
            avg_hops = sum(m.hops for m in self.delivered) / len(self.delivered)

        return {
            "delivered": len(self.delivered),
            "dropped": len(self.dropped),
            "packet_delivery_ratio": pdr,
            "avg_latency": avg_latency,
            "avg_hops": avg_hops,
        }