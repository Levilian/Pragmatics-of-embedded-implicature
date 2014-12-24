import csv
from collections import defaultdict
import numpy as np
from scipy import stats
from plots import message_state_barplot, comparison_plot, add_confidence_intervals
import matplotlib.pyplot as plt

SENTENCES = {
    "Every player hit all of his shots": "every(player)(hit(every(shot)))",
    "Every player hit none of his shots": "every(player)(hit(no(shot)))",    
    "Every player hit some of his shots": "every(player)(hit(some(shot)))",    
    "Exactly one player hit all of his shots": "exactly_one(player)(hit(every(shot)))",
    "Exactly one player hit none of his shots": "exactly_one(player)(hit(no(shot)))",
    "Exactly one player hit some of his shots": "exactly_one(player)(hit(some(shot)))",
    "No player hit all of his shots": "no(player)(hit(every(shot)))",
    "No player hit none of his shots": "no(player)(hit(no(shot)))",
    "No player hit some of his shots": "no(player)(hit(some(shot)))",
    "Every player hit only some of his shots": "every(player)(hit(exactly_one(shot)))",
    "Exactly one player hit only some of his shots": "exactly_one(player)(hit(exactly_one(shot)))",
    "No player hit only some of his shots": "no(player)(hit(exactly_one(shot)))"
}

TITLES = {
    "every(player)(hit(every(shot)))": 'every...every',
    "every(player)(hit(no(shot)))": 'every...no',
    "every(player)(hit(some(shot)))": 'every...some',
    "exactly_one(player)(hit(every(shot)))": 'exactly one...every',
    "exactly_one(player)(hit(no(shot)))": 'exactly one ..no',
    "exactly_one(player)(hit(some(shot)))": 'exactly one...some',
    "no(player)(hit(every(shot)))": 'no...every',
    "no(player)(hit(no(shot)))": 'no...no',
    "no(player)(hit(some(shot)))": 'no...some'}
    

CONDITION_MAP = {
    "none-none-none": "NNN",
    "none-none-half": "NNS",
    "none-none-all": "NNA",
    "none-half-half": "NSS",
    "none-half-all": "NSA",                         
    "none-all-all": "NAA",
    "half-half-half": "SSS",
    "half-half-all": "SSA",
    "half-all-all": "SAA",
    "all-all-all": "AAA" }

CONDITIONS = ("NNN", "NNS", "NNA", "NAA", "NSS", "NSA", "SSS", "SSA", "SAA", "AAA")

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

class Experiment:
    def __init__(self,
                 src_filename="../data/basketball-pilot-2-11-14-results-parsed.csv",
                 subjectCondition=None):
        
        self.src_filename = src_filename
        self.subjectCondition = subjectCondition
        self.data = [Item(d) for d in csv.DictReader(file(src_filename))]
        if self.subjectCondition:
            self.data = [x for x in self.data if x.subjectCondition == self.subjectCondition]
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
        loc = np.mean(vals)
        scale = np.std(vals) / np.sqrt(len(vals))
        return stats.t.interval(0.95, len(vals)-1, loc=loc, scale=scale)
    
    def target_analysis(self, func=np.mean):
        mu = defaultdict(lambda : defaultdict(list))
        for form, cond_dict in self.targets.items():
            for cond, vals in cond_dict.items():
                mu[form][cond] = func(vals)
        return mu

    def plot_targets(self, output_filename=None):
        rnames = sorted(self.targets.keys())
        cnames = CONDITIONS
        message_state_barplot(mat=self.target_means2matrix(rnames, cnames),
                              confidence_intervals=self.target_cis2matrix(rnames, cnames),
                              rnames=[TITLES[s] for s in rnames],
                              cnames=cnames,
                              nrows=3,
                              ncols=3,
                              output_filename=output_filename,
                              indices=[],                              
                              ylim=[0,8],
                              yticks=range(0,8),
                              ylabel="Subject responses")
        
    def target_values2matrix(self, rnames, cnames, value_dict):        
        mat = []
        for i, rname in enumerate(rnames):
            row = []
            for j, cname in enumerate(cnames):
                row.append(value_dict[rname][cname])
            mat.append(row)
        return mat

    def count_unique(self, attr=None):
        x = set([])
        for item in self.data:
            x.add(getattr(item, attr))
        return len(x)

    def report(self):
        print 'Participants:', self.count_unique('workerid')
        print 'Sentences:', self.count_unique('sentence')
        print 'Conditions:', self.count_unique('condition')


    def analyze_clustered_item(self, sentence, world_clusters):
        d = defaultdict(list)
        for item in self.data:
            if item.sentence == sentence:
                d[world_clusters[item.condition_norm]].append(item.response)                
        vals = []
        cis = []
        cnames = sorted(set(world_clusters.values()))
        for cname in cnames:
            vals.append(np.mean(d[cname]))
            cis.append(self.get_ci(np.array(d[cname])))
        return (vals, cis)        

    def plot_clustered_item(self, sentence, world_clusters, output_filename=None):
        vals, cis = self.analyze_clustered_item(sentence, world_clusters)
        cnames = sorted(set(world_clusters.values()))
        message_state_barplot(mat=[vals],
                              confidence_intervals=[cis],
                              rnames=[sentence],
                              cnames=cnames,
                              nrows=1,
                              ncols=1,
                              output_filename=output_filename,
                              ylim=[0,8],
                              yticks=range(0,8),
                              ylabel="Subject responses")

######################################################################
    
if __name__ == '__main__':


    exp1 = Experiment(src_filename='../data/basketball-pilot-2-11-14-results-parsed.csv')
    exp1.plot_targets(output_filename="../fig/basketball-pilot-2-11-14-results-parsed.pdf")
    exp1.report()

    #exp2a = Experiment(src_filename='../data/basketball-focus-only-manip-3-17-14-results-parsed.csv',  subjectCondition="focus")    
    #exp2b = Experiment(src_filename='../data/basketball-focus-only-manip-3-17-14-results-parsed.csv',  subjectCondition="only")

    
