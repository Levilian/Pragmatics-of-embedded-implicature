#!/usr/bin/env python

from copy import copy
from iterative_lexical_uncertainty import LexicalUncertaintyModel
from grammar import UncertaintyGrammars
from utils import display_matrix
from experiment import *
from fragment import *
from analysis import *

######################################################################

def simple_scalar_inference_example():

    def lexicon_iterator():
        mats = [
            np.array([[0., 1., 1.], [0., 0., 1.], [1., 1., 1.]]),
            np.array([[0., 1., 0.], [0., 0., 1.], [1., 1., 1.]]),
            np.array([[0., 0., 1.], [0., 0., 1.], [1., 1., 1.]])]
        for mat in mats:
            yield mat

    mod = LexicalUncertaintyModel(
        lexicon_iterator=lexicon_iterator,
        messages=['A scored', 'A aced', 'NULL'],
        states=['N', 'S', 'A'],
        temperature=1.0,
        nullmsg=True,
        nullcost=5.0)

    mod.run(n=0)

    for lex in mod.lexicon_iterator():
        print "=" * 70
        print "Messages"
        display_matrix(lex, rnames=mod.messages, cnames=mod.states, digits=2)
        print 'l0'
        display_matrix(mod.l0(lex), rnames=mod.messages, cnames=mod.states, digits=2)
        print 's1'
        display_matrix(mod.S(lex), rnames=mod.states, cnames=mod.messages, digits=2)

    display_matrix(mod.final_listener,  rnames=mod.messages, cnames=mod.states, digits=2)
            
######################################################################

def complex_example():
    # General settings:
    players = [a,b]
    shots = [s1,s2]
    worlds = get_worlds(basic_states=(0,1,2), length=2, increasing=False)
    baselexicon = define_lexicon(player=players, shot=shots, worlds=worlds)   
    subjs = ('PlayerA', 'PlayerB', 'some_player', 'every_player', 'no_player')
    preds = ('scored', 'aced')
    temperature = 1.0
    nullmsg = True
    nullcost = 5.0 
    worldnames = [worldname(w) for w in worlds]
    messages = []
    for subj, pred in product(subjs, preds):
        msg = "%s %s" % (subj.replace("_", " "), pred)        
        formula = "iv(%s, %s)" % (subj, pred)
        messages.append((msg, formula))

    # Neo-Gricean refinement:
    neogram = UncertaintyGrammars(
        baselexicon=copy(baselexicon),
        messages=copy(messages),
        worlds=worlds,
        refinable={'some_player': ['exactly_one_player'], 'PlayerA': ['only_PlayerA'], 'PlayerB': ['only_PlayerB'], 'scored': ['scored_not_aced'], 'aced': []},
        nullmsg=nullmsg)
    neomod = LexicalUncertaintyModel(
        lexicon_iterator=neogram.lexicon_iterator,
        baselexicon=neogram.baselexicon_mat,
        messages=neogram.messages,
        states=worldnames,
        temperature=temperature,
        nullmsg=nullmsg,
        nullcost=nullcost)
    # Run and report:
    neomod.run(n=0)
    neomod.listener_report(digits=2)

    # Unconstrained refinement:
    ucgram = UncertaintyGrammars(
        baselexicon=copy(baselexicon),
        messages=copy(messages),
        worlds=worlds,
        refinable={'some_player': [], 'PlayerA': [], 'PlayerB': [], 'scored': [], 'aced': []},
        nullmsg=nullmsg)
    ucmod = LexicalUncertaintyModel(
        lexicon_iterator=ucgram.lexicon_iterator,
        baselexicon=ucgram.baselexicon_mat,
        messages=ucgram.messages,
        states=worldnames,
        temperature=temperature,
        nullmsg=nullmsg,
        nullcost=nullcost)
    # Run and report:
    ucmod.run(n=0)
    ucmod.listener_report(digits=2)  

######################################################################

def experiment_plot_and_report(
        src_filename='../data/basketball-pilot-2-11-14-results-parsed.csv',
        output_filename="../fig/basketball-pilot-2-11-14-results-parsed.pdf"):
    exp1 = Experiment(src_filename=src_filename)
    exp1.plot_targets(output_filename=output_filename)

######################################################################
    
def experimental_assessment(experiment_src="../data/basketball-pilot-2-11-14-results-parsed.csv",
                            plot_output_filename='temp.pdf'):
    # General settings:
    subjs= ('every_player', 'exactly_one_player', 'no_player')
    objs = ('every_shot', 'no_shot', 'some_shot')
    players = [a,b,c]
    shots = [s1,s2]
    basic_states = (0,1,2)
    worlds = get_worlds(basic_states=(0,1,2), length=3, increasing=True)
    baselexicon = define_lexicon(player=players, shot=shots, worlds=worlds)
    temperature = 1.0
    nullmsg = True
    nullcost = 5.0       
    worldnames = [worldname(w) for w in worlds]
    messages = []
    for d1, d2 in product(subjs, objs):
        subj = d1.replace("_player", "(player)")
        obj = d2.replace("_shot", "(shot)")
        msg = "%s(hit(%s))" % (subj, obj)
        formula = "iv(%s, tv(hit, %s, self.worlds, player))" % (d1,  d2)       
        messages.append((msg, formula))    
     
    # Unconstrained refinement:
    ucgram = UncertaintyGrammars(
        baselexicon=copy(baselexicon),
        messages=copy(messages),
        worlds=copy(worlds),        
        refinable={'some_player': [], 'some_shot': []},
        nullmsg=nullcost)
    ucmod = LexicalUncertaintyModel(
        name="Unconstrained",
        lexicon_iterator=ucgram.lexicon_iterator,
        baselexicon=ucgram.baselexicon_mat,
        messages=ucgram.messages,
        states=worldnames,
        temperature=temperature,
        nullmsg=nullmsg,
        nullcost=nullcost)

    # Neo-Gricean refinement:
    neogram = UncertaintyGrammars(
        baselexicon=copy(baselexicon),
        messages=copy(messages),
        worlds=copy(worlds),        
        refinable={'some_player': ['exactly_one_player'], 'some_shot': ['exactly_one_shot']},
        nullmsg=nullcost)    
    neomod = LexicalUncertaintyModel(
        name="Neo-Gricean",
        lexicon_iterator=neogram.lexicon_iterator,
        baselexicon=neogram.baselexicon_mat,
        messages=neogram.messages,
        states=worldnames,
        temperature=temperature,
        nullmsg=nullmsg,
        nullcost=nullcost)
    
    # Run the models, going only to the first uncertainty listener (n=0):
    ucmod.run(n=0)
    neomod.run(n=0)
        
    # The analysis:
    analysis = Analysis(experiment=Experiment(experiment_src), models=[ucmod, neomod])    
    analysis.overall_analysis()
    analysis.analysis_by_message()
    analysis.comparison_plot(plot_output_filename='temp.pdf')

    
######################################################################


if __name__ == '__main__':

    #simple_scalar_inference_example()
    complex_example()
    #experiment_plot_and_report()
    #experimental_assessment()


