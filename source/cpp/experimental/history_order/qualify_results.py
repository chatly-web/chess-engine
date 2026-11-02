"""Apply the predeclared history-search gate. Never install an executable."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[4]
folder = root / 'history-pass'


def read(path):
    return json.loads(path.read_text())


selection = read(folder / 'selection.json')
sha = selection['sha256']
name = selection['chosen']
clock_files = [f'candidate-gnu-{b}-{i}-{c}.json'
               for b, i in [(180, 2), (600, 5)] for c in ['white', 'black']]
missing = [f for f in ['direct-fast.json', 'direct-old.json', 'replication-fast.json', 'fast-replication-summary.json', 'external.json', *clock_files]
           if not (folder / f).exists()]
report = {'candidate': selection, 'recommended_action': 'retain-existing-builds',
          'accuracy_measured': False, 'guaranteed_winner': False}
if missing:
    report.update(status='awaiting-records', missing=missing)
else:
    fast = read(folder / 'direct-fast.json')
    old = read(folder / 'direct-old.json')
    external = read(folder / 'external.json')
    replication = read(folder / 'replication-fast.json')
    pooled = read(folder / 'fast-replication-summary.json')
    assert fast['binary_sha256']['candidate'] == old['binary_sha256']['candidate'] == external['binary_sha256']['candidate'] == sha
    clocks = [read(folder / f) for f in clock_files]
    assert all(sha in v['source_hashes'].values() for v in clocks)
    assert replication['binary_sha256']['candidate'] == pooled['binary_sha256']['candidate'] == sha
    ci = pooled['corrected_97_5_interval']
    cp = sum(v['points'] for v in external['summary']['candidate'].values())
    bp = sum(v['points'] for v in external['summary']['baseline'].values())
    checks = {
        'positive_pooled_fast_corrected_lower97_5': bool(ci and ci[0] > .5),
        'nonnegative_v08_shadow_score': old['paired_mean_point_score'] >= .5,
        'complete_direct_fast': fast['games'] == fast['finished'] == 128 and fast['paired_units'] == 64 and fast['failures'] == 0,
        'complete_direct_old': old['games'] == old['finished'] == 64 and old['paired_units'] == 32 and old['failures'] == 0,
        'complete_fixed_replication': replication['games'] == replication['finished'] == 128 and replication['failures'] == 0 and pooled['pairs'] == 128 and pooled['games'] == pooled['finished'] == 256,
        'replication_split_audit': read(folder / 'replication-starting-data-audit.json')['passed'],
        'external_points_not_less_than_fast': cp >= bp,
        'gnu_wins_not_less_than_fast': external['summary']['candidate']['GNUChess6.3']['wins'] >= external['summary']['baseline']['GNUChess6.3']['wins'],
        'complete_external': len(external['matches']) == 128 and all(v['score'] is not None and not v['failure'] for v in external['matches']),
        'both_colours_both_clocks_without_own_failure': all(v['finished'] and v['failure_side'] != 'candidate' for v in clocks),
        'source_and_sanitizer_review': read(folder / 'source-review.json')['passed'] and read(folder / 'source-review.json')['selected_sha256'] == sha,
        'starting_data_audit': read(folder / 'starting-data-audit.json')['passed'],
        'independent_result_audit': read(folder / 'artifact-audit.json')['passed'],
    }
    for kind in ['rules', 'protocol']:
        v = read(root / f'history-{name}-{kind}.json')
        checks[kind] = v['native_binary_sha256'] == sha and v.get('passed', True)
        if kind == 'rules':
            checks['finite_rule_coverage'] = v['legal_positions'] == 2000 and v['tactical_move_sets_checked'] and v['perft_nodes'] == [197281, 97862, 43238]
    mates = read(folder / 'selected-mates.json')
    history = read(folder / 'selected-history.json')
    checks['bounded_mates'] = mates['binary_sha256'] == sha and mates['passed'] == mates['tests'] == 84 and mates['failed'] == 0
    checks['history_boundaries'] = history['passed'] and any(v['sha256'] == sha for v in history['cases'])
    passed = all(checks.values())
    report.update(status='complete', checks=checks, gate_passed=passed,
                  rejected_checks=[k for k, v in checks.items() if not v],
                  fast_initial_score=fast['paired_mean_point_score'], fast_pooled_score=pooled['mean_point_score'], fast_corrected_97_5_interval=ci,
                  old_score=old['paired_mean_point_score'], candidate_external_points=cp,
                  fast_external_points=bp)
    if passed:
        report['recommended_action'] = 'qualified-pending-final-review'

(folder / 'qualification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
