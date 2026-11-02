# Separate Lichess bridge utility fix

The competition engine is original C++. Hosting uses the separate [official lichess-bot bridge](https://github.com/lichess-bot-devs/lichess-bot), upstream revision `41266022bb881082b715b1ff080d3cee015fd12a` (observed version 2026.11.1.2). That utility is not bundled as our engine and is governed by its upstream GPL license.

Its retry callback used the original `details["kwargs"]` mapping for log redaction. After a transient token-check request failure, replacing `data` with a redaction placeholder also changed the arguments used for the next request. A valid token could then appear invalid. The local patch copies the outer details and keyword mapping before redaction. It preserves request data while retaining redacted logs. It does not bypass token/scope validation or change chess reasoning.

The local failure was reproduced with a dummy payload before the fix. Offline regression then verified unchanged retry arguments, no dummy secret in logs, an actual forced-timeout/retry sequence, and continued rejection of missing tokens or wrong scopes. Network calls are mocked; tests use no real credentials.

From an upstream checkout at the pinned revision, apply the provided `lichess-bot-retry-redaction.patch` with `git apply`, then use that bridge's Python environment to run:

```sh
python /path/to/chess-engine/source/bot_bridge/test_retry_redaction.py --bridge-root /path/to/lichess-bot
```

No populated config or token is provided. The patch is a declared adaptation of the separate bridge utility; no upstream chess search/evaluation code is copied into our engine. Account details and engine trial selection are described in the root `BOT-SETUP.md`. Running tests sends no challenge, move or message.

## Live challenge allowlist

`lichess-bot-live-allowlist.patch` adds an optional `challenge.allow_list_file` setting to the separate bridge. Copy `live_allowlist.py` into that bridge's `lib/` directory and apply the patch to the pinned upstream revision. Set the configuration key to an absolute path to a private JSON array of approved usernames. The list is read on every new incoming challenge; the chess engine and ongoing games are unaffected. An empty list denies all incoming challengers. Missing or malformed files fail closed. Username matching is case insensitive. Other challenge filters remain in force. Removing a name does not revoke an invitation already queued by the bridge.

Run the local access page with:

```sh
python access_manager.py --file /absolute/private/path/allowlist.json
```

It opens a loopback-only page with Add and Remove controls. The page has no Lichess credentials, never calls Lichess, and never sends challenges. It uses a per-launch private URL, validates Host and POST Origin, and atomically saves owner-only files. Only use it on a trusted local computer. Applying the bridge patch requires a one-time hosting restart **while idle, before event games**; later access edits require no restart. This hosting utility does not change the submitted C++ engine or the release ZIP. Existing mode, variant, clock and concurrency restrictions continue to apply. Previously rejected requests must be sent again.

Offline tests (using the bridge Python environment, no real Lichess requests):

```sh
python test_live_access.py --bridge-root /path/to/lichess-bot
```

These exercise the actual incoming challenge decision with one unchanged configuration instance, add/remove/case handling, human 10+5 and BOT 3+2 eligibility, retained rated/variant filters, empty/corrupt/missing-list rejection, file permissions and HTTP cross-origin protection.
