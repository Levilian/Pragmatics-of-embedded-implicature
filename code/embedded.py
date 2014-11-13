#!/usr/bin/env python

import numpy as np
from pragmods import Pragmod, display_matrix
from lexica import Lexica
from itertools import product, combinations

p = r'$p$'
q = r'$q$'
pvq = r'$p \vee q$'
pq = r'$p \wedge q$'
NULL = r'$0$'
w1 = r'$w_{1}$'
w2 = r'$w_{2}$'
w3 = r'$w_{3}$'

msgs = [p, q, pvq, pq, NULL]
states = [w1, w2, w3]


def powerset(x, minsize=1, maxsize=None):
    result = []
    if maxsize == None: maxsize = len(x)
    for i in range(minsize, maxsize+1):
        for val in combinations(x, i):
            result.append(list(val))
    return result

def get_lexica(baselexicon):
    mats = []
    pvals = powerset(baselexicon[p])
    qvals = powerset(baselexicon[q])
    for pset, qset in product(pvals, qvals):
        newlex = {p: pset,
                  q: qset,
                  pvq: sorted(set(pset) | set(qset)),
                  pq: sorted(set(pset) & set(qset)),
                  NULL: states}
        mat = lex2mat(newlex)
        if 0.0 not in np.sum(mat, axis=1):
            mats.append(mat)        
    return mats

def lex2mat(lex):
    mat = np.zeros((len(msgs), len(states)))
    for i, msg in enumerate(msgs):
        for j, state in enumerate(states):
            if state in lex[msg]:
                mat[i, j] = 1.0                
    return mat

lexica = get_lexica({p: [w1, w2], q: [w1, w3]})

                        
for mat in lexica:
    display_matrix(mat, cnames=states, rnames=msgs)

print len(lexica)


mod = Pragmod(lexica=lexica,
              messages=msgs,
              meanings=states,
              costs=np.array([0.0, 0.0, 1.0, 1.0, 5.0]),
              prior=np.repeat(1.0/len(states), len(states)),
              lexprior=np.repeat(1.0/len(lexica), len(lexica)),
              temperature=1.0)

root = '/Volumes/CHRIS/Documents/research/embedded-scalars/Pragmatics-of-embedded-implicature/fig'
mod.plot_expertise_listener(n=3, output_filename=root + "/disj-listener.pdf")
mod.plot_expertise_speaker(n=3, lexsum=True, output_filename=root + "/disj-speaker.pdf")
