import csv
from collections import defaultdict
import cPickle as pickle
from scipy import stats
import numpy as np

sentences = {
    "Every player hit all of his shots": "every(player)(made(every(shot)))",
    "Every player hit none of his shots": "every(player)(made(no(shot)))",    
    "Every player hit some of his shots": "every(player)(made(some(shot)))",    
    "Exactly one player hit all of his shots": "exactly_one(player)(made(every(shot)))",
    "Exactly one player hit none of his shots": "exactly_one(player)(made(no(shot)))",
    "Exactly one player hit some of his shots": "exactly_one(player)(made(some(shot)))",
    "No player hit all of his shots": "no(player)(made(every(shot)))",
    "No player hit none of his shots": "no(player)(made(no(shot)))",
    "No player hit some of his shots": "no(player)(made(some(shot)))"
}

condition_map = {
    "none-none-none": "NNN",
    "none-none-half": "NNS",
    "none-none-all": "NNA",
    "none-half-half": "NSS",
    "none-half-all": "NSA",                         
    "none-all-all": "NAA",
    "half-half-half": "SSS",
    "half-half-all": "SSA",
    "half-all-all": "SAA",
    "all-all-all": "AAA"
}

def get_responses(src_filename="../data/basketball-pilot-2-11-14-results-parsed.csv"):
    data = defaultdict(lambda : defaultdict(list))
    for d in csv.DictReader(file(src_filename)):
        sentence = d['sentence']
        if sentence in sentences:
            sentence = sentences[d['sentence']]
            condition = condition_map[d['condition']]
            response = float(d['response'])
            data[sentence][condition].append(response)
    return data

def process_responses(data, output_filename="../data/basketball-pilot-2-11-14-results-parsed.pickle"):
    results = defaultdict(dict)
    for sentence, cond_dist in data.items():
        for cond, vals in cond_dist.items():
            results[sentence][cond] = (np.mean(vals), get_ci(vals))
    pickle.dump(results, file(output_filename, 'w'), 2)


def get_ci(vals):
    loc = np.mean(vals)
    scale = np.std(vals) / np.sqrt(len(vals))
    return stats.t.interval(0.95, len(vals)-1, loc=loc, scale=scale)

process_responses(get_responses())

