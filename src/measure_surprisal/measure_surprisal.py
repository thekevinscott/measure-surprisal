"""Per-token surprisal in bits for a string, optionally conditioned on a context.

    client = Client(base_url="http://tower:8000/v1")
    pairs = await measure_surprisal("lazy dog", context="the brown fox jumped over the",
                                   client=client)

Sends `context + text` as one echoed prompt and locates the text's tokens by the
server's `text_offset`. Needs no local tokenizer.
"""

from __future__ import annotations

from bisect import bisect_left

from .utils.bits_from_logprobs import bits_from_logprobs
from .utils.client import Client

__all__ = ["measure_surprisal"]


async def measure_surprisal(text: str, *, context: str = "", client: Client) -> list[tuple[str, float]]:
    """Return (server token string, bits) pairs for `text` after `context`."""
    logprobs, offsets, tokens = await client.echo(context + text)
    if not len(logprobs) == len(offsets) == len(tokens):
        raise ValueError(f"{len(logprobs)} logprobs, {len(offsets)} offsets, {len(tokens)} tokens")
    # Offsets ascend, so this is the first token starting at or after the
    # boundary; one straddling it starts earlier and is charged to the context.
    start = bisect_left(offsets, len(context))
    return list(zip(tokens[start:], bits_from_logprobs(logprobs[start:])))
