"""Mocked Lambda-to-Bedrock integration checks; no AWS calls or credentials.

Run from the repository root:
    python -m unittest discover -s aws/tests -v

These checks do not verify a live AWS deployment or model permissions.
"""

import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


spec = importlib.util.spec_from_file_location(
    "roofgrid_app", Path(__file__).resolve().parents[1] / "functions" / "app.py"
)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class BedrockIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.event = {
            "httpMethod": "POST",
            "path": "/api/ai",
            "body": json.dumps({"messages": [
                {"role": "system", "content": "Explain solar planning."},
                {"role": "user", "content": "What affects generation?"},
            ]}),
        }
        self.bedrock = Mock()
        self.bedrock.converse.return_value = {
            "output": {"message": {"content": [
                {"text": "Orientation and shade affect generation."}
            ]}},
            "usage": {"inputTokens": 12, "outputTokens": 8, "totalTokens": 20},
            "stopReason": "end_turn",
        }
        self.client = Mock(return_value=self.bedrock)
        self.sdk = patch.dict(sys.modules, {"boto3": SimpleNamespace(client=self.client)})
        self.sdk.start()
        self.addCleanup(self.sdk.stop)

    def test_chat_route_maps_request_and_response(self):
        with patch.object(app, "_consume_ai_quota", return_value=True):
            result = app.lambda_handler(self.event, None)
        self.assertEqual(result["statusCode"], 200)
        self.client.assert_called_once_with("bedrock-runtime")
        request = self.bedrock.converse.call_args.kwargs
        self.assertEqual(request["system"], [{"text": "Explain solar planning."}])
        self.assertEqual(request["messages"], [{
            "role": "user", "content": [{"text": "What affects generation?"}]
        }])
        payload = json.loads(result["body"])
        self.assertEqual(payload["choices"][0]["message"]["content"],
                         "Orientation and shade affect generation.")
        self.assertEqual(payload["usage"]["total_tokens"], 20)

    def test_daily_quota_blocks_bedrock(self):
        with patch.object(app, "_consume_ai_quota", return_value=False):
            result = app.lambda_handler(self.event, None)
        self.assertEqual(result["statusCode"], 429)
        self.client.assert_not_called()

    def test_unavailable_quota_blocks_bedrock(self):
        with patch.object(app, "_consume_ai_quota", return_value=None):
            result = app.lambda_handler(self.event, None)
        self.assertEqual(result["statusCode"], 503)
        self.client.assert_not_called()

    def test_access_denied_returns_service_unavailable(self):
        error = RuntimeError("mock access denied")
        error.response = {"Error": {"Code": "AccessDeniedException"}}
        self.bedrock.converse.side_effect = error
        with patch.object(app, "_consume_ai_quota", return_value=True):
            with self.assertLogs("roofgrid.aws", level="ERROR"):
                result = app.lambda_handler(self.event, None)
        self.assertEqual(result["statusCode"], 503)


if __name__ == "__main__":
    unittest.main()
