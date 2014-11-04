#!/usr/bin/env python

import itertools
from collections import defaultdict
import numpy as np

import sys
sys.path.append('/Volumes/CHRIS/Documents/research/hurford/definitional-disjunction/pragmatic_disjunction/pypragmods/')
from pragmods import Pragmod, display_matrix
from lexica import Lexica

######################################################################
# Grammmar and model

# Domain (type e)
a = 'a'
b = 'b'
c = 'c'
entities = [a,b] #,c] # Leave c out for tractable lexical incertainty.
shots_entities = ['shot%s' % j for j in range(2)]
domain = entities + shots_entities

# <e,t>    
player = (lambda x : x in entities)
shots = (lambda x : x in shots_entities)
shot = shots

# Generic <e,et> made function. This version lets you specify how many
# shots each player made, the distinguishing feature of our contexts.
def relational_made(x, shotcounts):
    acount, bcount = shotcounts[0:2]
    ccount = shotcounts[2] if len(shotcounts) > 2 else None
    def pred(y):
        count = acount        
        if y == b:
            count = bcount
        elif y == c:
            count = ccount
        return x in shots_entities[: count]
    return pred

# Generic made of type <<et,t>,et> built from relational_made. Allows
# for intuitive logical forms like made(some(shots)).
def generic_quantified_made(Q, shotcounts):
    return (lambda y : Q(lambda x : relational_made(x, shotcounts)(y)))
            
# Quantifiers as type <et,<et,t>>
def some(f):
    def scope(g):
        for d in domain:
            if f(d) and g(d):
                return True
        return False
    return scope

def no(f):
    return (lambda g : not some(f)(g))
    
def every(f):
    def scope(g):
        for d in domain:
            if f(d) and not g(d):
                return False
        return True
    return scope

def exactly_one(f):
    def scope(g):
        f_set = set([d for d in domain if f(d)])
        g_set = set([d for d in domain if g(d)])
        return len(f_set & g_set) == 1
    return scope

######################################################################
# Base lexicon with associated states:

def generate_states(n=2):    
    states = []
    if n == 2:
        for i in range(3):
            for j in range(i, 3):
                states.append((i, j))
    # This is intracable with lexical uncertainty:
    if n == 3:
        for i in range(3):
            for j in range(i, 3):
                for k in range(j, 3):
                    states.append((i, j, k))
    return states

def define_baselexicon(states,
                       subj_dets=('every', 'some', 'no', 'exactly_one'),
                       obj_dets=('every', 'some', 'no', 'exactly_one')):
    # In the above context, this (0,1,2) means a made no shots, b made
    # some but not all shots, and c made all shots:
    baselexicon = defaultdict(list)
    messages = []    
    for (det1, det2) in itertools.product(subj_dets, obj_dets):
        msg = '%s(player)(made(%s(shot)))' % (det1, det2)
        for state in states:            
            made = (lambda Q : generic_quantified_made(Q, state))                               
            semval = eval(msg)
            if semval:
                baselexicon[msg].append("".join(map(str, state)))
    return baselexicon

######################################################################
# Modeling without lexical uncertainty

def lex2mat(lex, msgs, states):
    mat = np.zeros((len(msgs), len(states)))
    for i, msg in enumerate(msgs):
        for j, state in enumerate(states):
            if state in lex[msg]:
                mat[i, j] = 1.0  
    return mat

def basic_model_run():
   
    states = generate_states(n=2)
        
    baselexicon = define_baselexicon(states)
    # Add the NULL messsage, true in all states:
    baselexicon['NULL'] = ["".join(map(str, state)) for state in states]

    # Canonical ordering of states:
    states = sorted(set([s for vals in baselexicon.values() for s in vals]))
    
    # Define messages with NULL is on the end for the sake of the cost vector:
    msgs = sorted(baselexicon.keys())
    msgs.remove('NULL')
    msgs.append('NULL')

    # Costs:    
    costs = np.zeros(len(msgs))
    costs[-1] = 5.0 # NULL cost.

    # Lexicon as a matrix:
    matlex = lex2mat(baselexicon, msgs, states)

    # Have a look at the lexicon:
    # display_matrix(matlex, rnames=msgs, cnames=states)

    # The model:
    mod = Pragmod(lexica=None,
                  messages=msgs,
                  meanings=states,
                  costs=costs,
                  prior=np.repeat(1.0/len(states), len(states)),
                  lexprior=None,
                  temperature=1.0)

    langs = mod.run_base_model(matlex, n=2, display=False)
    return get_best_inferences(langs, msgs, states)


def get_best_inferences(langs, msgs, states):
    final_listener = langs[-1]
    best_inferences = {}
    for i, msg in enumerate(msgs):
        maxval = max(final_listener[i])
        best_states = [state for j, state in enumerate(states) if final_listener[i,j] == maxval]
        best_inferences[msg] = best_states
    return best_inferences
        

######################################################################
# Lexical uncertainty

def uncertainty_run():
    # Concessions to tractibility:
    subj_dets = ('every', 'some', 'no', 'exactly_one')
    obj_dets = ('every', 'some', 'exactly_one')
    states = generate_states(n=2)
        
    baselexicon = define_baselexicon(states, subj_dets=subj_dets, obj_dets=obj_dets)
    
    lexica = Lexica(baselexicon=baselexicon,
                    nullsem=True,
                    null_cost=5.0,
                    block_ineffability=False,
                    block_trivial_messages=True)
    
    print "Lexica", len(lexica)
                                          
    mod = Pragmod(lexica=lexica.lexica2matrices(),             
                messages=lexica.messages,
                meanings=lexica.states,
                costs=lexica.cost_vector(),
                prior=np.repeat(1.0/len(lexica.states), len(lexica.states)),
                lexprior=np.repeat(1.0/len(lexica), len(lexica)),
                temperature=1.0)

    langs = mod.run_uncertainty_model(n=10, display=False)
    return get_best_inferences(langs, lexica.messages, lexica.states)              

######################################################################

if __name__ == '__main__':

    made = (lambda Q : generic_quantified_made(Q, (0,1)))

    expressions_examples = (
        'made(every(shot))(b)',
        'every(player)(made(some(shots)))',
        'exactly_one(player)(made(every(shot)))',
        'some(player)(made(no(shots)))')

    for exp in expressions_examples:
        print exp, eval(exp)


    best_inferences = basic_model_run()
    for key, val in sorted(best_inferences.items()):
        print key, val

    
    best_inferences = uncertainty_run()
    for key, val in sorted(best_inferences.items()):
        print key, val
