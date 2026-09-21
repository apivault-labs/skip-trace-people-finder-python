import unittest

from skip_trace import SkipTraceClient


class RecordingClient(SkipTraceClient):
    def __init__(self):
        self.payload = None
        self.actor_timeout = None

    def _execute(self, payload, actor_timeout_secs):
        self.payload = payload
        self.actor_timeout = actor_timeout_secs
        return [{"success": True, "bestPhone": "+12025550182"}]


class ClientContractTests(unittest.TestCase):
    def test_combined_payload_uses_current_public_contract(self):
        client = RecordingClient()
        rows = client.search(
            names=[" Jane Example; Springfield, IL "],
            emails=["jane@example.com"],
            max_results=3,
            output_preset="contacts",
            verify_emails=True,
        )
        self.assertEqual(rows[0]["success"], True)
        self.assertEqual(client.payload["workflow"], "combined")
        self.assertEqual(client.payload["name"], ["Jane Example; Springfield, IL"])
        self.assertEqual(client.payload["email"], ["jane@example.com"])
        self.assertEqual(client.payload["max_results"], 3)
        self.assertEqual(client.payload["outputPreset"], "contacts")
        self.assertIs(client.payload["useDemoOnEmpty"], False)
        self.assertNotIn("tier", client.payload)

    def test_invalid_or_empty_input_is_rejected_locally(self):
        client = RecordingClient()
        with self.assertRaises(ValueError):
            client.search()
        with self.assertRaises(ValueError):
            client.search(names=["Jane Example"], output_preset="unknown")

    def test_helpers_follow_matched_record_pricing(self):
        self.assertEqual(SkipTraceClient.estimate_cost(1000), 6.5)
        rows = [{"success": True}, {"success": False}]
        self.assertEqual(len(SkipTraceClient.filter_matches(rows)), 1)


if __name__ == "__main__":
    unittest.main()
