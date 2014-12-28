#!/usr/bin/env python

import sys
from copy import copy
from collections import defaultdict
from itertools import product
import numpy as np
from scipy.stats import spearmanr, pearsonr
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
        self.modnames = ['Literal', 'Fixed lexicon'] + [mod.name for mod in self.models]
        if NULL in self.messages:
            self.messages.remove(NULL)
            for i, lis in enumerate(self.listeners):
                self.listeners[i] = lis[: -1]
        self.expmat = np.array(self.experiment.target_means2matrix(self.messages, self.worlds))
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

    def comparison_plot(self, width=0.2, output_filename=None):
        nrows = len(self.listeners)+1
        ncols = len(self.messages)
        fig, axarray = plt.subplots(nrows=nrows, ncols=ncols)
        fig.subplots_adjust(bottom=-1.0)
        fig.set_figheight(nrows)
        fig.set_figwidth(ncols*2.5)        
        for i, lis in enumerate(self.listeners):
            self.model_comparison_plot(axarray[i], lis, width=width, color=colors[i+1], top=i==0, bottom=False, modname=self.modnames[i])
        self.model_comparison_plot(axarray[-1], self.expmat, width=width, color=colors[0], top=False, bottom=True, modname='Human')
        if output_filename:
            plt.savefig(output_filename, bbox_inches='tight')
        else:
            plt.show()

    def model_comparison_plot(self, axarray, modmat, width=1.0, color='black', top=False, bottom=False, modname=None):
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
                ax.yaxis.set_label_position("right")
                ax.set_ylabel(modname, fontsize=16)                
            ax.tick_params(axis='both', which='both', bottom='off', left='off', top='off', right='off')
            
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
