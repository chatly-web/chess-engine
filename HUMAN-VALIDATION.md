# Real-human match validation

At 2026-11-02T23:18:04.812050+05:30, BOT [ayushgohil](https://lichess.org/@/ayushgohil) was online and idle. Its checked public history returned zero completed games. **No human win rate or human playing-strength claim has been established.** Engine-versus-engine scores do not substitute for human results.

The private human trial uses `./engine/clash-history`, SHA256 `bb117a724f65b35ab376f14afee837870176b95962363d7afc170aa60b663444`, unchanged for both time controls. This is the original experimental history candidate, with all move selection and evaluation in C++. The public default remains the preceding conservative build; trial selection does not silently change that executable.

The single approved friend can challenge from their normal account: Standard chess, Casual, 10+5. Play normally without engine assistance. Start with one game, then reverse colours. A separate 3+2 test checks the same engine and bridge at the knockout clock. The BOT makes every move automatically; nobody should make human moves from its BOT account.

Save completed Lichess game links and results, noting opponent rating, colour, clock, disconnections and the frozen engine hash. A win against one friend does not establish results against stronger Chess Club members. Further consenting human opponents require explicit usernames for the private allowlist; automatic matchmaking stays disabled. No outgoing challenges were sent during preparation.

The hosting repair preserves the token-check retry body while redacting logs. Its offline regression tests passed, authentication and `bot:play` scope were checked, and the repaired bridge connected successfully. There is no bypass of permissions or third-party move source. The live game itself is still required to verify end-to-end moves, draws, clocks and outcomes.

Competition games must use the same submitted version in both stages, with no human modifications or advice during a game. Before submission, select one executable and align the bridge and stated launch command. The trial is preparation, not an extra engine submitted for the human stage.
