# Competition hosting status

Dedicated account: [ayushgohil](https://lichess.org/@/ayushgohil), permanently converted to **BOT** with the user's approval. The private `bot:play` token was validated and the official lichess-bot bridge connected successfully. No live game has completed yet; offline full-clock games are recorded in STRONG-SEARCH.md and the historical LONG-PASS.md.

The current local setup launches `engine/clash-native` directly with UCI. Python runs the bridge, not chess search. The private bridge configuration and token are stored outside this repository with owner-only permissions. Books, tablebases, online move sources, pondering, automatic matchmaking and automatic chat greetings are disabled. Incoming challenges are restricted to the single friend approved by the user. A local launcher prevents duplicate bridge instances and keeps the Mac awake while running.

## Remaining before the competition

1. While signed in as `ayushgohil`, set automatic threefold-draw claims to **Always** in [game preferences](https://lichess.org/account/preferences/game-behavior), then verify draw handling in a live test. The private `bot:play` token cannot read account preferences (HTTP 403), so this setting is not verified. Offline harnesses claim available draws automatically.
2. With the hosting Mac awake and connected, have the approved friend challenge `ayushgohil` to casual standard **3+2** and **10+5** games. Test both colours and record completed game links. Do not make human moves from the BOT account. No outgoing challenges have been sent by this setup.
3. Add the authorised competition accounts to the private challenge allowlist before the event. The current friend-only setting will reject other challengers. Check the bridge's allowed casual blitz/rapid controls against the event invitation.
4. Supply a separate token scoped only to `challenge:write` to organisers using their designated private channel. Keep `bot:play` private; neither token belongs in the repository, ZIP or chat.
5. Submit the accessible GitHub repository, BOT username, source, executable, dependencies and exact launch command `./engine/clash-native`. Use the announced deadline, **2 November, 23:59 IST**. Confirm the submission channel and acceptance of AI-assisted code with the organisers.
6. Freeze the same tested executable for both tournament stages. Keep the hosting machine powered, awake and connected until every game finishes. Do not change, restart or advise the engine during a tournament game.

## Hosting on another computer

Build using `./build-native.sh` with a C++17 compiler. The supplied executable is for Apple Silicon macOS; rebuild on Linux or Windows. Install the [official bridge](https://github.com/lichess-bot-devs/lichess-bot) separately and point its UCI engine configuration to this repository's absolute `engine/` directory and `clash-native` executable. Disable all external move sources and recreate the private credentials/configuration on that computer. Verify full live games before relying on it.

The local launcher and populated bridge configuration are machine-specific and intentionally excluded from this public repository. Repository ignore rules do not replace inspecting files before publishing.
