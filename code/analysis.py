import numpy as np
from scipy.stats import spearmanr
from compositional_uncertainty import *
from experiment import *
from plots import *
from pragmod import rownorm, colnorm

class Analysis:
    def __init__(self,
                 experiment=None,
                 model=None,
                 speakernorm_experiment=False,
                 listenernorm_experiment=False,
                 likertize_model=False):
        self.experiment = experiment
        self.model = model
        self.messages = self.model.messages
        self.worlds = self.model.get_worldnames()
        self.modmat = self.model.langs[-1]
        if NULL in self.messages:
            self.messages.remove(NULL)
            self.modmat = self.modmat[: -1]
        self.expmat = np.array(self.experiment.target_means2matrix(self.messages, self.worlds))
        # Rescaling:
        self.likertize_model = likertize_model
        self.speakernorm_experiment = speakernorm_experiment
        self.listenernorm_experiment = listenernorm_experiment
        if self.speakernorm_experiment:
            self.likertize_model = False
            self.expmat = colnorm(self.expmat)
        if self.listenernorm_experiment:
            self.likertize_model = False
            self.expmat = rownorm(self.expmat)
        if self.likertize_model:
            self.modmat = self.likertize(self.modmat)             
            
    def listener_correlation_plot(self, output_filename=None):                
        # Correlation analysis:
        coef, p = self.correlation_test(self.expmat.flatten(), self.modmat.flatten())
        correlation_text = r"$\rho = %s$; %s" % (np.round(coef, 2), self.printable_pval(p))
        # Plot:
        correlation_plot(xmat=self.modmat,
                         ymat=self.expmat,
                         xticks=xticks,
                         yticks=yticks,
                         xlabel="Model predictions",
                         ylabel="Subject responses",
                         correlation_text=correlation_text,
                         output_filename=output_filename)

    def listener_comparison_plot(self, output_filename=None, indices=[]):
        # Correlations:
        correlation_stats = [(self.correlation_test(self.modmat[i], self.expmat[i])) for i in range(self.modmat.shape[0])]
        correlation_texts = [(np.round(x[0], 2), self.printable_pval(x[1])) for x in correlation_stats]
        correlation_texts = [r"$\rho = %s$; %s" % x for x in correlation_texts]
        # Limits:
        ylim = LIKERT_LIMS
        yticks = LIKERT_AXIS_TICKS
        confidence_intervals = self.experiment.target_cis2matrix(self.messages, self.worlds)
        if self.speakernorm_experiment or self.listenernorm_experiment:
            ylim = PROB_LIMS
            yaxis = PROB_AXIS_TICKS
            confidence_intervals = None
        comparison_plot(modmat=self.modmat,
                        expmat=self.expmat,
                        confidence_intervals=confidence_intervals,
                        correlation_texts=correlation_texts,
                        rnames=self.messages,
                        cnames=self.worlds,
                        nrows=len(self.model.subj_dets + self.model.proper_names),
                        ncols=len(self.model.obj_dets),
                        output_filename=output_filename,
                        indices=indices,
                        ylim=ylim,
                        yticks=yticks,
                        ylabel="")

    def likertize(self, mat):
        return np.array([1.0 + (6.0 * row) for row in mat])

    def printable_pval(self, p):
        return r"$p = %s$" % np.round(p, 3) if p >= 0.001 else "p < 0.001"

    def correlation_test(self, x, y):
        coef, p = spearmanr(x, y)
        return (coef, p)

######################################################################    
    
if __name__ == '__main__':

    mcfrank_ordering = [(2, 2), (2, 0), (2, 1),
                        (1, 2), (1, 0), (1, 1),
                        (0, 2), (0, 0), (0, 1)]
                        #(3, 2), (3, 0), (3, 1)] # if some is included put it first in subj_dets and use this line
    
    model = UncertaintyLexicon(entities=[a,b,c],
                               shot_entities=shot_entities,
                               subj_dets=('every', 'exactly_one', 'no'),
                               obj_dets=('every', 'some', 'no'),
                               enrichable_dets=('some',),
                               proper_names=())
    model.double_quantifier_language()                            
    model.uncertainty_run(temperature=1.0, n=1)
    model.report()
    print model.final_listener2latex(digits=2)

    experiment = Experiment(src_filename="../data/basketball-pilot-2-11-14-results-parsed.csv")

    #analysis = Analysis(experiment=experiment, model=model, listenernorm_experiment=False, speakernorm_experiment=False, likertize_model=True)
    #analysis.listener_comparison_plot(output_filename="../fig/experiment-barplots.pdf", indices=mcfrank_ordering)

    analysis = Analysis(experiment=experiment, model=model, listenernorm_experiment=True, speakernorm_experiment=False)
    analysis.listener_correlation_plot(output_filename="../fig/experiment-scatterplot-explistenernorm.pdf")

    #analysis = Analysis(experiment=experiment, model=model, listenernorm_experiment=False, speakernorm_experiment=True)
    #analysis.listener_correlation_plot(output_filename="../fig/experiment-scatterplot-expspeakernorm.pdf")
