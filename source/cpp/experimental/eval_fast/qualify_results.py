"""Apply the fixed evaluation-efficiency gate. Never install an executable."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[4]
folder = root / 'eval-fast-pass'


def read(path):
    return json.loads(path.read_text())


selection = read(folder / 'selection.json')
sha = selection['sha256']
name = selection['chosen']
clock_files = [f'candidate-gnu-{base}-{inc}-{colour}.json'
               for base, inc in [(180, 2), (600, 5)] for colour in ['white', 'black']]
missing = [f for f in ['direct.json', 'external.json', 'external-resolved.json', *clock_files] if not (folder / f).exists()]
report = {'candidate': selection, 'recommended_action': 'retain-v08',
          'accuracy_measured': False, 'guaranteed_winner': False}
if missing:
    report.update(status='awaiting-records', missing=missing)
else:
    direct = read(folder / 'direct.json')
    external = read(folder / 'external-resolved.json')
    assert direct['binary_sha256']['candidate'] == external['binary_sha256']['candidate'] == sha
    clocks = [read(folder / f) for f in clock_files]
    assert all(sha in v['source_hashes'].values() for v in clocks)
    benchmark = read(folder / 'benchmark.json')
    equivalence = read(folder / 'evaluation-equivalence.json')
    search = read(folder / f'{name}-search-equivalence.json')
    ci = direct['approximate_95_interval']
    candidate_points = sum(v['points'] for v in external['summary']['candidate'].values())
    baseline_points = sum(v['points'] for v in external['summary']['baseline'].values())
    checks = {
        'fixed_depth_speed_ratio_at_least_1_15': benchmark['summary'][name]['median_speed_ratio'] >= 1.15,
        'positive_fresh_direct_lower95': bool(ci and ci[0] > .5),
        'complete_direct_batch': direct['games'] == direct['finished'] == 192 and direct['paired_units'] == 96 and direct['failures'] == 0,
        'external_points_not_less_than_baseline': candidate_points >= baseline_points,
        'gnu_wins_not_less_than_baseline': external['summary']['candidate']['GNUChess6.3']['wins'] >= external['summary']['baseline']['GNUChess6.3']['wins'],
        'complete_external_batch': len(external['matches']) == 96 and all(v['score'] is not None and not v['failure'] for v in external['matches']),
        'four_exact_clocks_finished_without_own_failure': all(v['finished'] and v['failure_side'] != 'candidate' for v in clocks),
        'finite_evaluation_equivalence': equivalence['passed'] and equivalence['positions'] == 10000 and equivalence['binary_sha256'][name] == sha,
        'finite_search_equivalence': search['passed'] and search['positions'] == 204 and search['candidate_sha256'] == sha,
        'source_and_sanitizer_review': read(folder / 'source-review.json')['passed'] and read(folder / 'source-review.json')['selected_sha256'] == sha,
        'starting_data_audit': read(folder / 'starting-data-audit.json')['passed'],
        'independent_results_audit': read(folder / 'artifact-audit.json')['passed'],
    }
    for kind in ['rules', 'protocol']:
        v = read(root / f'eval-fast-{name}-{kind}.json')
        checks[f'{kind}_checks'] = v['native_binary_sha256'] == sha and v.get('passed', True)
        if kind == 'rules':
            checks['finite_rule_coverage'] = v['legal_positions'] == 2000 and v['tactical_move_sets_checked'] and v['perft_nodes'] == [197281, 97862, 43238]
    mates = read(folder / 'selected-mates.json')
    checks['bounded_mates'] = mates['binary_sha256'] == sha and mates['passed'] == mates['tests'] == 84 and mates['failed'] == 0
    history = read(folder / 'selected-history.json')
    checks['history_boundaries'] = history['passed'] and any(v['sha256'] == sha for v in history['cases'])
    passed = all(checks.values())
    report.update(status='complete', checks=checks, gate_passed=passed,
                  rejected_checks=[k for k, v in checks.items() if not v],
                  direct_point_score=direct['paired_mean_point_score'],
                  direct_approximate_95_interval=ci,
                  external_candidate_points=candidate_points,
                  external_baseline_points=baseline_points)
    if passed:
        report['recommended_action'] = 'qualified-pending-final-review'

(folder / 'qualification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
