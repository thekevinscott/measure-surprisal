"""The log2 per-token conversion. No I/O."""

import math

import pytest

from .bits_from_logprobs import bits_from_logprobs

HALF = -math.log(2)       # p = 1/2  -> 1 bit
QUARTER = -math.log(4)    # p = 1/4  -> 2 bits


def describe_bits_from_logprobs():
    def test_one_half_costs_one_bit():
        assert bits_from_logprobs([HALF]) == pytest.approx([1.0])

    def test_bits_preserve_token_order():
        assert bits_from_logprobs([HALF, QUARTER, HALF]) == pytest.approx([1.0, 2.0, 1.0])

    def test_certainty_costs_nothing():
        assert bits_from_logprobs([0.0]) == [0.0]

    def test_nothing_costs_nothing():
        assert bits_from_logprobs([]) == []

    def test_a_token_with_nothing_before_it_contributes_nothing():
        assert bits_from_logprobs([None, HALF]) == pytest.approx([0.0, 1.0])
