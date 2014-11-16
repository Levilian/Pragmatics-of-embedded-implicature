#!/usr/bin/env python

import itertools
from collections import defaultdict
import numpy as np
import random

from pragmods import Pragmod, display_matrix

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

# GQ proper names, type <et,t>
a_gq = (lambda f : f(a))
b_gq = (lambda f : f(b))
c_gq = (lambda f : f(c))

# Quantificational determiners as type <et,<et,t>>
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

def generate_states(full_state_cross_product=False):
    if full_state_cross_product:
        return list(itertools.product(range(2), range(2)))
    n = len(entities)
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

def double_quantifier_message_iterator(subj_dets, obj_dets):
    for (det1, det2) in itertools.product(subj_dets, obj_dets):
        msg = '%s(player)(made(%s(shot)))' % (det1, det2)
        yield msg

def mixed_message_iterator(subj_dets, obj_dets):
    for (det1, det2) in itertools.product(subj_dets, obj_dets):
        if '_gq' in det1:
            msg = '%s(made(%s(shot)))' % (det1, det2)
        else:
            msg = '%s(player)(made(%s(shot)))' % (det1, det2)
        yield msg

def define_baselexicon(states,
                       subj_dets=('every', 'some', 'no', 'exactly_one'),
                       obj_dets=('every', 'some', 'no', 'exactly_one'),
                       message_iterator=double_quantifier_message_iterator):
    # In the above context, this (0,1,2) means a made no shots, b made
    # some but not all shots, and c made all shots:
    baselexicon = defaultdict(list)
    messages = []    
    for msg in message_iterator(subj_dets, obj_dets):
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
    if not 0.0 in np.sum(mat, axis=1):
        return mat
    else:
        return None

def basic_model_run(display=False):
   
    states = generate_states()
        
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
    
    # The model:
    mod = Pragmod(lexica=None,
                  messages=msgs,
                  meanings=states,
                  costs=costs,
                  prior=np.repeat(1.0/len(states), len(states)),
                  lexprior=None,
                  temperature=1.0)

    langs = mod.run_base_model(matlex, n=2, display=False)
    best_inferences = get_best_inferences(langs[-1], msgs, states)
    if display:
        display_matrix(final, rnames=msgs, cnames=states)
        for key, val in sorted(best_inferences.items()):
            print key, val    
    return langs[-1], best_inferences

def get_best_inferences(final_listener, msgs, states):    
    best_inferences = {}
    final_listener = np.round(final_listener, 10)
    for i, msg in enumerate(msgs):
        maxval = max(final_listener[i])
        best_states = [(state, str(np.round(maxval, 4))) for j, state in enumerate(states) if final_listener[i,j] == maxval]
        best_inferences[msg] = best_states             
    return best_inferences        

######################################################################
# Streaming lexical uncertainty

def stream_lex_mats(baselexicon, messages, states, sampsize=0):
    m = len(messages)
    n = len(states) 
    enrichments = [powerset(baselexicon[msg]) for msg in messages]
    iterator = None
    if sampsize:
        iterator = sampling_iterator(enrichments, sampsize)
    else:
        iterator = itertools.product(*enrichments)    
    for x in iterator:
        lex = dict(zip(messages, x))
        mat = np.zeros((len(messages)+1, len(states)))
        for i, msg in enumerate(messages):
            for j, state in enumerate(states):
                if state in lex[msg]:
                    mat[i, j] = 1.0
        mat[-1] = np.ones(len(states))
        if not 0.0 in np.sum(mat, axis=1):
            yield mat

def sampling_iterator(enrichments, sampsize):
    max_iter = np.product([len(x) for x in enrichments if len(x) > 1])
    print 'Upper-bound lexica size:', max_iter
    maxinds = [len(x)-1 for x in enrichments]
    vecs = set([])
    iterations = 0  
    while len(vecs) < sampsize and iterations <= max_iter:
        v = tuple([random.randint(0,ind) for ind in maxinds])
        iterations += 1
        if v not in vecs:
            vecs.add(v)
            yield [enrichments[j][v[j]] for j in range(len(v))]
        
def powerset(x, minsize=1, maxsize=None):
    result = []
    if maxsize == None: maxsize = len(x)
    for i in range(minsize, maxsize+1):
        for val in itertools.combinations(x, i):
            result.append(list(val))
    return result            

def uncertainty_run_stream(sampsize=0, # If positive, then sampsize lexica will be used.
                           n=0,  # Depth of iteration beyond L1.                         
                           subj_dets=('every', 'some', 'no', 'exactly_one'),
                           obj_dets=('every', 'some', 'no'),
                           display=True,
                           message_iterator=double_quantifier_message_iterator,
                           full_state_cross_product=False):
    states = generate_states(full_state_cross_product=full_state_cross_product)
    baselexicon = define_baselexicon(states, subj_dets=subj_dets, obj_dets=obj_dets, message_iterator=message_iterator)
    states = sorted(set([s for vals in baselexicon.values() for s in vals]))
    msgs = sorted(baselexicon.keys())    
    costs = np.zeros(len(msgs)+1)
    costs[-1] = 5.0
    mod = Pragmod(lexica=None,
                  messages=msgs,
                  meanings=states,
                  costs=costs,
                  prior=np.repeat(1.0/len(states), len(states)),
                  lexprior=None)
    final = np.zeros((len(msgs)+1, len(states)))
    for mat_index, mat in enumerate(stream_lex_mats(baselexicon, msgs, states, sampsize=sampsize)):
        if mat_index and mat_index % 1000000 == 0: print mat_index
        final += mod.prior * mod.s1(mat).T
    final = np.divide(final.T, np.sum(final, axis=1)).T
    for i in range(n):
        final = mod.L(mod.S(final))
    best_inferences = get_best_inferences(final, msgs + ['NULL'], states)    
    if display:
        print 'Lexica', mat_index+1
        display_matrix(final, rnames=msgs + ['NULL'], cnames=states)
        for key, val in sorted(best_inferences.items()):
            print key, val    
    return final,  best_inferences

######################################################################
# Lexical uncertainty
#
### THis in-memory version isn't really viable for this setting.
#
#
# def uncertainty_run(display=True):
#     # Concessions to tractibility:
#     subj_dets = ('every', 'some') #, 'exactly_one')
#     obj_dets = ('every', 'some', 'no') #, 'exactly_one')
#     states = generate_states()
#        
#     baselexicon = define_baselexicon(states, subj_dets=subj_dets, obj_dets=obj_dets)
#    
#     lexica = Lexica(baselexicon=baselexicon,
#                     nullsem=True,
#                     null_cost=5.0,
#                     block_ineffability=False,
#                     block_trivial_messages=True)
#    
#     print "Lexica", len(lexica)
#                                          
#     mod = Pragmod(lexica=lexica.lexica2matrices(),             
#                 messages=lexica.messages,
#                 meanings=lexica.states,
#                 costs=lexica.cost_vector(),
#                 prior=np.repeat(1.0/len(lexica.states), len(lexica.states)),
#                 lexprior=np.repeat(1.0/len(lexica), len(lexica)),
#                 temperature=1.0)
#
#     langs = mod.run_uncertainty_model(n=1, display=False)
#     best_inferences = get_best_inferences(langs[-1], lexica.messages, lexica.states)
#     if display:
#         display_matrix(langs[-1], rnames=lexica.messages, cnames=lexica.states)
#         for key, val in sorted(best_inferences.items()):
#             print key, val 
#     return langs[-1], best_inferences         

######################################################################

if __name__ == '__main__':

    # (0,1) is an aritrarily chosen state: player A made no shots, player B merely some
    made = (lambda Q : generic_quantified_made(Q, (0,1)))
    
    expressions_examples = (
        'made(every(shot))(b)',
        'every(player)(made(some(shots)))',
        'exactly_one(player)(made(every(shot)))',
        'some(player)(made(no(shots)))')
    
    for exp in expressions_examples:
        print exp, eval(exp)

    print "======================================================================"


    # final_listener, best_inferences = basic_model_run()        
    # final_listener, best_inferences = uncertainty_run()   
   
    #final_listener, best_inferences = uncertainty_run_stream(sampsize=1000, # If positive, then sampsize lexica will be used.
    #                                                         n=0,           # Depth of iteration beyond L1.
    #                                                         subj_dets=('every', 'some', 'no', 'exactly_one'),
    #                                                         obj_dets=('every', 'some', 'no'))

    print "======================================================================"

    final_listener, best_inferences = uncertainty_run_stream(sampsize=10**5, # If positive, then sampsize lexica will be used.
                                                             n=10,           # Depth of iteration beyond L1.
                                                             subj_dets=('every', 'some', 'no', 'a_gq', 'b_gq'),
                                                             obj_dets=('some',),
                                                             message_iterator=mixed_message_iterator,
                                                             full_state_cross_product=True)
    
