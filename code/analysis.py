#!/usr/bin/env python

import sys
from copy import copy
from collections import defaultdict
from itertools import product
import numpy as np
from scipy.stats import spearmanr, pearsonr
from plots import *
from utils import *
import csv

######################################################################

class Analysis:
    def __init__(self, experiment=None, models=None):
        self.experiment = experiment
        self.models = models
        self.messages = copy(self.models[0].messages)
        self.worlds = self.models[0].states
        self.literal_listener, rsa_spk, self.rsa_listener = self.models[0].rsa()
        self.uncertainty_listeners = [mod.final_listener for mod in self.models]
        self.listeners = [self.literal_listener, self.rsa_listener] + self.uncertainty_listeners
        self.modnames = ['Literal semantics', 'Fixed lexicon pragmatics'] + [mod.name for mod in self.models]
        if NULL in self.messages:
            self.messages.remove(NULL)
            for i, lis in enumerate(self.listeners):
                self.listeners[i] = lis[: -1]
        self.expmat = np.array(self.experiment.target_means2matrix(self.messages, self.worlds))
        self.confidence_intervals = self.experiment.target_cis2matrix(self.messages, self.worlds)
        self.rescale_experiment()        

    def rescale_experiment(self):
        self.expmat = rownorm(self.expmat-1.0)
        
    def overall_analysis(self, digits=4):
        expvec = self.expmat.flatten()
        rows = []
        for i, lis in enumerate(self.listeners):
            lisvec = lis.flatten()
            pearson, pearson_p = pearsonr(expvec, lisvec)
            spearman, spearman_p = spearmanr(expvec, lisvec)
            err = mse(expvec, lisvec)            
            rows.append(np.array([pearson, pearson_p, spearman, spearman_p, err]))        
        display_matrix(np.array(rows), rnames=self.modnames, cnames=['Pearson', 'Pearson p', 'Spearman', 'Spearman p', 'MSE'], digits=digits)
	
    def analysis_by_message(self, digits=4):
        rows = []
        msglen = max([len(x) for x in self.messages])
        modlen = max([len(x) for x in self.modnames])
        rnames = [msg.rjust(msglen)+" "+ mod.rjust(modlen) for msg, mod in product(self.messages, self.modnames)]
        for i, msg in enumerate(self.messages):        
            expvec = self.expmat[i]
            for j, lis in enumerate(self.listeners):
                lisvec = lis[i]
                pearson, pearson_p = pearsonr(expvec, lisvec)
                spearman, spearman_p = spearmanr(expvec, lisvec)
                err = mse(expvec, lisvec)            
                rows.append(np.array([pearson, pearson_p, spearman, spearman_p, err]))        
        display_matrix(np.array(rows), rnames=rnames, cnames=['Pearson', 'Pearson p', 'Spearman', 'Spearman p', 'MSE'], digits=digits)
                	
	def comparison_plot(self):
		pass
		

    def listener_comparison_plot(self, output_filename=None, indices=[], nrows=1, ncols=None):
        # Correlations:
        correlation_stats = [(self.correlation_test(self.modmat[i], self.expmat[i])) for i in range(self.modmat.shape[0])]
        correlation_texts = self.correlation(by_message=True)
        correlation_texts = [r"%s $\rho = %s$; %s" % (self.correlation_func_name, round(coef, 2), self.printable_pval(p)) for coef, p in correlation_texts]
        self.correlation_func = spearmanr
        self.correlation_func_name = 'Spearman'
        correlation_texts2 = self.correlation(by_message=True)
        correlation_texts2 = [r"%s $\rho = %s$; %s" % (self.correlation_func_name, round(coef, 2), self.printable_pval(p)) for coef, p in correlation_texts2]
        correlation_texts = [x + "\n" + y for x, y in zip(correlation_texts, correlation_texts2)]
        # MSE:
        errs = [self.mse(self.modmat[i], self.expmat[i]) for i in range(self.modmat.shape[0])]
        errs = ["MSE = %s" % np.round(err, 4) for err in errs]
        correlation_texts = [x + "\n" + y for x, y in zip(errs, correlation_texts)]
        # Limits:                
        comparison_plot(modmat=self.modmat,
                        expmat=self.expmat,
                        confidence_intervals=self.confidence_intervals,
                        correlation_texts=correlation_texts,
                        rnames=self.messages,
                        cnames=self.worlds,
                        nrows=nrows,
                        ncols=ncols,
                        output_filename=output_filename,
                        indices=indices,
                        ylim=self.ylim,
                        yticks=self.yticks,
                        ylabel="")

    def printable_pval(self, p):
        return r"$p = %s$" % np.round(p, 3) if p >= 0.001 else r"$p < 0.001$"
            
    def to_csv(self, output_filename):
        writer = csv.writer(file(output_filename, 'w'))
        writer.writerow(['Sentence','Condition','HumanMean','HumanLowerCI','HumanUpperCI', 'LiteralListener','RSAListener','UncertaintyListener'])
        for i, msg in enumerate(self.messages):
            for j, world in enumerate(self.worlds):
                row = [msg, world, lit[i,j], lis[i,j], self.modmat[i,j], self.expmat[i,j], self.confidence_intervals[i][j][0], self.confidence_intervals[i][j][1]]
                writer.writerow(row)

######################################################################    
    
if __name__ == '__main__':

    pass
