# Separate Lichess bridge utility fix

The competition engine is original C++. Hosting uses the separate [official lichess-bot bridge](https://github.com/lichess-bot-devs/lichess-bot), upstream revision `41266022bb881082b715b1ff080d3cee015fd12a` (observed version 2026.11.1.2). That utility is not bundled as our engine and is governed by its upstream GPL license.

Its retry callback used the original `details["kwargs"]` mapping for log redaction. After a transient token-check request failure, replacing `data` with a redaction placeholder also changed the arguments used for the next request. A valid token could then appear invalid. The local patch copies the outer details and keyword mapping before redaction. It preserves request data while retaining redacted logs. It does not bypass token/scope validation or change chess reasoning.

The local failure was reproduced with a dummy payload before the fix. Offline regression then verified unchanged retry arguments, no dummy secret in logs, an actual forced-timeout/retry sequence, and continued rejection of missing tokens or wrong scopes. Network calls are mocked; tests use no real credentials.

From an upstream checkout at the pinned revision, apply the provided `lichess-bot-retry-redaction.patch` with `git apply`, then use that bridge's Python environment to run:

```sh
python /path/to/chess-engine/source/bot_bridge/test_retry_redaction.py --bridge-root /path/to/lichess-bot
```

No populated config or token is provided. The patch is a declared adaptation of the separate bridge utility; no upstream chess search/evaluation code is copied into our engine. Account details and engine trial selection are described in the root `BOT-SETUP.md`. Running tests sends no challenge, move or message.
