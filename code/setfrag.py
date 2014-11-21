#!/usr/bin/env python

import sys
from itertools import product
import numpy as np
from utils import NULL, powerset

######################################################################

a = 'a'; b = 'b'; c = 'c'
s1 = 's1' ; s2 = 's2'

def generic_quantifier(dom=[], worlds=[], relfunc=None):    
    pass

def fa_det(det, restriction):    
    pass

def iv(a, b):
    return b in a
    
def fa_tv(tv, Q):
    pass

def fa_intensional(X, w):
    return [x[1:] for x in X if w == x[0]]
    
def fa_propositional(X, y):
    return [x[0] for x in X if y == x[1]]
    
def define_lexicon(players=[a,b], shots=[s1, s2], worlds=[(0,0), (0,1), (1,0), (1,1)]):
    domain = players + shots
    player_property_domain = [[w,X] for w, X in product(worlds, powerset(players))]
    lex = {
        "some":        None,
        "exactly_one": None,
        "every":       None,
        "no":          None,
        "PlayerA":     [[w, X] for w, X in product(worlds, powerset(domain)) if a in X],
        "PlayerB":     [[w, X] for w, X in product(worlds, powerset(domain)) if b in X],
        "PlayerC":     [[w, X] for w, X in product(worlds, powerset(domain)) if c in X],
        "player":      [[w, x] for w, x in product(worlds, players)],
        "shot":        [[w, x] for w, x in product(worlds, shots)],
        "scored":      [[w, x] for w, x in product(worlds, players) if len(shots[: w[players.index(x)]]) > 0],
        "missed":      [[w, x] for w, x in product(worlds, players) if len(shots[: w[players.index(x)]]) == 0],
        "made":        [[w, x, y] for w, x, y in product(worlds, players, shots) if y in shots[: w[players.index(x)]]] }        
    return lex

######################################################################

if __name__ == '__main__':

    lex = define_lexicon()

    for word, sem in lex.items():
        setattr(sys.modules[__name__], word, sem)

    print fa(PlayerA
    print fa_intensional(made, (1,1))
    print fa_intensional(scored, (1,1))
    print fa_propositional(scored, b)
    #print scored
