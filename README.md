# measure_surprisal

Per-token surprisal in bits, optionally conditioned on a context.

```sh
uv run measure_surprisal "lazy dog" \
  --context "the brown fox jumped over the" \
  --base-url http://tower.tail790bbc.ts.net:8000/v1
```

```python
from measure_surprisal import Client, measure_surprisal

client = Client(base_url="http://tower:8000/v1")
pairs = await measure_surprisal("lazy dog", context="the brown fox jumped over the",
                                client=client)
total_bits = sum(bits for _, bits in pairs)
```

`Client` is the scorer: `base_url`, `api_key`, `model`. Bits are only comparable
within one scorer, so those three travel together rather than as loose kwargs,
and one client serves many measurements. `model` is optional when the server
serves exactly one. Everything is an explicit argument — no environment
variables.

`measure_surprisal.py` is the entry point: it decides which echoed tokens
belong to the text. Under `utils/`, `client.py` is a dumb pipe to the server
and `bits_from_logprobs.py` is the arithmetic.

Install the standalone package and development dependencies with `uv sync`.

Extracted from [`basharena_public/measure_surprisal`](https://github.com/thekevinscott/basharena_public/tree/1a9ad2d32241141e2abb600ced101e03e970dfc7/measure_surprisal)
at commit `1a9ad2d32241141e2abb600ced101e03e970dfc7`. The recorded fixtures are preserved; version 0.2 changes the return type. No license was specified in the source
repository at extraction; this extraction does not assign one.


## Breaking API change in 0.2.0

The async function now returns `list[tuple[str, float]]`, not a float.
The exported bits_from_logprobs helper likewise returns one float per input,
not a total; Echo now includes a tokens field.
Each pair contains the token string exactly as supplied by the server and its
surprisal in bits, in order. Callers needing a total sum the second elements.
A null logprob (normally the first token without preceding context) becomes
0.0 bits and retains its token. Tokens straddling the context boundary are
excluded, matching the previous total's boundary rule.

The CLI prints two lines: a JSON array with bits rounded to four decimal
places, followed by the total (computed from unrounded values) to four places.
For example, from a stubbed scorer:

```text
[["foo", 1.2346], [" bar", 0.5]]
1.7346
```

## Requires a server that echoes prompt logprobs

`context + text` goes out as one completion with `echo=true`; the text's tokens
are located by the server's `text_offset`. No local tokenizer is needed, but the
endpoint must return `logprobs.tokens`, `token_logprobs`, and `text_offset` for *prompt* tokens.

vLLM does. OpenAI's own API dropped it. llama.cpp's server does not, under any
flag — verified on build b9744 three ways (`echo`, `prompt_logprobs`, and native
`/completion` with `n_probs`). Against one of those you get `NoPromptLogprobs`.

`context` and `text` are concatenated exactly as given, so the separating space
is yours to place — and it matters. A token starting before `len(context)` is
charged to the context and excluded. The totals on Qwen2.5-0.5B are:

```
--context "the brown fox jumped over the"  "lazy dog"    12.5462   # "thelazy dog"
--context "the brown fox jumped over the"  " lazy dog"    0.4943   # right
--context "the brown fox jumped over the " "lazy dog"     0.0433   # " lazy" charged to the context
```

Bits are only comparable within one scorer. A 3B charges far more than
gpt-oss-120b for the same string, and a Q4 GGUF differs from the same model in
fp16.

## Tests

```sh
just test          # unit + integration, no network
just unit          # the per-token log2 conversion, colocated. no I/O.
just integration   # recorded fixtures through the real SDK over a local fake server
just e2e http://host:8000/v1 [model]   # against a live server

# the same, without just
uv run pytest        # e2e skips without --base-url
uv run pytest src
uv run pytest tests/integration
uv run pytest tests/e2e --base-url http://host:8000/v1
```

The e2e run must name its own directory: pytest only registers `--base-url` when
that conftest is an initial one. A repo-wide `pytest` skips e2e instead.

`tests/integration/__fixtures__/README.md` records which fixtures are real
recordings and which are hand-built.
