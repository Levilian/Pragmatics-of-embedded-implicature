#!/usr/bin/env python

import sys
import re
from itertools import product
import numpy as np
from utils import NULL, powerset

######################################################################

a = 'a'; b = 'b'; c = 'c'
s1 = 's1' ; s2 = 's2'

def define_lexicon(player=[], shot=[], worlds=[]):
    D_et = powerset(player+shot)
    relational_made =  [[w, x, y] for w, x, y in product(worlds, player, shot) if y in shot[: w[player.index(x)]]]
    lex = {
        # Concessions to tractability -- these are defined extensionally (invariant across worlds):
        "some":        [[X, Y] for X, Y in product(D_et, repeat=2) if len(set(X) & set(Y)) > 0],
        "exactly_one": [[X, Y] for X, Y in product(D_et, repeat=2) if len(set(X) & set(Y)) == 1],
        "every":       [[X, Y] for X, Y in product(D_et, repeat=2) if set(X) <= set(Y)],
        "no":          [[X, Y] for X, Y in product(D_et, repeat=2) if len(set(X) & set(Y)) == 0],
        "PlayerA":     [X for X in D_et if a in X],
        "PlayerB":     [X for X in D_et if b in X],
        "PlayerC":     [X for X in D_et if c in X],        
        "player":      player,
        "shot":        shot,
        # Intensional predicates:
        "scored":      [[w, x] for w, x in product(worlds, player) if len(shot[: w[player.index(x)]]) > 0],
        "doubled":     [[w, x] for w, x in product(worlds, player) if len(shot[: w[player.index(x)]]) > 1],
        "missed":      [[w, x] for w, x in product(worlds, player) if len(shot[: w[player.index(x)]]) == 0],
        "made" :       [[w, x, y] for w, x, y in product(worlds, player, shot) if y in shot[: w[player.index(x)]]],
        # More concessions to tractability -- we'll refine these rather than the determiners:
        "some_player": [X for X in powerset(player, minsize=1) if len(set(player) & set(Y)) > 0],
        "some_shot":   [X for X in powerset(shot, minsize=1) if len(set(shot) & set(Y)) > 0]        
        }
    return lex

def fa(A, b):
    return [y for x, y in A if x == b]
                    
def iv(Q, X):
    return (lambda w : fa(X, w) in Q)

def tv(V, Q, worlds, subjects):
    return [[w,x] for w, x in product(worlds, subjects) if [y for w_prime, x_prime, y in V if w_prime == w and x_prime == x] in Q]

    
######################################################################

def get_worlds(basic_states=(0,1,2), length=3, increasing=False):
    worlds = list(product(basic_states, repeat=length))        
    if increasing:
        worlds = [w for w in worlds if check_increasing(w)]
    return worlds

def check_increasing(w):
    for j in range(len(w)-1):
        for k in range((j+1), len(w)):
            if w[j] > w[k]:
                return False
    return True

def worldname(w):
    return "".join(["NSA"[i] for i in w])

######################################################################

if __name__ == '__main__':

    # Domain set up:
    player = [a, b, c]
    shot = [s1, s2]
    worlds = get_worlds((0,1,2), length=len(player), increasing=True)    
    lex = define_lexicon(player=player, shot=shot, worlds=worlds)

    # Import the lexicon into this namespace:
    for word, sem in lex.items():
        setattr(sys.modules[__name__], word, sem)

    # Examples:
    for d1, d2 in product(("some", "exactly_one", "every", "no"), repeat=2):
        msg = "%s(player)(made(%s(shot)))" % (d1, d2)
        formula = "iv(fa(%s, player), tv(made, fa(%s, shot), worlds, player))" % (d1,  d2)       
        print msg, [worldname(w) for w in worlds if eval(formula)(w)]

    # Examples:
    for pn, pred in product(('PlayerA', 'PlayerB', 'PlayerC'), ("missed", "scored", "doubled")):
        msg = "%s(%s)" % (pn, pred)
        formula = "iv(%s, %s)" % (pn, pred)
        print msg, [worldname(w) for w in worlds if eval(formula)(w)]
    
    
    
