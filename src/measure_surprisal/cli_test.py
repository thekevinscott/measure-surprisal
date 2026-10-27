"""CLI formatting without a scorer."""

from unittest.mock import AsyncMock

from . import cli


def test_cli_prints_pairs_then_total(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["measure_surprisal", "foo bar", "--base-url", "http://unused/v1"])
    monkeypatch.setattr(cli, "Client", lambda **kwargs: object())
    monkeypatch.setattr(cli, "measure_surprisal", AsyncMock(return_value=[("foo", 1.234567), (" bar", 0.5)]))
    cli.main()
    assert capsys.readouterr().out == '[["foo", 1.2346], [" bar", 0.5]]\n1.7346\n'
