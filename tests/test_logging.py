import unittest
import logging
import json
import os
from unittest.mock import patch, MagicMock

from nexum.logging import (
    NexumLocalFormatter,
    NexumDatadogFormatter,
    NexumElasticFormatter,
    setup_logging,
)


class TestNexumLocalFormatter(unittest.TestCase):
    def test_local_formatter_output(self):
        formatter = NexumLocalFormatter("%(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="Mensagem de teste",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)

        self.assertIn("[Nexum]", output)
        self.assertIn("INFO", output)
        self.assertIn("Mensagem de teste", output)


class TestNexumDatadogFormatter(unittest.TestCase):
    @patch("nexum.logging.dd_tracer")
    def test_datadog_formatter_without_trace(self, mock_tracer):
        mock_tracer.current_span.return_value = None

        formatter = NexumDatadogFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname=__file__,
            lineno=10,
            msg="Teste DD",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        data = json.loads(output)

        self.assertEqual(data["level"], "WARNING")
        self.assertEqual(data["message"], "Teste DD")
        self.assertNotIn("dd.trace_id", data)

    @patch("nexum.logging.dd_tracer")
    def test_datadog_formatter_with_trace(self, mock_tracer):
        span = MagicMock()
        span.trace_id = 123
        span.span_id = 456
        mock_tracer.current_span.return_value = span

        formatter = NexumDatadogFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname=__file__,
            lineno=10,
            msg="Erro DD",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        data = json.loads(output)

        self.assertEqual(data["dd.trace_id"], 123)
        self.assertEqual(data["dd.span_id"], 456)


class TestNexumElasticFormatter(unittest.TestCase):
    @patch("nexum.logging.elasticapm")
    @patch("nexum.logging.execution_context")
    def test_elastic_formatter_with_trace(self, mock_exec, mock_elastic):
        mock_exec.get_trace_id.return_value = "abc123"
        mock_exec.get_transaction_id.return_value = "xyz789"

        formatter = NexumElasticFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="Elastic teste",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        data = json.loads(output)

        self.assertEqual(data["trace.id"], "abc123")
        self.assertEqual(data["transaction.id"], "xyz789")

    @patch("nexum.logging.elasticapm", None)
    def test_elastic_formatter_without_trace(self):
        formatter = NexumElasticFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="Sem APM",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        data = json.loads(output)

        self.assertEqual(data["message"], "Sem APM")
        self.assertNotIn("trace.id", data)
        self.assertNotIn("transaction.id", data)


class TestSetupLogging(unittest.TestCase):

    @patch("logging.getLogger")
    @patch("logging.StreamHandler")
    def test_setup_logging_user_defined_level(self, mock_handler, mock_logger):
        mock_logger.return_value = MagicMock(handlers=[])

        with patch.dict(os.environ, {"NEXUM_LOG_MODE": "LOCAL", "LOG_LEVEL": "WARNING"}):
            setup_logging()

        mock_logger.return_value.setLevel.assert_called_with("WARNING")

    @patch("logging.getLogger")
    @patch("logging.StreamHandler")
    def test_setup_logging_local_default_debug(self, mock_handler, mock_logger):
        mock_logger.return_value = MagicMock(handlers=[])

        with patch.dict(os.environ, {"NEXUM_LOG_MODE": "LOCAL"}, clear=True):
            setup_logging()

        mock_logger.return_value.setLevel.assert_called_with("DEBUG")

    @patch("logging.getLogger")
    @patch("logging.StreamHandler")
    def test_setup_logging_non_local_default_info(self, mock_handler, mock_logger):
        mock_logger.return_value = MagicMock(handlers=[])

        with patch.dict(os.environ, {"NEXUM_LOG_MODE": "DATADOG"}, clear=True):
            setup_logging()

        mock_logger.return_value.setLevel.assert_called_with("INFO")

    @patch("logging.getLogger")
    @patch("logging.StreamHandler")
    def test_setup_logging_datadog_formatter(self, mock_handler, mock_logger):
        mock_logger.return_value = MagicMock(handlers=[])

        with patch.dict(os.environ, {"NEXUM_LOG_MODE": "DATADOG"}):
            setup_logging()

        handler_instance = mock_handler.return_value
        handler_instance.setFormatter.assert_called()


if __name__ == "__main__":
    unittest.main()
