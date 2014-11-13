#!/usr/bin/env python

import itertools
from collections import defaultdict
import numpy as np
import random

def powerset(x, minsize=0, maxsize=None):
    result = []
    if maxsize == None: maxsize = len(x)
    for i in range(minsize, maxsize+1):
        for val in itertools.combinations(x, i):
            result.append(list(val))
    return result            


a = 'a'; b = 'b'; c = 'c'
entities = [a, b]
shot_entities = ['s1', 's2']
domain = entities + shot_entities

pw = powerset(domain)

some = [[x, y] for x, y in itertools.product(pw, pw) if len(set(x) & set(y)) > 0]

print len(some)
