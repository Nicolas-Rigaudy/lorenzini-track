"""Seeded random streams.

Each component (one shark's movement, one tag's transmissions, one receiver's uplink) draws
from its own stream, derived from the run seed and a label. Adding a shark or a receiver
therefore leaves every other stream, and its output, unchanged.
"""

import hashlib
import random


def stream(seed: int, *labels: object) -> random.Random:
    key = ":".join([str(seed), *(str(label) for label in labels)])
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))
