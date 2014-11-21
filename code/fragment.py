#!/usr/bin/env python

import sys
import itertools
import numpy as np
from utils import NULL

######################################################################

a = 'a'; b = 'b'; c = 'c'
s1 = 's1' ; s2 = 's2'

TYPE_WX = "wx"
TYPE_WEET = "weet"
TYPE_WTV = "wxtx"
TYPE_DET = "xxt"
TYPE_NP = "xt"

def is_intensional_type(typ):
    return typ.startswith("w")

PLAYERS = [a,b]

BASELEXICON = {
    ("some", TYPE_DET):        (lambda X : (lambda Y : len(set(X) & set(Y)) > 0)),
    ("exactly_one", TYPE_DET): (lambda X : (lambda Y : len(set(X) & set(Y)) == 1)),
    ("every", TYPE_DET):       (lambda X : (lambda Y : set(X) <= set(Y))),
    ("no", TYPE_DET):          (lambda X : (lambda Y : len(set(X) & set(Y)) == 0)),
    ("PlayerA", TYPE_NP):      (lambda Y : a in Y),
    ("PlayerB", TYPE_NP):      (lambda Y : b in Y),
    ("PlayerC", TYPE_NP):      (lambda Y : c in Y),
    ("intensional_player", TYPE_WX): (lambda p,s,c : p),
    ("intensional_shot", TYPE_WX):   (lambda p,s,c : s),
    ("intensional_relational_made", TYPE_WEET): (lambda p,s,c : (lambda x : (lambda y : x in s[: c[p.index(y)]]))),
    ("intensional_made", TYPE_WTV): (lambda p,s,c : (lambda Q : [y for y in p if Q([x for x in s if intensional_relational_made(p, s, c)(x)(y)])])),
    ("intensional_scored", TYPE_WX): (lambda p,s,c : [x for x in p if x in intensional_made(p,s,c)(some(intensional_shot(p,s,c)))]),
    ("intensional_missed", TYPE_WX): (lambda p,s,c : [x for x in p if x not in intensional_made(p,s,c)(every(intensional_shot(p,s,c)))]),
}

######################################################################

class World:
    def __init__(self, p=None, s=None, c=None):
        self.params = (p, s, c)
        self.name = "".join(['NSA'[i] for i in c])
        
    def interpret(self, exp, withlex={}):
        # Import the lexicon into this space:
        for word_with_typ, sem in withlex.items():
            setattr(sys.modules[__name__], word_with_typ[0], sem)                            
        # Extensions for all the intensionalized predicates:
        player = intensional_player(*self.params)
        shot = intensional_shot(*self.params)
        relational_made = intensional_relational_made(*self.params)
        made = intensional_made(*self.params)
        scored = intensional_scored(*self.params)
        missed = intensional_missed(*self.params)       
        # Return the value in this world:
        return eval(exp)

class WorldSet:
    def __init__(self, basic_states=(0,1,2), p=None, s=None, increasing=True):
        self.basic_states = basic_states
        self.p = p
        self.s = s
        self.increasing = increasing
        shotcounts = list(itertools.product(self.basic_states, repeat=len(self.p)))
        if increasing:
            shotcounts = [sc for sc in shotcounts if self._check_increasing(sc)]
        self.worlds = [World(p=self.p, s=self.s, c=c) for c in shotcounts]
        self.names = [w.name for w in self.worlds]

    def interpret(self, exp, vectorize=False, withlex={}):
        p = [(w, w.interpret(exp, withlex=withlex)) for w in self.worlds]
        if vectorize:            
            p = np.array([self.indicator(val) for w, val in p])
        return p

    def _check_increasing(self, w):
        for j in range(len(w)-1):
            for k in range((j+1), len(w)):
                if w[j] > w[k]:
                    return False
        return True
    
    def indicator(self, x):
        return 1.0 if x else 0.0
    
    def __str__(self):
        return " ".join(self.names)

    def __len__(self):
        return len(self.worlds)

######################################################################

if __name__ == '__main__':

    # Entity domains:
    people = [a, b, c]
    shots = [s1, s2]

    # world = World(p=[a,b], s=shots, c=(0,1,2))
    
    worldset = WorldSet(basic_states=(0,1,2), p=people, s=shots, increasing=True)
        
    examples = [        
        "scored",
        "a in scored",
        "PlayerA(made(no(shot)))",
        "PlayerB(made(some(shot)))",
        "PlayerC(made(every(shot)))",
        "PlayerC(scored)",
        "PlayerC(missed)",
        "PlayerB(missed)",
        "some_player(scored)",
        "some(player)(made(every(shot)))",
        "every(player)(made(some(shot)))",
        "some(player)(made(exactly_one(shot)))",
        "no(player)(made(exactly_one(shot)))"]

    for ex in examples:
        print "======================================================================"
        print ex, [(x[0].name, x[1]) for x in worldset.interpret(ex, withlex=BASELEXICON)]
