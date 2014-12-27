#!/usr/bin/env python

import sys
from copy import copy
from collections import defaultdict
from itertools import product
import numpy as np
from scipy.stats import spearmanr, pearsonr
from plots import *
from utils import *
from experiment import TITLES
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

    def comparison_plot(self, stats=False, width=0.2, output_filename=None):        
        fig, axarray = plt.subplots(nrows=len(self.listeners)+1, ncols=len(self.messages))
        for i, lis in enumerate(self.listeners):
            self.model_comparison_plot(axarray[i], lis, stats=stats, width=width, color=colors[i+1], top=i==0, bottom=False, modname=self.modnames[i])
        self.model_comparison_plot(axarray[-1], self.expmat, stats=stats, width=width, color=colors[0], top=False, bottom=True, modname='Human')
        fig.text(0.06, 0.5, 'Probability', ha='center', va='center', rotation='vertical', fontsize=20)
        if output_filename:
            plt.savefig(output_filename, bbox_inches='tight')
        else:
            plt.show()

    def model_comparison_plot(self, axarray, modmat, stats=False, width=1.0, color='black', top=False, bottom=False, modname=None):
        pos = np.arange(0.0, len(self.worlds)*width, width)
        xlim = [0.0, len(self.worlds)*width]
        xtick_labels = "" * len(self.worlds)                
        if bottom:
            xtick_labels = self.worlds
        yticks = [0.0, 0.25, 0.5, 0.75, 1.0]            
        ytick_labels = ["0", "", ".5", "", "1"]
        for j, ax in enumerate(axarray):
            msg = self.messages[j]
            row = modmat[j]
            ax.bar(pos, row, width, color=color)
            ax.set_xlim(xlim)
            ax.set_ylim((0.0, 1.0))
            ax.set_xticks(pos+(width/2.0))
            ax.set_xticklabels(xtick_labels, fontsize=14, rotation='vertical', color='black')            
            if top:
                ax.set_title(TITLES[self.messages[j]])
            ax.set_yticks(yticks)     
            if j == 0:                                           
                ax.set_yticklabels(ytick_labels)
            else:
                ax.set_yticklabels([])
            if j == len(self.messages)-1:
                ax.yaxis.tick_right()
                ax.set_yticks([0.5])
                ax.set_yticklabels([modname], rotation='vertical')

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
