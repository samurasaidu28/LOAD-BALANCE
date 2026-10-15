"""
AI Load-Balancing Module
Uses a lightweight Scikit-learn model (Decision Tree or Random Forest)
to select the best next-hop peer based on multiple features.
"""

from __future__ import annotations
import random
from typing import List, Optional, Dict
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os
import config
from src.nodes import PeerNode


class AILoadBalancer:
    def __init__(self, model_type: str = config.AI_MODEL_TYPE):
        self.model_type = model_type
        self.model = None
        self.feature_names = config.FEATURE_COLUMNS
        self.is_trained = False

        if model_type == "decision_tree":
            self.model = DecisionTreeClassifier(
                max_depth=6, min_samples_leaf=5, random_state=config.RANDOM_SEED
            )
        else:
            self.model = RandomForestClassifier(
                n_estimators=50,
                max_depth=8,
                min_samples_leaf=4,
                random_state=config.RANDOM_SEED,
                n_jobs=-1,
            )

    def _generate_synthetic_training_data(self, n_samples: int = config.TRAINING_SAMPLES):
        """
        Generate realistic synthetic training data that reflects
        good vs bad forwarding decisions in a rural P2P setting.
        Label = 1 means "good choice", 0 means "poor choice".
        """
        X = []
        y = []

        for _ in range(n_samples):
            battery = random.uniform(0.0, 1.0)
            signal = random.uniform(0.2, 1.0)
            bandwidth = random.uniform(0.3, 1.2)
            reliability = random.uniform(0.3, 1.0)
            queue = random.uniform(0.0, 1.0)
            success = random.uniform(0.2, 1.0)

            # Heuristic score that defines a "good" peer
            score = (
                0.30 * battery
                + 0.20 * signal
                + 0.15 * bandwidth
                + 0.20 * reliability
                + 0.10 * (1.0 - queue)
                + 0.05 * success
            )

            # Add some noise
            label = 1 if score + random.uniform(-0.1, 0.1) > 0.55 else 0

            X.append([battery, signal, bandwidth, reliability, queue, success])
            y.append(label)

        return np.array(X), np.array(y)

    def train(self, force_retrain: bool = False):
        """Train (or load) the model."""
        model_path = os.path.join(config.DATA_DIR, "ai_model.joblib")

        if os.path.exists(model_path) and not force_retrain:
            self.model = joblib.load(model_path)
            self.is_trained = True
            print(f"[AI] Loaded existing model from {model_path}")
            return

        print("[AI] Generating synthetic training data...")
        X, y = self._generate_synthetic_training_data()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=config.RANDOM_SEED
        )

        self.model.fit(X_train, y_train)
        acc = accuracy_score(y_test, self.model.predict(X_test))
        print(f"[AI] Model trained. Validation accuracy: {acc:.3f}")

        os.makedirs(config.DATA_DIR, exist_ok=True)
        joblib.dump(self.model, model_path)
        self.is_trained = True

    def predict_score(self, features: Dict[str, float]) -> float:
        """Return probability that this node is a good choice."""
        if not self.is_trained:
            self.train()

        vec = np.array([[features[f] for f in self.feature_names]])
        # Probability of class 1 (good)
        proba = self.model.predict_proba(vec)[0][1]
        return float(proba)

    def select_peer(
        self, candidates: List[PeerNode], exclude: Optional[str] = None
    ) -> Optional[PeerNode]:
        """
        Select the best peer from the candidate list using the AI model.
        Returns None if no suitable candidate exists.
        """
        if not candidates:
            return None

        best_node = None
        best_score = -1.0

        for node in candidates:
            if exclude and node.node_id == exclude:
                continue
            if not node.can_forward():
                continue

            features = node.get_features()
            score = self.predict_score(features)

            # Small random tie-breaker
            score += random.uniform(0, 0.01)

            if score > best_score:
                best_score = score
                best_node = node

        return best_node