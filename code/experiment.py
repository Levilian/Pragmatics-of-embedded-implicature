#!/usr/bin/env python

import csv
from collections import defaultdict
from itertools import product
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from utils import *
import bootstrap

######################################################################
# Clas for modeling experimental items (rows in the table):

class Item:
    def __init__(self, data):
        # Attributes for data/basketball-pilot-2-11-14-results-parsed.csv:
        #
        # workerid,
        # Answer.language,
        # player1color,
        # player2color,
        # player3color,
        # sentence,
        # condition,
        # conditionOrder,
        # trialnum,
        # response,
        # rt,
        # trainingCorrect
        self.data = data
        for key, val in self.data.items():
            key = key.replace(".", "_")
            if key in ('trialnum', 'response', 'rt'):
                val = int(val)
            elif key == 'trainingCorrect' and val == 'NA':
                val = None
            setattr(self, key, val)
        # For correspondence with the modeling:
        self.condition_norm = CONDITION_MAP.get(self.condition, None)
        self.formula = SENTENCES.get(self.sentence, None)

    def __str__(self):
        return str(self.d)

######################################################################
# Class for the entire experiment, built from the spreadsheet:
    
class Experiment:
    def __init__(self, src_filename="../data/basketball-pilot-2-11-14-results-parsed.csv"):        
        self.src_filename = src_filename
        self.data = [Item(d) for d in csv.DictReader(file(src_filename))]
        self.targets = defaultdict(lambda : defaultdict(list))
        self.get_target_responses()

    def get_target_responses(self):
        for item in self.data:
           if item.formula:
               self.targets[item.formula][item.condition_norm].append(item.response) 

    def target_means(self):
        return self.target_analysis(func=np.mean)

    def target_means2matrix(self, rnames, cnames):
        return self.target_values2matrix(rnames, cnames, self.target_means())

    def target_cis2matrix(self, rnames, cnames):
        return self.target_values2matrix(rnames, cnames, self.target_cis())
        
    def target_cis(self):        
        return self.target_analysis(func=self.get_ci)

    def get_ci(self, vals):
        if len(set(vals)) == 1:
            return (vals[0], vals[0])
        # In case bootstrap.py is missing or not working:
        # loc = np.mean(vals)
        # scale = np.std(vals) / np.sqrt(len(vals))
        # return stats.t.interval(0.95, len(vals)-1, loc=loc, scale=scale)        
        return bootstrap.ci(vals, method='bca')
    
    def target_analysis(self, func=np.mean):
        mu = defaultdict(lambda : defaultdict(list))
        for form, cond_dict in self.targets.items():
            for cond, vals in cond_dict.items():
                mu[form][cond] = func(vals)
        return mu
        
    def target_values2matrix(self, rnames, cnames, value_dict):        
        mat = []
        for i, rname in enumerate(rnames):
            row = []
            for j, cname in enumerate(cnames):
                row.append(value_dict[rname][cname])
            mat.append(row)
        return mat    

    def plot_targets(self, output_filename=None):
        rnames = sorted(self.targets.keys())
        mat = self.target_means2matrix(rnames, CONDITIONS)
        confidence_intervals = self.target_cis2matrix(rnames, CONDITIONS)                        
        # Orientation:
        barwidth = 1.0
        pos = np.arange(0.0, len(CONDITIONS)*barwidth, barwidth)
        xlim = [0,8]
        xticks = range(1,8)
        xlabel = "Human responses"
        ylim = [0.0, len(CONDITIONS)*barwidth]
        yticks = pos+(barwidth/2.0)
        yticklabels = [r'\texttt{%s}' % s for s in CONDITIONS[::-1]] # Reversal for preferred condition order.
        titles = [TITLES[s] for s in rnames]
        titles = [r"\emph{%s}" % s for s in titles]
        # Sizing:        
        nrows = 3
        ncols = 3
        axis_height = 4
        axis_width = 4        
        # Basic figure dimensions and design:
        fig, axarray = plt.subplots(nrows=nrows, ncols=ncols)
        fig.set_figheight(axis_height*nrows)
        fig.set_figwidth(axis_width*ncols)
        fig.subplots_adjust(wspace=0.3)
        fig.text(0.5, 0.05, 'Mean human response', ha='center', va='center', fontsize=xtick_labelsize+2)
        fig.text(0.05, 0.5, 'World', ha='center', va='center', rotation='vertical', fontsize=ytick_labelsize+2)
        # Axes:
        indices = list(product(range(nrows), range(ncols)))    
        for i, row in enumerate(mat):
            row = row[::-1] # Reversal for preferred condition order.
            axindex = indices[i]
            ax = axarray[axindex]
            ax.tick_params(axis='both', which='both', bottom='off', left='off', top='off', right='off', labelbottom='on')
            ax.barh(pos, row, barwidth, color=colors[0])
            ax.set_title(titles[i], fontsize=title_size)
            # x-axis
            ax.set_xlim(xlim)
            ax.set_xticks(xticks)
            # x-axis labels only for bottom row to avoid clutter:
            if axindex[0] == 2:
                ax.set_xticklabels(xticks, fontsize=xtick_labelsize, color='black')
            else:
                ax.set_xticklabels([])
            # y-axis:
            ax.set_ylim(ylim)
            ax.set_yticks(yticks)            
            ax.set_yticklabels(yticklabels, fontsize=ytick_labelsize, rotation='horizontal', color='black')
            # Confidence intervals:
            cis = confidence_intervals[i]
            cis = cis[::-1]  # Reversal for preferred condition order.
            for j, xpos in enumerate(pos):
                xpos = xpos+(barwidth/2.0)
                ax.plot(cis[j], [xpos, xpos], linewidth=2, color='#555555') 
        # Output:
        if output_filename:
            plt.savefig(output_filename, bbox_inches='tight')
        else:
            plt.show()

######################################################################
    
if __name__ == '__main__':

    exp1 = Experiment(src_filename='../data/basketball-pilot-2-11-14-results-parsed.csv')
    exp1.plot_targets(output_filename="../fig/basketball-pilot-2-11-14-results-parsed.pdf")


