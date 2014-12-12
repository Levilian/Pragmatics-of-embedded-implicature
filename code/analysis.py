#!/usr/bin/env python

import sys
from copy import copy
from collections import defaultdict
import numpy as np
from scipy.stats import spearmanr, pearsonr
from experiment import *
from plots import *
from utils import *
import csv
from correlation_analysis import r_doi_ci

######################################################################

class Analysis:
    def __init__(self,
                 experiment=None,
                 model=None,
                 speakernorm_experiment=False,
                 listenernorm_experiment=False,
                 likertize_model=False,
                 correlation_func=pearsonr):
        self.experiment = experiment
        self.model = model
        self.messages = copy(self.model.messages)
        self.worlds = self.model.states
        self.correlation_func = correlation_func
        self.correlation_func_name = "Pearson"
        if "spearman" in self.correlation_func.__name__:
            self.correlation_func_name = 'Spearman'       
        self.modmat = self.model.final_listener
        if NULL in self.messages:
            self.messages.remove(NULL)
            self.modmat = self.modmat[: -1]
        self.expmat = np.array(self.experiment.target_means2matrix(self.messages, self.worlds))
        self.confidence_intervals = self.experiment.target_cis2matrix(self.messages, self.worlds)
        # Rescaling:
        self.likertize_model = likertize_model
        self.speakernorm_experiment = speakernorm_experiment
        self.listenernorm_experiment = listenernorm_experiment
        if self.speakernorm_experiment:
            self.likertize_model = False
            self.rescale_confidence_intervals(byrow=False)
            self.expmat = colnorm(self.expmat)            
        if self.listenernorm_experiment:
            self.likertize_model = False
            self.rescale_confidence_intervals(byrow=True)
            self.expmat = rownorm(self.expmat)            
        if self.likertize_model:
            self.modmat = self.likertize(self.modmat)
        # Y-axis design:
        self.ylim = LIKERT_LIMS
        self.yticks = LIKERT_AXIS_TICKS
        if self.speakernorm_experiment or self.listenernorm_experiment:
            self.ylim = PROB_LIMS
            self.yticks = PROB_AXIS_TICKS
            
    def listener_correlation_plot(self, output_filename=None):                
        # Correlation analysis:
        coef, p, n = self.correlation(by_message=False)
        correlation_text = r"%s $\rho = %s$; %s" % (self.correlation_func_name, np.round(coef, 2), self.printable_pval(p))
        # Plot:
        correlation_plot(xmat=self.modmat,
                         ymat=self.expmat,
                         xlabel="Model predictions",
                         ylabel="Subject responses",
                         correlation_text=correlation_text,
                         output_filename=output_filename)

    def listener_comparison_plot(self, output_filename=None, indices=[], nrows=1, ncols=None):
        # Correlations:
        correlation_stats = [(self.correlation_test(self.modmat[i], self.expmat[i])) for i in range(self.modmat.shape[0])]
        correlation_texts = self.correlation(by_message=True)
        correlation_texts = [r"%s $\rho = %s$; %s" % (self.correlation_func_name, coef, p) for coef, p in correlation_texts]
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

    def rescale_confidence_intervals(self, byrow=True):
        m, n = self.expmat.shape
        if byrow:
            norms = np.sum(self.expmat, axis=1)           
            for i in range(m):
                for j in range(n):
                    upper, lower = self.confidence_intervals[i][j]
                    self.confidence_intervals[i][j] = (upper/norms[i], lower/norms[i])
        else:
            norms = np.sum(self.expmat, axis=0)
            for i in range(m):
                for j in range(n):
                    upper, lower = self.confidence_intervals[i][j]
                    self.confidence_intervals[i][j] = (upper/norms[j], lower/norms[j])
                    

    def likertize(self, mat):
        return np.array([1.0 + (6.0 * row) for row in mat])

    def printable_pval(self, p):
        return r"$p = %s$" % np.round(p, 3) if p >= 0.001 else r"$p < 0.001$"

    def correlation_test(self, x, y):
        n = len(x)       
        coef, p = self.correlation_func(x, y)
        return (coef, p, n)

    def correlation(self, by_message=False):
        if by_message:
            return [(self.correlation_test(self.modmat[i], self.expmat[i]))[:2] for i in range(self.modmat.shape[0])]
        else:
            return self.correlation_test(self.expmat.flatten(), self.modmat.flatten())

    def correlation_by_message(self, a, b):
        return [(self.correlation_test(a[i], b[i])) for i in range(a.shape[0])]

    def correlation_comparison(self, x, y, z, conf_level=0.95):
        xy_coef, _, n = self.correlation_test(x, y)
        xz_coef, _, n = self.correlation_test(x, z)
        yz_coef, _, n = self.correlation_test(y, z)
        lower = None; upper = None; sig = None
        try:
            lower, upper = r_doi_ci(xy_coef, xz_coef, yz_coef, n, conf_level=conf_level)
            sig = not (lower < 0.0 and upper > 0.0)
        except ZeroDivisionError:
            sys.stderr.write("Warning: correlation analysis failed.\n")          
        return (sig, lower, upper, xy_coef, xz_coef, yz_coef, n)

    def correlation_comparison_by_message(self, a, b, c, conf_level=0.95):
        return zip(self.model.messages, [self.correlation_comparison(a[i], b[i], c[i], conf_level=conf_level) for i in range(a.shape[0])])

    def correlation_analysis(self, conf_level=0.95):
        lit, spk, lis = self.model.rsa()
        lit = lit[:-1]
        lis = lis[:-1]
        human = copy(self.expmat)
        lexunc = copy(self.modmat)        
        print 'Human: Lit vs. LexUnc:', self.correlation_comparison(human.flatten(), lit.flatten(), lexunc.flatten(), conf_level=conf_level)
        print 'Human: RSA vs. LexUnc:', self.correlation_comparison(human.flatten(), lis.flatten(), lexunc.flatten(), conf_level=conf_level)        
        print 'By message',        
        print '\nHuman: Lit vs. LexUnc:'        
        for m, vals in self.correlation_comparison_by_message(human, lit, lexunc, conf_level=conf_level):
            print m, vals            
        print '\nHuman: RSA vs. LexUnc:'
        for m, vals in self.correlation_comparison_by_message(human, lis, lexunc, conf_level=conf_level):
            print m, vals

    def message_specific_clustered_correlation_analysis(self, msg, clustering, conf_level=0.95):
        exp_means, exp_cis = self.experiment.analyze_clustered_item(msg, clustering)
        mod_msg = SENTENCES[msg]
        lit, spk, lis = self.model.rsa()
        lit = self.clustered_vector(lit[self.messages.index(mod_msg)], clustering)
        lis = self.clustered_vector(lis[self.messages.index(mod_msg)], clustering)
        lexunc = self.clustered_vector(self.modmat[self.messages.index(mod_msg)], clustering)
        print msg
        print 'Human: Lit vs. LexUnc:', self.correlation_comparison(exp_means, lit, lexunc, conf_level=conf_level)
        print 'Human: RSA vs. LexUnc:', self.correlation_comparison(exp_means, lis, lexunc, conf_level=conf_level)    

    def clustered_vector(self, vec, clustering):
        d = defaultdict(list)
        for j, w in enumerate(self.worlds):
            d[clustering[w]].append(vec[j])
        cnames = sorted(set(clustering.values()))
        vals = np.array([np.mean(d[cname]) for cname in cnames])
        vals = 1.0 + (6.0 * vals)
        return vals
            
    def to_csv(self, output_filename):
        writer = csv.writer(file(output_filename, 'w'))
        writer.writerow(['Sentence','Condition','LiteralListener','RSAListener','UncertaintyListener','HumanMean','HumanLowerCI','HumanUpperCI'])
        lit, spk, lis = self.model.rsa()
        lit = lit[:-1]
        lis = lis[:-1]
        for i, msg in enumerate(self.messages):
            for j, world in enumerate(self.worlds):
                row = [msg, world, lit[i,j], lis[i,j], self.modmat[i,j], self.expmat[i,j], self.confidence_intervals[i][j][0], self.confidence_intervals[i][j][1]]
                writer.writerow(row)

######################################################################    
    
if __name__ == '__main__':

    # For an example, see the experiment method in examples.py.
    pass

