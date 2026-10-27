"""Bits from natural-log probabilities. No I/O."""

from __future__ import annotations

import math
from collections.abc import Iterable

_LN2 = math.log(2)


def bits_from_logprobs(logprobs: Iterable[float | None]) -> list[float]:
    """Return -log2(p) for each token.

    A `None` logprob means nothing preceded that token; it contributes zero bits,
    which under-counts rather than guessing.
    """
    return [0.0 if lp is None else -lp / _LN2 for lp in logprobs]
