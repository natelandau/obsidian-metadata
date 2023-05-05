# type: ignore
"""Test alerts and logging."""
import re

import pytest

from obsidian_metadata._utils import alerts
from obsidian_metadata._utils.alerts import logger as log
from tests.helpers import Regex, strip_ansi


def test_dryrun(capsys):
    """Test dry run."""
    alerts.dryrun("This prints in dry run")
    captured = strip_ansi(capsys.readouterr().out)
    assert captured == "DRYRUN   | This prints in dry run\n"


def test_success(capsys):
    """Test success."""
    alerts.success("This prints in success")
    captured = strip_ansi(capsys.readouterr().out)
    assert captured == "SUCCESS  | This prints in success\n"


def test_error(capsys):
    """Test success."""
    alerts.error("This prints in error")
    captured = strip_ansi(capsys.readouterr().out)
    assert captured == "ERROR    | This prints in error\n"


def test_warning(capsys):
    """Test warning."""
    alerts.warning("This prints in warning")
    captured = strip_ansi(capsys.readouterr().out)
    assert captured == "WARNING  | This prints in warning\n"


def test_notice(capsys):
    """Test notice."""
    alerts.notice("This prints in notice")
    captured = strip_ansi(capsys.readouterr().out)
    assert captured == "NOTICE   | This prints in notice\n"


def test_alerts_debug(capsys):
    """Test debug."""
    alerts.debug("This prints in debug")
    captured = strip_ansi(capsys.readouterr().out)
    assert captured == "DEBUG    | This prints in debug\n"


def test_usage(capsys):
    """Test usage."""
    alerts.usage("This prints in usage")
    captured = strip_ansi(capsys.readouterr().out)
    assert captured == "USAGE    | This prints in usage\n"

    alerts.usage(
        "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua",
        width=80,
    )
    captured = strip_ansi(capsys.readouterr().out)
    assert "USAGE    | Lorem ipsum dolor sit amet" in captured
    assert "         | incididunt ut labore et dolore magna aliqua" in captured

    alerts.usage(
        "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua",
        width=20,
    )
    captured = strip_ansi(capsys.readouterr().out)
    assert "USAGE    | Lorem ipsum dolor" in captured
    assert "         | sit amet," in captured
    assert "         | adipisicing elit," in captured


def test_info(capsys):
    """Test info."""
    alerts.info("This prints in info")
    captured = strip_ansi(capsys.readouterr().out)
    assert captured == "INFO     | This prints in info\n"


def test_dim(capsys):
    """Test info."""
    alerts.dim("This prints in dim")
    captured = strip_ansi(capsys.readouterr().out)
    assert captured == "This prints in dim\n"


@pytest.mark.parametrize(
    ("verbosity", "log_to_file"),
    [(0, False), (1, False), (2, True), (3, True)],
)
def test_logging(capsys, tmp_path, verbosity, log_to_file) -> None:
    """Test logging."""
    tmp_log = tmp_path / "tmp.log"
    logging = alerts.LoggerManager(
        log_file=tmp_log,
        verbosity=verbosity,
        log_to_file=log_to_file,
    )

    assert logging.verbosity == verbosity

    if verbosity >= 3:
        assert logging.is_trace() is True
        captured = strip_ansi(capsys.readouterr().out)
        assert not captured

        assert logging.is_trace("trace text") is True
        captured = strip_ansi(capsys.readouterr().out)
        assert captured == "trace text\n"

        log.trace("This is Trace logging")
        cap_error = strip_ansi(capsys.readouterr().err)
        assert cap_error == Regex(r"^TRACE    \| This is Trace logging \([\w\._:]+:\d+\)$")
    else:
        assert logging.is_trace("trace text") is False
        captured = strip_ansi(capsys.readouterr().out)
        assert captured != "trace text\n"

        log.trace("This is Trace logging")
        cap_error = strip_ansi(capsys.readouterr().err)
        assert cap_error != Regex(r"^TRACE    \| This is Trace logging \([\w\._:]+:\d+\)$")

    if verbosity >= 2:
        assert logging.is_debug() is True
        captured = strip_ansi(capsys.readouterr().out)
        assert not captured

        assert logging.is_debug("debug text") is True
        captured = strip_ansi(capsys.readouterr().out)
        assert captured == "debug text\n"

        log.debug("This is Debug logging")
        captured = strip_ansi(capsys.readouterr().err)
        assert captured == Regex(r"^DEBUG    \| This is Debug logging \([\w\._:]+:\d+\)$")
    else:
        assert logging.is_debug("debug text") is False
        captured = strip_ansi(capsys.readouterr().out)
        assert captured != "debug text\n"

        log.debug("This is Debug logging")
        captured = strip_ansi(capsys.readouterr().err)
        assert captured != Regex(r"^DEBUG    \| This is Debug logging \([\w\._:]+:\d+\)$")

    if verbosity >= 1:
        assert logging.is_info() is True
        captured = strip_ansi(capsys.readouterr().out)
        assert not captured

        assert logging.is_info("info text") is True
        captured = strip_ansi(capsys.readouterr().out)
        assert captured == "info text\n"

        log.info("This is Info logging")
        captured = strip_ansi(capsys.readouterr().err)
        assert captured == "INFO     | This is Info logging\n"
    else:
        assert logging.is_info("info text") is False
        captured = strip_ansi(capsys.readouterr().out)
        assert captured != "info text\n"

        log.info("This is Info logging")
        captured = strip_ansi(capsys.readouterr().out)
        assert not captured

    assert logging.is_default() is True
    captured = strip_ansi(capsys.readouterr().out)
    assert not captured

    assert logging.is_default("default text") is True
    captured = strip_ansi(capsys.readouterr().out)
    assert captured == "default text\n"

    if log_to_file:
        assert tmp_log.exists() is True
        log_file_content = tmp_log.read_text()
        assert log_file_content == Regex(
            r"^\d{4}-\d{2}-\d{2} \d+:\d+:\d+\.\d+ \| DEBUG    \| [\w\.:]+:\d+ \- Logging to file:",
            re.MULTILINE,
        )
    else:
        assert tmp_log.exists() is False
