#!/usr/bin/env python

import itertools
from copy import copy
import numpy as np
from fragment import *
from utils import display_matrix, NULL, powerset

######################################################################

class UncertaintyGrammars:
    def __init__(self,
                 baselexicon=BASELEXICON,
                 messages=[],
                 worlds=[],
                 refinable={},
                 nullmsg=True):
        
        self.baselexicon = baselexicon
        self.messages = messages
        self.worlds = worlds
        self.refinable = refinable
        self.nullmsg = NULL
        if self.nullmsg:
            self.messages.append(NULL)

    def lexicon_iterator(self):
        words_with_types, refinements = zip(*self.get_all_refinements().items())
        print [len(x) for x in refinements]
        m = len(self.messages)
        n = len(self.worlds)        
        for meaning_vector in itertools.product(*refinements):
            lex = dict(zip(words_with_types, meaning_vector))
            mat = np.zeros((m, n))   
            for i, msg in enumerate(self.messages):
                mat[i] = self.worlds.interpret(msg, vectorize=True, withlex=lex)
            # Final row for universally true NULL message:
            if self.nullmsg:
                mat[-1] = np.ones(n)
            if 0.0 not in np.sum(mat, axis=1):
                yield mat 
 
    def get_all_refinements(self):
        ref = {}
        for word_and_typ, den in self.baselexicon.items():
            word, typ = word_and_typ
            val = []
            if word in self.refinable:
                if is_intensional_type(typ):
                    val = [den]
                else:
                    val = self.refinements(den, self.refinable[word])
            else:
                val = [den]
            ref[(word, typ)] = val
        return ref
                                            
    def characteristic_set(self, func, dom, minsize=0):
        return [X for X in powerset(dom, minsize=minsize) if func(X)]

    def refinements(self, semval, dom=None):
        if isinstance(semval, list):
            return powerset(func, minsize=1)
        else:
            refined = []
            for X in powerset(self.characteristic_set(semval, dom, minsize=0), minsize=1):
                refined.append((lambda x, X=X : x in X))
        return refined
       
######################################################################

if __name__ == '__main__':

    players = [a,b]
    shots = [s1,s2]
    basic_states = (0,1)
        
    lex = copy(BASELEXICON)
    lex[("some_player", TYPE_NP)] =  (lambda Y : len(set(players) & set(Y)) > 0)
    lex[("every_player", TYPE_NP)] = (lambda Y : set(players) <= set(Y))
    lex[("no_player", TYPE_NP)] =    (lambda Y : len(set(players) & set(Y)) == 0)        

    ug = UncertaintyGrammars(
        baselexicon=lex,
        messages=["PlayerA(scored)", "PlayerB(scored)", "every_player(scored)", "no_player(scored)", "some_player(scored)"],
        worlds=WorldSet(basic_states=basic_states, p=players, s=shots, increasing=False),
        refinable={'some_player': [a,b], 'intensional_scored': [a,b]},
        nullmsg=True)

    for lex in ug.lexicon_iterator():
        display_matrix(lex, rnames=ug.messages, cnames=ug.worlds.names)
