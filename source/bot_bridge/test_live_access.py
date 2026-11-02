"""Offline behavioral/security tests; no Lichess network calls."""
import argparse
from collections import Counter, defaultdict
import copy
import http.client
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.parse import urlsplit

from access_manager import make_server
from live_allowlist import read_usernames, update_usernames

parser = argparse.ArgumentParser()
parser.add_argument("--bridge-root", type=Path, required=True)
args, rest = parser.parse_known_args()
sys.path.insert(0, str(args.bridge_root.resolve()))
from lib.config import Configuration, insert_default_values
from lib.model import Challenge
from lib.blocklist import OnlineBlocklist


class AccessTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "access.json"
        self.path.write_text('["InitialUser"]')

    def tearDown(self):
        self.temp.cleanup()

    def test_update_validation_and_permissions(self):
        update_usernames(self.path, "SecondUser")
        update_usernames(self.path, "seconduser")
        self.assertEqual(read_usernames(self.path), ["InitialUser", "SecondUser"])
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        for name in ["*", "x", "../bad", "https://lichess.org/@/test", "two names", "<script>"]:
            with self.assertRaises(ValueError):
                update_usernames(self.path, name)
        update_usernames(self.path, "SECONDUSER", remove=True)
        self.assertEqual(read_usernames(self.path), ["InitialUser"])

    def test_reload_actual_challenge_decision(self):
        params = {"token": "", "url": "https://lichess.org", "engine": {}, "challenge": {}, "matchmaking": {}}
        insert_default_values(params)
        cfg = Configuration(params).challenge
        cfg.config.update(allow_list_file=str(self.path), accept_bot=True, modes=["casual"],
                          variants=["standard"], time_controls=["blitz", "rapid"], min_base=180,
                          max_base=600, min_increment=2, max_increment=5)
        event = {"id": "testtest", "rated": False, "variant": {"key": "standard"},
                 "perf": {"name": "Blitz"}, "speed": "blitz", "color": "white", "finalColor": "white",
                 "timeControl": {"type": "clock", "limit": 180, "increment": 2},
                 "challenger": {"name": "NewUser", "rating": 1500, "title": "BOT"}}
        profile = {"username": "OurBot"}
        def check(payload=event):
            return Challenge(payload, profile).is_supported(cfg, defaultdict(list), Counter(), OnlineBlocklist([]), profile)[0]
        self.assertFalse(check())
        update_usernames(self.path, "newuser")
        self.assertTrue(check())  # same Configuration instance, no restart/reload
        human = copy.deepcopy(event)
        human["challenger"].pop("title")
        human.update(speed="rapid")
        human["timeControl"].update(limit=600, increment=5)
        self.assertTrue(check(human))
        rated = copy.deepcopy(event); rated["rated"] = True
        self.assertFalse(check(rated))
        wrong = copy.deepcopy(event); wrong["variant"]["key"] = "atomic"
        self.assertFalse(check(wrong))
        update_usernames(self.path, "NewUser", remove=True)
        self.assertFalse(check())
        self.path.write_text('[]')
        self.assertFalse(check())  # empty list must never mean allow everyone
        self.path.write_text('broken')
        with self.assertLogs("lib.model", level="ERROR"):
            self.assertFalse(check())
        self.path.unlink()
        with self.assertLogs("lib.model", level="ERROR"):
            self.assertFalse(check())

    def test_http_access_and_csrf(self):
        server, url = make_server(self.path)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        parsed = urlsplit(url)
        origin = f"http://127.0.0.1:{server.server_port}"
        def request(method, path, headers=None, body=None):
            conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            conn.request(method, path, body=body, headers=headers or {})
            response = conn.getresponse(); data = response.read(); conn.close()
            return response.status, data
        try:
            self.assertEqual(request("GET", parsed.path)[0], 200)
            self.assertEqual(request("GET", "/users")[0], 403)
            self.assertEqual(request("GET", parsed.path, {"Host": "evil.example"})[0], 403)
            body = json.dumps({"username": "HttpUser"})
            self.assertEqual(request("POST", parsed.path + "add", body=body)[0], 403)
            headers = {"Origin": origin, "X-Access-Manager": "1", "Content-Type": "application/json"}
            self.assertEqual(request("POST", parsed.path + "add", headers, body)[0], 200)
            self.assertIn("HttpUser", read_usernames(self.path))
            headers["Origin"] = "https://evil.example"
            self.assertEqual(request("POST", parsed.path + "remove", headers, body)[0], 403)
            self.assertIn("HttpUser", read_usernames(self.path))
        finally:
            server.shutdown(); server.server_close(); thread.join()


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0], *rest])
