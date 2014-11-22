#!/usr/bin/env python

from copy import copy
import numpy as np
from scipy.stats import spearmanr
from experiment import *
from plots import *
from utils import *

######################################################################

class Analysis:
    def __init__(self,
                 experiment=None,
                 model=None,
                 speakernorm_experiment=False,
                 listenernorm_experiment=False,
                 likertize_model=False):
        self.experiment = experiment
        self.model = model
        self.messages = copy(self.model.messages)
        self.worlds = self.model.states
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
        coef, p = self.correlation_test(self.expmat.flatten(), self.modmat.flatten())
        correlation_text = r"Spearman $\rho = %s$; %s" % (np.round(coef, 2), self.printable_pval(p))
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
        correlation_texts = [(np.round(x[0], 2), self.printable_pval(x[1])) for x in correlation_stats]
        correlation_texts = [r"Spearman $\rho = %s$; %s" % x for x in correlation_texts]
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
        coef, p = spearmanr(x, y)
        return (coef, p)

######################################################################    
    
if __name__ == '__main__':

    # For an example, see the experiment method in examples.py.
    pass

