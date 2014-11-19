#!/usr/bin/env python

import sys
import itertools
import numpy as np

######################################################################
# In this grammar, nouns and VPs denote sets of entities, and
# quantificational determiners denote functions from sets to functions
# from sets to truth values. This design makes it easy to take a
# quantifier like some(shot) and get all of its subsets --- we just
# calculate its characteristic set.
#
# Because of Python's limits on hashable entities, "sets" in the above
# are actually lists. This shouldn't cause problems because all
# assertions of membership for these objects involve first converting
# them to sets.

######################################################################
# Model

# Quantificational determiners: <x, <x,t>>
some =        (lambda X : (lambda Y : len(set(X) & set(Y)) > 0))
exactly_one = (lambda X : (lambda Y : len(set(X) & set(Y)) == 1))
every =       (lambda X : (lambda Y : set(X) <= set(Y)))
no =          (lambda X : (lambda Y : len(set(X) & set(Y)) == 0))

# Quantifier phrases: <x,t>
PlayerA = (lambda X : a in X)
PlayerB = (lambda X : b in X)
PlayerC = (lambda X : c in X)

# Nouns (denoting lists of entities, type <w,x>)
intensional_player = (lambda p,s,c : p)
intensional_shot = (lambda p,s,c : s)

# Transitive verb in <w, eet> (the idea is that a world is defined by
# sequences like (0,1,2), which mean that player A made 0 shots,
# player A made some but not all, and player C made all):
def intensional_relational_made(p, s, c):
    return (lambda x : (lambda y : x in s[: c[p.index(y)]]))

# Transitive verb <w, <xt,x>>:
def intensional_made(p, s, c):
    def located_made(Q):        
        func = (lambda y : Q([x for x in s if intensional_relational_made(p, s, c)(x)(y)]))
        return [y for y in p if func(y)]
    return located_made

# Intransitive verbs denoting in <w,x> (with meanings derived from made):
intensional_scored = (lambda p,s,c : [x for x in p if x in intensional_made(p,s,c)(some(intensional_shot(p,s,c)))])
intensional_missed = (lambda p,s,c : [x for x in p if x not in intensional_made(p,s,c)(every(intensional_shot(p,s,c)))])

######################################################################

class World:
    def __init__(self, p=None, s=None, c=None, lexicon=None):
        self.params = (p, s, c)
        self.lexicon = lexicon
        self.name = "".join(['NSA'[i] for i in c])
        
    def interpret(self, exp):                                    
        # Extensions for all the intensionalized predicates:
        player = intensional_player(*self.params)
        shot = intensional_shot(*self.params)
        relational_made = intensional_relational_made(*self.params)
        made = intensional_made(*self.params)
        scored = intensional_scored(*self.params)
        missed = intensional_missed(*self.params)
        # Now import the lexicon into this space:
        if self.lexicon:
            for key, val in self.lexicon.items():
                setattr(sys.modules[__name__], key, val)
        # Return the value in this world:
        return eval(exp)

class WorldSet:
    def __init__(self, basic_states=(0,1,2), p=None, s=None, increasing=True, lexicon=None):
        self.basic_states = basic_states
        self.p = p
        self.s = s
        self.increasing = increasing
        self.lexicon = lexicon
        shotcounts = list(itertools.product(self.basic_states, repeat=len(self.p)))
        if increasing:
            shotcounts = [sc for sc in shotcounts if self._check_increasing(sc)]
        self.worlds = [World(p=self.p, s=self.s, c=c, lexicon=lexicon) for c in shotcounts]
        self.names = [w.name for w in self.worlds]

    def interpret(self, exp, vectorize=False):
        p = [(w, w.interpret(exp)) for w in self.worlds]
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

######################################################################

if __name__ == '__main__':

    a = 'a'; b = 'b'; c = 'c'
    s1 = 's1' ; s2 = 's2'

    # Entity domains:
    people = [a, b, c]
    shots = [s1, s2]

    # world = World(p=[a,b], s=shots, c=(0,1,2))
    
    worldset = WorldSet(basic_states=(0,1,2), p=people, s=shots, increasing=True, lexicon={'some': exactly_one})
        
    examples = [        
        "scored",
        "a in scored",
        "PlayerA(made(no(shot)))",
        "PlayerB(made(some(shot)))",
        "PlayerC(made(every(shot)))",
        "PlayerC(scored)",
        "PlayerC(missed)",
        "PlayerB(missed)",
        "some(player)(made(every(shot)))",
        "every(player)(made(some(shot)))",
        "some(player)(made(exactly_one(shot)))",
        "no(player)(made(exactly_one(shot)))"]

    for ex in examples:
        print "======================================================================"
        print ex, [(x[0].name, x[1]) for x in worldset.interpret(ex)]
        #print ex, worldset.interpret(ex, vectorize=False, withlex={'some': every})
