#!/usr/bin/env python

import itertools

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

# Defined for flexibility and to avoid having to type quotation marks:
a = 'a'; b = 'b'; c = 'c'
s1 = 's1' ; s2 = 's2'

# Domain and subdomains:
entities = [a, b, c]
shot_entities = [s1, s2]
domain = entities + shot_entities

# Nouns (denoting lists of entities, type x)
player = entities
shot = shot_entities

# Quantificational determiners: <x, <x,t>>
some =        (lambda X : (lambda Y : len(set(X) & set(Y)) > 0))
exactly_one = (lambda X : (lambda Y : len(set(X) & set(Y)) == 1))
every =       (lambda X : (lambda Y : set(X) <= set(Y)))
no =          (lambda X : (lambda Y : len(set(X) & set(Y)) == 0))

# Quantifier phrases: <x,t>
PlayerA = (lambda X : a in X)
PlayerB = (lambda X : b in X)
PlayerC = (lambda X : c in X)

# Transitive verb in <w, eet> (the idea is that a world is defined by
# sequences like (0,1,2), which mean that player A made 0 shots,
# player A made some but not all, and player C made all):
def intensional_relational_made(entities, shot_entities, shotcounts):
    return (lambda x : (lambda y : x in shot_entities[: shotcounts[entities.index(y)]]))

# Transitive verb <w, <xt,x>>:
def intensional_made(entities, shot_entities, shotcounts):
    def located_made(Q):        
        func = (lambda y : Q([x for x in shot_entities if intensional_relational_made(entities, shot_entities, shotcounts)(x)(y)]))
        return [y for y in entities if func(y)]
    return located_made

# Intransitive verbs denoting in <w,x> (with meanings derived from made):
intensional_scored = (lambda params : [x for x in domain if x in intensional_made(*params)(some(shot))])
intensional_missed = (lambda params : [x for x in domain if x not in intensional_made(*params)(every(shot))])

######################################################################
# This makes setting the "world" more intuitive. The conceit is that
# player, shot, etc., have the same denotations in all worlds. Only
# the denotation of made changes from world to world. Hence a world is
# defined by its sequence of shotcounts, and World.interpret just
# needs to refine relational_made to reflect that. Having this class
# would make it is easy to allow worlds to vary by other properties:
# one would just given World.__init__ more parameters and in turn
# redefine more predicates before using eval in World.interpet.

class World:
    def __init__(self, entities=entities, shot_entities=shot_entities, shotcounts=range(len(entities))):
        self.entities = entities
        self.shot_entities = shot_entities
        self.shotcounts = shotcounts
        self.params = (self.entities, self.shot_entities, shotcounts)

    def interpret(self, exp):
        # Extensions for all the intensionalized predicates:
        relational_made = intensional_relational_made(*self.params)
        made = intensional_made(*self.params)
        scored = intensional_scored(self.params)
        missed = intensional_missed(self.params)
        # Return the value in this world:
        return eval(exp)

######################################################################
# Utilities

def powerset(x, minsize=0, maxsize=None):
    result = []
    if maxsize == None: maxsize = len(x)
    for i in range(minsize, maxsize+1):
        for val in itertools.combinations(x, i):
            result.append(list(val))
    return result

def characteristic_set(func, dom, minsize=0):
    return [X for X in powerset(dom, minsize=minsize) if func(X)]

######################################################################

if __name__ == '__main__':

    world = World(entities=[a,b], shotcounts=(0,2))
    
    examples = [
        "characteristic_set(some(player), entities)",
        "characteristic_set(no(player), entities)",
        "relational_made(s2)(a)",
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
        print ex, world.interpret(ex)
        
