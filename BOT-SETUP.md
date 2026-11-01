# Competition hosting checklist

A dedicated BOT account has not yet been created. Offline engine tests do not replace a live Lichess connection test.

1. Create a dedicated unused Lichess account. Do not play a human game on it. Keep your normal account separate.
2. Create a private API token with only `bot:play`. Store it outside this repository. Never paste it into chat, commit it, or send it to organisers.
3. Install the official bridge from https://github.com/lichess-bot-devs/lichess-bot and follow its current setup instructions. Convert the dedicated account to BOT status using the bridge's documented upgrade command; conversion is permanent.
4. Build the engine on the competition machine with `./build-native.sh`, or use the included Apple Silicon executable on compatible macOS. In the bridge config set UCI, executable `clash-native`, and its `engine/` directory. This launch does not use the Python interpreter.
5. Disable online move sources, local/online tablebases, opening books and automatic matchmaking. Limit competition challenges to the permitted participants/organisers, standard chess, casual games and the event controls (3+2 and 10+5). The official bridge configuration remains the authority for current option names.
6. From your normal account challenge the BOT to casual games at both controls, with the engine playing both colours. Confirm it automatically accepts, starts, moves legally and completes games. Record game links and test the exact submitted executable. Do not make moves manually on the BOT account.
7. Create a separate `challenge:write` token for organisers, supplied through their designated private channel. Keep `bot:play` private. The public repository should contain neither token nor the populated bridge config.
8. Keep the hosting computer powered, awake, and connected. Check the announced round times, keep the bot available until every game finishes, and freeze the same executable for both stages. The rules prohibit altering, restarting or advising the engine during tournament games.
9. Submit the accessible repository, exact launch command, source, executable, dependencies/provenance README and BOT username. Use the earlier announced deadline, 2 November 23:59 IST. Confirm submission-channel details and acceptance of AI-assisted code with the organisers.

Repository ignores `config.yml`, `.env` and common token/secret names. This is not a substitute for inspecting staged files before pushing.
