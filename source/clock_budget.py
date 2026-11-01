"""Conservative wall-clock allocation. All UCI inputs are milliseconds."""
def budget(args, white):
    if 'movetime' in args:
        available = max(0, args['movetime']) / 1000
        return max(0, available - min(.05, available * .2))
    clock = 'wtime' if white else 'btime'
    increment = 'winc' if white else 'binc'
    if clock not in args:
        return 86400 if 'depth' in args or 'nodes' in args else 1.0
    remaining = max(0, args[clock]) / 1000
    inc = max(0, args.get(increment, 0)) / 1000
    # Never spend the increment before it has actually arrived.
    reserve = min(.25, remaining * .2)
    spendable = max(0, remaining - reserve)
    horizon = max(1, args.get('movestogo', 30))
    target = remaining / horizon + .65 * inc
    return min(spendable, target, remaining * .25)
