"""Apply the predeclared tactical-strength gate; never install an executable."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[4]
folder = root / 'strength-first-pass'


def read(path):
    return json.loads(path.read_text())


selection = read(folder / 'selection.json')
sha = selection['sha256']
name = selection['chosen']
report = {
    'candidate': selection,
    'production_sha256': hashlib.sha256((root / 'engine/clash-native').read_bytes()).hexdigest(),
    'recommended_action': 'retain-v08',
    'new_accuracy_measured': False,
    'guaranteed_winner': False,
}
expected = [f'candidate-gnu-{base}-{inc}-{colour}.json'
            for base, inc in [(180, 2), (600, 5)]
            for colour in ['white', 'black']]
missing = [f for f in ['confirmation.json', *expected] if not (folder / f).exists()]
if missing:
    report.update(status='awaiting-records', missing=missing)
else:
    confirmation = read(folder / 'confirmation.json')
    assert confirmation['binary_sha256']['candidate'] == sha
    comparison = confirmation['comparisons']['candidate']
    clocks = [read(folder / f) for f in expected]
    assert all(sha in v['source_hashes'].values() for v in clocks)
    ci = comparison['approximate_95_interval']
    gnu = confirmation['summary']['candidate']['GNUChess6.3']
    baseline_gnu = confirmation['summary']['baseline']['GNUChess6.3']
    checks = {
        'positive_fresh_matched_lower95': bool(ci and ci[0] > 0),
        'gnu_point_difference_nonnegative': comparison['per_opponent_difference']['GNUChess6.3'] >= 0,
        'gnu_wins_not_less_than_baseline': gnu['wins'] >= baseline_gnu['wins'],
        'standard_start_gnu_blitz_win': any(
            v['base'] == 180 and v['increment'] == 2 and not v['failure']
            and v['finished'] and v['result'] in ['1-0', '0-1']
            and ((v['result'] == '1-0') == (v['our_colour'] == 'white')) for v in clocks),
        'four_exact_clocks_finished_without_own_failure': all(
            v['finished'] and v.get('failure_side') != 'candidate' for v in clocks),
        'no_confirmation_technical_failures': not any(
            v['failures'] for summary in confirmation['summary'].values() for v in summary.values()),
        'complete_confirmation': len(confirmation['matches']) == 288
            and all(v['score'] is not None for v in confirmation['matches'])
            and comparison['matched_units'] == 72,
    }
    for kind in ['rules', 'protocol']:
        result = read(root / f'strength-first-{name}-{kind}.json')
        checks[f'{kind}_checks'] = result['native_binary_sha256'] == sha and result.get('passed', True)
        if kind == 'rules':
            checks['finite_rule_coverage'] = result['legal_positions'] == 2000 and result['tactical_move_sets_checked'] and result['perft_nodes'] == [197281, 97862, 43238]
    mates = read(folder / f'{name}-mates.json')
    checks['bounded_mates'] = mates['binary_sha256'] == sha and mates['passed'] == mates['tests'] == 84 and mates['failed'] == 0
    king = read(folder / 'king-defence.json')
    checks['finite_king_defence'] = king['binary_sha256'][name] == sha and king['summary'][name] == {'passes': 24, 'tests': 24}
    review = read(folder / 'source-review.json')
    checks['source_and_sanitizer_review'] = review['selected_sha256'] == sha and review['passed']
    checks['independent_artifact_audit'] = read(folder / 'artifact-audit.json')['passed']
    checks['human_prefix_split_audit'] = read(folder / 'starting-data-audit.json')['passed']
    passed = all(checks.values())
    report.update(status='complete', comparison=comparison, checks=checks,
                  gate_passed=passed, rejected_checks=[k for k, v in checks.items() if not v])
    if passed:
        report['recommended_action'] = 'candidate-qualified-pending-final-review'

(folder / 'qualification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
