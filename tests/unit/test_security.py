import socket
from pathlib import Path
from unittest.mock import patch
import pytest

from monopoly.cli.models import RunConfig
from monopoly.cli.cli import process_statement

def test_no_network_calls_during_processing():
    """
    Security Audit Test:
    Ensures that processing a statement does not attempt to open any network sockets.
    This validates that the tool is local-only and does not transmit PII.
    """

    # Configure the run
    # We use pprint=True to avoid writing to disk, although writing to disk is also a local op.
    config = RunConfig(
        output_directory=Path("/tmp"),
        pprint=True,
        safety_check=True,
        use_ocr=False
    )

    example_file = Path("src/monopoly/examples/example_statement.pdf")

    # Patch socket.socket to fail if called
    with patch("socket.socket", side_effect=RuntimeError("Network access attempted!")) as mock_socket:

        result = process_statement(example_file, config)

        # Verify socket was never initialized
        assert mock_socket.call_count == 0, "Socket initialized during processing, indicating potential network activity"

        # If result is returned (it might be None if pprint is True), check for errors
        if result and result.error_info:
             if "Network access attempted!" in result.error_info.get("message", ""):
                 pytest.fail("Network access was attempted during processing!")
