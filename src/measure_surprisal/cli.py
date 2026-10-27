"""Print per-token bits as JSON, then their total.

measure_surprisal "the string" --context "what comes before" --base-url URL
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from openai import APIConnectionError

from .utils.client import Client
from .measure_surprisal import measure_surprisal


def main() -> None:
    p = argparse.ArgumentParser(prog="measure_surprisal", description=__doc__)
    p.add_argument("text", help="the string to price, in bits")
    p.add_argument("--context", default="", help="what the model reads first")
    p.add_argument("--base-url", required=True, help="OpenAI-compatible endpoint, e.g. http://host:8000/v1")
    p.add_argument("--model", help="defaults to the server's model when it serves exactly one")
    p.add_argument("--api-key", default="EMPTY")
    args = p.parse_args()

    try:
        client = Client(base_url=args.base_url, model=args.model, api_key=args.api_key)
        pairs = asyncio.run(measure_surprisal(args.text, context=args.context, client=client))
    except APIConnectionError:
        sys.exit(f"measure_surprisal: could not reach {args.base_url} -- is the server up?")
    except Exception as exc:
        sys.exit(f"measure_surprisal: {exc}")

    print(json.dumps([(token, round(bits, 4)) for token, bits in pairs], ensure_ascii=False))
    print(f"{sum(bits for _, bits in pairs):.4f}")
