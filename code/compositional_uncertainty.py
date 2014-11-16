#!/usr/bin/env python

import itertools
from collections import defaultdict
import numpy as np
from fragment import *
from pragmods import display_matrix, Pragmod
from semgrammar import get_best_inferences

NULL = 'NULL'

class UncertaintyLexicon:
    def __init__(self,
                 entities=entities,
                 shot_entities=shot_entities,
                 subj_dets=('every', 'some', 'exactly_one', 'no'),
                 obj_dets=('every', 'some', 'no'),
                 enrichable_dets=('some','PlayerA', 'PlayerB', 'PlayerC'),
                 proper_names=('PlayerA', 'PlayerB', 'PlayerC')):

        self.entities = entities
        self.shot_entities = shot_entities
        self.domain = self.entities + self.shot_entities
        self.subj_dets = subj_dets
        self.obj_dets = obj_dets
        self.dets = self.subj_dets + self.obj_dets
        self.enrichable_dets = enrichable_dets
        self.proper_names = proper_names       
        self.nouns_with_domains = (('player', entities), ('shot', self.shot_entities))
        self.baselexicon = {}
        self.lexica = []
        self.worlds = []
        self.messages = []
        self.matrices = []

    def double_quantifier_language(self):
        self.get_worlds()
        self.define_baselexicon()
        self.get_lexica()
        langs = self.get_double_quantifier_language()
        self.langs2mats(langs)

    def subject_scoring_language(self):
        self.get_worlds(increasing=False)
        self.define_baselexicon()
        self.get_lexica()
        langs = self.get_subject_scoring_language()
        self.langs2mats(langs)
                                     
    def define_baselexicon(self):
        player = self.entities
        shot = self.shot_entities    
        for det in self.dets:            
            for noun, dom in self.nouns_with_domains:
                np = "%s(%s)" % (det, noun)
                val = characteristic_set(eval(np), dom)
                if det in self.enrichable_dets:
                    val = powerset(val, minsize=1)
                else:
                    val = [val]
                self.baselexicon[np] = val
        for pn in self.proper_names:
            val = characteristic_set(eval(pn), self.entities)
            if pn in self.enrichable_dets:
                val = powerset(val, minsize=1)
            else:
                val = [val]
            self.baselexicon[pn] = val

    def get_lexica(self):
        words, enrichments = zip(*self.baselexicon.items())
        for x in itertools.product(*enrichments):
            self.lexica.append(dict(zip(words, x)))

    def get_double_quantifier_language(self):
        langs = []
        for lex in self.lexica:
            lang = defaultdict(list)
            lang[NULL] = self.worlds
            for det1, det2 in itertools.product(self.subj_dets, self.obj_dets):
                subj_str = "%s(player)" % det1
                subj = lex[subj_str]
                obj_str = "%s(shot)" % det2
                obj = lex[obj_str]
                msg = "%s(made(%s))" % (subj_str, obj_str)
                self.messages.append(msg)
                for world in self.worlds:
                    made = intensional_made(self.entities, self.shot_entities, world)
                    val = (lambda Y : Y in subj)(made((lambda X : X in obj)))
                    if val:
                        lang[msg].append(world)                
            langs.append(lang)
        self.messages = sorted(set(self.messages))
        self.messages.append(NULL)                               
        return langs

    def get_subject_scoring_language(self):
        langs = []
        for lex in self.lexica:
            lang = defaultdict(list)
            lang[NULL] = self.worlds
            for world in self.worlds:
                scored = [x for x in domain if x in intensional_made(self.entities, self.shot_entities, world)(some(self.shot_entities))]                
                for det in self.subj_dets + self.proper_names:
                    subj_str = None
                    if det in self.subj_dets:
                        subj_str = "%s(player)" % det                     
                    else:
                        subj_str = det
                    msg = "%s(scored)" % subj_str
                    subj = lex[subj_str]                    
                    self.messages.append(msg)
                    val = (lambda Y : Y in subj)(scored)
                    if val:
                        lang[msg].append(world)
            langs.append(lang)
        self.messages = sorted(set(self.messages))
        self.messages.append(NULL)                               
        return langs

    def get_worlds(self, increasing=True):
        self.worlds = list(itertools.product((0,1,2), repeat=len(self.entities)))
        if increasing:
            self.worlds = [w for w in self.worlds if self.check_increasing(w)]

    def check_increasing(self, w):
        for j in range(len(w)-1):
            for k in range((j+1), len(w)):
                if w[j] > w[k]:
                    return False
        return True        
    
    def langs2mats(self, langs):
        world_count = len(self.worlds)
        msg_count = len(self.messages)
        for lang in langs:
            mat = np.zeros((msg_count, world_count))
            for i, msg in enumerate(self.messages):
                for j, world in enumerate(self.worlds):
                    if world in lang[msg]:
                        mat[i, j] += 1.0            
            if 0.0 not in np.sum(mat, axis=1):
                self.matrices.append(mat)

    def uncertainty_run(self,
                        display=True,
                        null_cost=5.0,
                        prior=None,
                        lexprior=None,
                        temperature=1.0):
        if prior == None:
            prior = np.repeat(1.0/len(self.worlds), len(self.worlds))
        if lexprior == None:
            lexprior = np.repeat(1.0/len(self.matrices), len(self.matrices))
        costs = np.zeros(len(self.messages))
        costs[-1] = null_cost                                                      
        mod = Pragmod(lexica=self.matrices,
                      messages=self.messages,
                      meanings=self.worlds,
                      costs=costs,
                      prior=prior,
                      lexprior=lexprior,
                      temperature=0.5)

        langs = mod.run_uncertainty_model(n=1, display=False)
        best_inferences = get_best_inferences(langs[-1], self.messages, self.worlds)
        if display:
            alph = 'NSA'
            display_matrix(langs[-1], rnames=self.messages, cnames=["".join([alph[i] for i in w]) for w in self.worlds])
            for key, val in sorted(best_inferences.items()):
                print key, val 
        return langs[-1], best_inferences


######################################################################

if __name__ == '__main__':

    ##################################################
    # Illustrative example
    
    experiment = UncertaintyLexicon(entities=[a,b],
                                    shot_entities=shot_entities,
                                    subj_dets=('every', 'some', 'exactly_one', 'no'),
                                    obj_dets=(),
                                    enrichable_dets=('some', 'PlayerA', 'PlayerB'),
                                    proper_names=('PlayerA', 'PlayerB'))
    experiment.subject_scoring_language()
    experiment.uncertainty_run()

    ##################################################
    # Modeling the pilot data

    experiment = UncertaintyLexicon(entities=[a,b,c],
                                    shot_entities=shot_entities,
                                    subj_dets=('every', 'some', 'exactly_one', 'no'),
                                    obj_dets=('every', 'some', 'no'),
                                    enrichable_dets=('some',),
                                    proper_names=())
    experiment.double_quantifier_language()
    experiment.uncertainty_run()

    
        
