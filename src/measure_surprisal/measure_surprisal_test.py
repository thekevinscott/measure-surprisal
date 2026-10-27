"""Which of the echoed tokens belong to the text."""

import math

import pytest

from .measure_surprisal import measure_surprisal
from .utils.client import Echo

HALF = -math.log(2)       # p = 1/2  -> 1 bit
QUARTER = -math.log(4)    # p = 1/4  -> 2 bits


class Server:
    """Returns the echo the test names, and records what it was asked to price."""

    def __init__(self, echo: Echo):
        self.echo_ = echo
        self.prompts: list[str] = []

    async def echo(self, prompt: str) -> Echo:
        self.prompts.append(prompt)
        return self.echo_


def describe_measure_surprisal():
    async def test_every_token_counts_without_a_context():
        client = Server(Echo([HALF, QUARTER], [0, 4], ["abcd", "efg"]))

        assert await measure_surprisal("abcdefg", client=client) == [("abcd", 1.0), ("efg", 2.0)]

    async def test_the_context_is_prepended_to_the_scored_prompt():
        client = Server(Echo([HALF], [0], ["the dog"]))

        await measure_surprisal("dog", context="the ", client=client)

        assert client.prompts == ["the dog"]

    async def test_a_ragged_server_response_raises_rather_than_truncating():
        client = Server(Echo([HALF], [0, 1], ["a"]))

        with pytest.raises(ValueError):
            await measure_surprisal("ab", client=client)

    def describe_with_a_context():
        async def test_tokens_before_the_boundary_are_excluded():
            client = Server(Echo([HALF, QUARTER], [0, 3], ["abc", "x"]))

            assert await measure_surprisal("x", context="abc", client=client) == [("x", 2.0)]

        async def test_a_token_straddling_the_boundary_is_charged_to_the_context():
            # starts at 2, context is 3 chars: it spans the seam, so it is not counted.
            client = Server(Echo([HALF, QUARTER], [0, 2], ["ab", "cx"]))

            assert await measure_surprisal("x", context="abc", client=client) == []


async def test_first_token_without_context_has_zero_bits():
    client = Server(Echo([None, HALF], [0, 3], ["foo", "bar"]))
    assert await measure_surprisal("foobar", client=client) == [("foo", 0.0), ("bar", 1.0)]


async def test_mismatched_token_count_is_rejected():
    client = Server(Echo([HALF], [0], []))
    with pytest.raises(ValueError):
        await measure_surprisal("a", client=client)
