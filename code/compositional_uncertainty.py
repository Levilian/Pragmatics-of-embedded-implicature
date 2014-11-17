#!/usr/bin/env python

import itertools
from collections import defaultdict
import numpy as np
import random
import cPickle as pickle
from fragment import *
from pragmods import display_matrix, Pragmod
from semgrammar import get_best_inferences
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

NULL = 'NULL'

class UncertaintyLexicon:
    def __init__(self,
                 entities=entities,
                 shot_entities=shot_entities,
                 basic_states=(0,1,2),
                 subj_dets=('every', 'some', 'exactly_one', 'no'),
                 obj_dets=('every', 'some', 'no'),
                 enrichable_dets=('some','PlayerA', 'PlayerB', 'PlayerC'),
                 proper_names=('PlayerA', 'PlayerB', 'PlayerC'),
                 null_msg=True):
        self.entities = entities
        self.shot_entities = shot_entities
        self.domain = self.entities + self.shot_entities
        self.basic_states = basic_states
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
        self.langs = []
        self.null_msg = null_msg

    def double_quantifier_language(self, noisy=False):
        self.get_worlds()
        self.define_baselexicon()
        self.get_lexica()
        langs = self.get_double_quantifier_language()
        self.langs2mats(langs, noisy=noisy)

    def subject_scoring_language(self, noisy=False):
        self.get_worlds(increasing=False)
        self.define_baselexicon()
        self.get_lexica()
        langs = self.get_subject_scoring_language()
        self.langs2mats(langs, noisy=noisy)

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
            for world in self.worlds:
                made = intensional_made(self.entities, self.shot_entities, world)
                for det1, det2 in itertools.product(self.subj_dets+self.proper_names, self.obj_dets):
                    # No complement need be added for proper names:
                    if det1 in self.subj_dets:                        
                        det1 = "%s(player)" % det1                    
                    subj = lex[det1]
                    obj_str = "%s(shot)" % det2
                    obj = lex[obj_str]
                    msg = "%s(made(%s))" % (det1, obj_str)
                    self.messages.append(msg)            
                    val = (lambda Y : Y in subj)(made((lambda X : X in obj)))
                    if val:
                        lang[msg].append(world)            
            langs.append(lang)
        self.messages = sorted(set(self.messages))
        if self.null_msg:
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
                    # No complement need be added for proper names:                  
                    if det in self.subj_dets:
                        det = "%s(player)" % det                     
                    msg = "%s(scored)" % det
                    subj = lex[det]                    
                    self.messages.append(msg)
                    val = (lambda Y : Y in subj)(scored)
                    if val:
                        lang[msg].append(world)
            langs.append(lang)
        self.messages = sorted(set(self.messages))
        if self.null_msg:
            self.messages.append(NULL)                               
        return langs

    def get_worlds(self, increasing=True):
        self.worlds = list(itertools.product(self.basic_states, repeat=len(self.entities)))
        if increasing:
            self.worlds = [w for w in self.worlds if self.check_increasing(w)]

    def check_increasing(self, w):
        for j in range(len(w)-1):
            for k in range((j+1), len(w)):
                if w[j] > w[k]:
                    return False
        return True        
    
    def langs2mats(self, langs, noisy=True):
        world_count = len(self.worlds)
        msg_count = len(self.messages)
        for lang in langs:
            mat = self.initial_matrix(msg_count, world_count, noisy=noisy)
            for i, msg in enumerate(self.messages):
                for j, world in enumerate(self.worlds):
                    if world in lang[msg]:
                        mat[i, j] += 1.0            
            if 0.0 not in np.sum(mat, axis=1):
                self.matrices.append(mat)

    def initial_matrix(self, m, n, noisy=False, lower=0.0, upper=0.1):
        if noisy:
            vals = np.array([random.uniform(lower, upper) for i in range(m*n)])
            return vals.reshape(m, n)
        else:
            return np.zeros((m, n))

    def uncertainty_run(self,
                        display=True,
                        null_cost=5.0,
                        prior=None,
                        lexprior=None,
                        temperature=1.0,
                        n=1):
        if prior == None:
            prior = np.repeat(1.0/len(self.worlds), len(self.worlds))
        if lexprior == None:
            lexprior = np.repeat(1.0/len(self.matrices), len(self.matrices))
        costs = np.zeros(len(self.messages))
        if self.null_msg:
            costs[-1] = null_cost                                                      
        mod = Pragmod(lexica=self.matrices,
                      messages=self.messages,
                      meanings=self.worlds,
                      costs=costs,
                      prior=prior,
                      lexprior=lexprior,
                      temperature=1.0)        
        self.langs = mod.run_uncertainty_model(n=n, display=False)
        # Smith et al. anxiety listener:
        # langs = mod.run_anxiety_model(n=1, display=False)
        # Anxiety/uncertainty:
        # langs = mod.run_expertise_model(n=3, display=False)
        # langs[-1] = np.sum(langs[-1], axis=0)

    def report(self, digits=4):
        print 'Lexical', len(self.matrices)
        print 'Final listener'
        display_matrix(self.langs[-1], rnames=self.messages, cnames=self.get_worldnames(), digits=2)
        print 'Best inferences'
        best_inferences = self.get_best_inferences(digits=4)  
        for msg, val in sorted(best_inferences.items()):
            print msg, val

    def get_best_inferences(self, digits=4):    
        best_inferences = {}
        # Round to avoid tiny distinctions that don't even display:
        final_listener = np.round(self.langs[-1], 10)
        for i, msg in enumerate(self.messages):
            maxval = max(final_listener[i])
            best_states = [(self.get_worldname(w), str(np.round(maxval, digits))) for j, w in enumerate(self.worlds) if final_listener[i,j] == maxval]
            best_inferences[msg] = best_states             
        return best_inferences   

    def get_worldname(self, w):
        alph = 'NSA'
        return "".join([alph[i] for i in w])

    def get_worldnames(self):
        return [self.get_worldname(w) for w in self.worlds]
    
    def final_listener2latex(self, digits=2):        
        mat = self.langs[-1]
        rnames = self.messages
        cnames = self.get_worldnames()
        mat = np.round(mat, digits)
        rows = []
        rows.append([''] + cnames)
        for i in range(mat.shape[0]):
            rowmax = max(mat[i])
            def highlighter(x): return r"\graycell{%s}" % x if x == rowmax else str(x)
            vals = [highlighter(x) for x in mat[i]]            
            rows.append([rnames[i]] + vals)
        s = ""
        s += "\\begin{tabular}[c]{r *{%s}{r} }\n" % len(cnames)
        s += "\\toprule\n"
        s += "%s\\\\\n" % " & ".join(rows[0])
        s += "\\midrule\n"
        for row in rows[1: ]:
            s += "%s\\\\\n" % " & ".join(row)
        s += "\\bottomrule\n"
        s += "\\end{tabular}"
        return s
   
    def final_listener2plot(self, output_filename=None, nrows=None, ncols=None, include_null=True, indices=None, likertize=False):
        mat = self.langs[-1]        
        rnames = self.messages
        cnames = self.get_worldnames()
        if not nrows:       
            nrows = len(self.subj_dets + self.proper_names)
            ncols = len(self.obj_dets)
        plt.style.use('ggplot')
        fig, axarray = plt.subplots(nrows=nrows, ncols=ncols)
        fig.set_figheight(3*nrows)
        fig.set_figwidth(7*ncols)
        fig.subplots_adjust(bottom=-0.5)
        if indices == None:
            indices = list(itertools.product(range(nrows), range(ncols)))        
        if not include_null:
            mat = mat[:-1]
        for i, row in enumerate(mat):
            axind = indices[i]
            rowinitial = False
            if axind[1] == 0:
                rowinitial = True        
            self.dist2plot(axarray[axind], row, title=rnames[i], cnames=cnames, rowinitial=rowinitial, likertize=likertize)
        if output_filename:
            plt.savefig(output_filename, bbox_inches='tight')
        else:
            plt.show()
            
    def dist2plot(self, ax, row, title="", cnames=None, rowinitial=True, likertize=False):
        ylim = [0,1]
        ylabel = r"$L(w \mid m)$"
        if likertize:
            row = 1.0 + (6.0 * row)
            ylim = [0,7]
            ylabel = "Likert(%s)" % ylabel                     
        width = 1.0
        pos = np.arange(0, len(row), width)
        ax.bar(pos, row, width)
        ax.set_xlim([0.0, len(row)])
        ax.set_xticks(pos+(width/2.0))
        ax.set_xticklabels(cnames, fontsize=14,  rotation='vertical', color='black')
        ax.set_ylim(ylim)                
        if not rowinitial:
            ylabel = ""
            ax.set_yticklabels("")   
        ax.set_ylabel(ylabel, fontsize=14)         
        ax.set_title(title)  

    def final_listener2plot_compare(self, comparison_filename=None, output_filename=None, nrows=None, ncols=None, include_null=True, indices=None, likertize=False):
        results = pickle.load(file(comparison_filename))
        mat = self.langs[-1]        
        rnames = self.messages
        cnames = self.get_worldnames()
        if not nrows:       
            nrows = len(self.subj_dets + self.proper_names)
            ncols = len(self.obj_dets)
        plt.style.use('ggplot')
        fig, axarray = plt.subplots(nrows=nrows, ncols=ncols)
        fig.set_figheight(3*nrows)
        fig.set_figwidth(7*ncols)
        fig.subplots_adjust(bottom=-0.5)
        if indices == None:
            indices = list(itertools.product(range(nrows), range(ncols)))        
        if not include_null:
            mat = mat[:-1]
        for i, row in enumerate(mat):
            axind = indices[i]
            rowinitial = False
            if axind[1] == 0:
                rowinitial = True
            empirical_row = [results[rnames[i]][wname] for wname in cnames]
            self.dist2plot_compare(axarray[axind], row, empirical_row, title=rnames[i], cnames=cnames, rowinitial=rowinitial, likertize=likertize)
        if output_filename:
            plt.savefig(output_filename, bbox_inches='tight')
        else:
            plt.show()

    def dist2plot_compare(self, ax, row, empirical_row, title="", cnames=None, rowinitial=True, likertize=False):
        empirical_means, empirical_cis = zip(*empirical_row)                    
        if not likertize:
            empirical_means = empirical_means/np.sum(empirical_means)
        coef, p = pearsonr(np.array(empirical_means), row)
        pstr = r"$p = %s$" % np.round(p, 3) if p >= 0.001 else "p < 0.001"
        ylim = [0,1]
        ylabel = r"$L(w \mid m)$"
        if likertize:
            row = 1.0 + (6.0 * row)
            ylim = [0,7]
            ylabel = "Likert(%s)" % ylabel                     
        width = 0.5
        gap = 0.2
        barsetwidth = (width*2)+gap
        pos = np.arange(0, len(row)+barsetwidth, barsetwidth)
        ax.bar(pos, row, width, label="Model")
        ax.bar(pos+width, empirical_means, width, color="#A60628", label="Experiment")
        for i, ci in enumerate(empirical_cis):
            xpos = pos[i]+(width*1.5)
            ax.plot([xpos,xpos], ci, linewidth=2, color='black')            
        ax.text(pos[0], ylim[1], r"Pearson $\rho$: %s; %s" % (np.round(coef, 2), pstr), color="black", verticalalignment='top', fontsize=14)
        ax.set_xlim([0.0, len(row)+((len(row)-1)*gap)])
        ax.set_xticks(pos+(barsetwidth/2.0))
        ax.set_xticklabels(cnames, fontsize=14,  rotation='vertical', color='black')
        ax.set_ylim(ylim)
        ax.legend()
        if not rowinitial:
            ylabel = ""
            ax.set_yticklabels("")   
        ax.set_ylabel(ylabel, fontsize=14)         
        ax.set_title(title)              
            
######################################################################

if __name__ == '__main__':

    ##################################################
    # Illustrative example

    def simple_example():
        experiment = UncertaintyLexicon(entities=[a,b],
                                        basic_states=(0,1),
                                        shot_entities=shot_entities,
                                        subj_dets=('every', 'some', 'no'),
                                        obj_dets=(),
                                        enrichable_dets=('some', 'PlayerA', 'PlayerB'),
                                        proper_names=('PlayerA', 'PlayerB'))
        experiment.subject_scoring_language()
        experiment.uncertainty_run(temperature=1.0, n=1)
        experiment.report()
        print experiment.final_listener2latex(digits=2)
        experiment.final_listener2plot(output_filename="../fig/example-simple.pdf", nrows=2, ncols=3, include_null=True)
        
    
    ##################################################
    # Modeling the pilot data

    def pilot():
        pilot = UncertaintyLexicon(entities=[a,b,c],
                                   shot_entities=shot_entities,
                                   subj_dets=('every', 'exactly_one', 'no'),
                                   obj_dets=('every', 'some', 'no'),
                                   enrichable_dets=('some',),
                                   proper_names=())
        pilot.double_quantifier_language()

        mcfrank_ordering = [(2, 2), (2, 0), (2, 1),
                            (1, 2), (1, 0), (1, 1),
                            (0, 2), (0, 0), (0, 1)]
                            #(3, 2), (3, 0), (3, 1)] # if some is included put it first in subj_dets and use this line
                        
        pilot.uncertainty_run(temperature=1.0, n=1)
        pilot.report()
        print pilot.final_listener2latex(digits=2)
        #pilot.final_listener2plot(output_filename="../fig/example-pilot-likertize.pdf", include_null=False, indices=mcfrank_ordering, likertize=True)
        #pilot.final_listener2plot(output_filename="../fig/example-pilot-L10.pdf", include_null=False, indices=mcfrank_ordering)        
        pilot.final_listener2plot_compare(output_filename="../fig/example-pilot-experimentcmp-likertize.pdf",
                                          comparison_filename="../data/basketball-pilot-2-11-14-results-parsed.pickle",
                                          indices=mcfrank_ordering,
                                          include_null=False,
                                          likertize=True)       

    ##################################################
    # Put it all together:

    def full():
        experiment = UncertaintyLexicon(entities=[a,b,c],
                                        basic_states=(0,1,2),
                                        shot_entities=shot_entities,
                                        subj_dets=('every', 'some', 'no', 'exactly_one'),
                                        obj_dets=('every', 'some', 'no', 'exactly_one'),
                                        enrichable_dets=('some', 'PlayerA', 'PlayerB'), # Left out C because of memory issues.
                                        proper_names=('PlayerA', 'PlayerB', 'PlayerC'))
        experiment.double_quantifier_language()
        experiment.uncertainty_run(temperature=1.0, n=1)
        experiment.report()
        print experiment.final_listener2latex(digits=2)
        experiment.final_listener2plot(output_filename="../fig/example-full.pdf", include_null=False)
        

    #simple_example()
    pilot()
    #full()
