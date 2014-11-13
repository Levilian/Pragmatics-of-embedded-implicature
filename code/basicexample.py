#!/usr/bin/env python

import itertools
from collections import defaultdict
import numpy as np
import random

from pragmods import Pragmod, display_matrix

a = 'a'; b = 'b'; c = 'c'
entities = [a, b]
shot_entities = ['s1', 's2']
domain = entities + shot_entities

pw = [['s1', 's2'], ['s1'], ['s2'], []]

def get_worlds():
    worlds = []
    for d1, d2 in itertools.product(pw, pw):
        worlds.append({a: d1, b: d2})
    return worlds

worlds = get_worlds()

player = (lambda x : (lambda w : x in entities))
shot = (lambda x : (lambda w : x in shot_entities))
relational_made = (lambda sh : (lambda ent : (lambda w : sh in w[ent])))
made = (lambda Q : (lambda ent : (lambda w : Q(lambda sh : relational_made(sh)(ent))(w))))

def charset(f, dom):
    return [d for d in dom if f(d)]

def some(f):
    def scope(g):
        def intensions(w):
            for x in domain:
                if f(x)(w) and g(x)(w):
                    return True
            return False
        return intensions
    return scope

def no(f):
    return (lambda g : (lambda w : not some(f)(g)(w)))

def every(f):
    def scope(g):
        def intensions(w):
            for x in domain:
                if f(x)(w) and not g(x)(w):
                    return False
            return True
        return intensions
    return scope

def exactly_one(f):
    def scope(g):
        def intensions(w):
            if len([x for x in domain if f(x)(w) and g(x)(w)]) == 1:
                return True
            return False
        return intensions
    return scope

######################################################################

if __name__ == '__main__':
    
    expression_examples = (
        'every(player)(made(some(shot)))',
        'every(player)(made(no(shot)))',
        'exactly_one(player)(made(every(shot)))',
        'some(player)(made(no(shot)))',
        'exactly_one(player)(made(no(shot)))',
        'exactly_one(player)(made(exactly_one(shot)))',
        'every(player)(made(some(shot)))',
        'every(player)(made(exactly_one(shot)))')

    for exp in expression_examples:
        print "======================================================================"
        print exp
        for w in charset(eval(exp), worlds):
            print w
        
