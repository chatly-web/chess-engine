# Research decisions behind this pass

The target is an original engine that plays reliably at 180+2 and 600+5 on the entrant's own machine. An algorithm is retained for measured results, rather than its name or the language model that wrote it.

| Approach | Decision for this event build |
|---|---|
| Random/greedy moves | Useful as a utility baseline; inadequate look-ahead. |
| Plain minimax | Correct adversarial framework; alpha-beta/PVS searches more selectively within the clock. |
| Alpha-beta/PVS with iterative deepening | Retain the existing original implementation, legal fallback and completed-iteration result on timeout. Transpositions, capture/history ordering, null moves and guarded reductions already exist. |
| Handcrafted evaluation | Retain original material, piece-square, pawn, mobility and king-safety terms as a tested reference. |
| Learned classical weights | Implemented from human final results with game-disjoint fitting/validation and fresh independent matches. Lower fitting loss alone did not qualify it for promotion. |
| Supervised neural value/policy | Permitted only with original data/weights. No pretrained engine network is imported. This pass does not claim to have trained a neural network. Replacing the evaluator would require another independent strength gate and C++ inference validation. |
| MCTS with self-play reinforcement learning | Research direction, not a completed feature. The AlphaZero result combines a trained neural network, millions of self-play games and substantial specialised hardware. Merely replacing alpha-beta with MCTS does not reproduce that evidence. |
| Multicore search | Implemented original root splitting with private tables and atomic bounds/stop signals; test exact binaries, because more hardware and more searched nodes do not automatically improve match results. |
| Dynamic clock allocation | Implemented an original bounded policy based on own search instability. The cited time-management abstract motivates the experiment; it is not a claim that this implementation reproduces the paper's gains. |

The competition's building guide explicitly presents the six approaches from random/greedy through neural evaluation and describes result-based classical fitting: [organiser guide](https://docs.google.com/document/d/1FfH7e7Njdvlk9aBPa-Cj13Jg0Igffu6rI1QIfsw7eag/edit). The restrictions on foreign engine code/analysis/weights and runtime books/tablebases are in the [competition rules](https://docs.google.com/document/d/1AUgyug3T_akye_rt3oEtTY7yXywO1AVG7TO77v9Py-g/edit).

[Silver et al., AlphaZero preprint](https://arxiv.org/abs/1712.01815) describes general self-play reinforcement learning. The authors' [full-evaluation explanation](https://deepmind.google/blog/alphazero-shedding-new-light-on-chess-shogi-and-go/) describes neural-guided MCTS, millions of training games, four first-generation TPUs and 44 CPU cores for match inference, and three-hour-plus-15-second tests. Those are different conditions from this Mac and the event. The decision to retain the existing C++ search is an engineering judgment for this project; the paper does not compare our implementations.

[Solak and Vuckovic, Time Management During a Chess Game](https://doi.org/10.3233/ICG-2009-32403), abstract consulted, reports experiments with six time models. We implemented our own soft/hard allocation and assessed it in actual-clock games; no existing engine code was copied.

[Lichess's own accuracy explanation](https://lichess.org/page/accuracy) says the metric is derived from Stockfish evaluations and depends on the positions/game. It is not a universal test grade or a tournament win probability. No new accuracy percentage is claimed for this pass, and no Stockfish evaluation dataset is used to train/tune the entrant. [Lichess game exports](https://database.lichess.org/) are available under CC0; the separately offered evaluation/puzzle labels were excluded.
