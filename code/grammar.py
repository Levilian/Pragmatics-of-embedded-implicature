#!/usr/bin/env python

import itertools
from collections import defaultdict
import numpy as np
from fragment import *

NULL = 'NULL'

def powerset(x, minsize=0, maxsize=None):
    result = []
    if maxsize == None: maxsize = len(x)
    for i in range(minsize, maxsize+1):
        for val in itertools.combinations(x, i):
            result.append(list(val))
    return result

class UncertaintyGrammars:
    def __init__(self,
                 baselexicon=('player', 'shot', 'some', 'exactly_one', 'every', 'no', 'PlayerA', 'PlayerB', 'PlayerC', 'made', 'scored', 'missed'),
                 messages=[],
                 worlds=None,                                
                 refinable=('some', 'PlayerA', 'PlayerB', 'PlayerC'),
                 nullmsg=True,
                 nullcost=5.0):
        self.baselexicon = baselexicon
        self.messages = messages
        self.worlds = worlds
        self.refinable = refinable
        self.nonrefinable = [x for x in self.baselexicon if x not in self.refinable]
        self.nullmsg = nullmsg
        self.nullcost = nullcost

    def lexicon_iterator(self):
        enrichments = None
        m = len(self.messages)
        if self.nullmsg:
            m += 1
        n = len(self.worlds)        
        for meaning_vector in itertools.product(*enrichments):
            lex = dict(zip(self.baselexicon, meaning_vector))
            # +1 on the rows of the NULL message
            mat = np.zeros((m, n))   
            for i, msg in enumerate(self.messages):
                mat[i] = self.worlds.interpret(msg, vectorize=True, withlex=lex)
            # Final row for universally true NULL message:
            mat[-1] = np.ones(n)
            yield mat  
                                        
    def characteristic_set(self, func, dom, minsize=0):
        return [X for X in powerset(dom, minsize=minsize) if func(X)]

    def refinements(self, semval, dom):
        if isinstance(semval, list):
            return powerset(func, minsize=1)
        else:
            refined = []
            for X in powerset(self.characteristic_set(semval, dom, minsize=0), minsize=1):
                refined.append((lambda x, X=X : x in X))
        return refined
       
######################################################################

if __name__ == '__main__':

    pass

