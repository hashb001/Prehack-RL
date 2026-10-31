"""Generate responses and collect probe records (shared by exp_02 and exp_03)."""
import random
from prehack.auditing.probes import run_probes
from prehack.tasks.arithmetic import make_problem, sample_response


def collect(seeds, problems_per_seed, responses_per_problem, judges,
            messy_rate=0.1, transformations=None) -> list[dict]:
    if problems_per_seed < 1 or responses_per_problem < 1 or not seeds or len(set(seeds)) != len(seeds):
        raise ValueError('Use positive counts and distinct seeds')
    if not 0.0 <= messy_rate <= 1.0:
        raise ValueError('messy_rate must be in [0, 1]')
    records = []
    for seed in seeds:
        rng = random.Random(seed)
        for i in range(problems_per_seed):
            problem = make_problem(rng, f'{seed}-{i}')
            for r in range(responses_per_problem):
                text = sample_response(problem, rng, messy_rate)
                for judge in judges:   # all judges see identical responses (paired design)
                    for rec in run_probes(problem, text, judge, transformations):
                        records.append({'seed': seed, 'response_index': r, **rec})
    return records
