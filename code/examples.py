#!/usr/bin/env python

import os
from pragmod import LexicalUncertaintyModel
from grammar import UncertaintyGrammars
from experiment import Experiment
from analysis import Analysis
from fragment import *

######################################################################
    
def illustration_subj():
    players = [a,b]
    shots = [s1,s2]
    basic_states = (0,1)
    worlds = get_worlds(basic_states=(0,1), length=2, increasing=False)
    baselexicon = define_lexicon(player=players, shot=shots, worlds=worlds)

    ug = UncertaintyGrammars(
        baselexicon=baselexicon,
        messages=[("PlayerA(scored)",       "iv(PlayerA, scored)"),
                  ("PlayerB(scored)",       "iv(PlayerB, scored)"),
                  ("every(player)(scored)", "iv(fa(every, player), scored)"),
                  ("no(player)(scored)",    "iv(fa(no, player), scored)"),
                  ("some_player(scored)",   "iv(some_player, scored)")],
        worlds=worlds,
        refinable=['some_player', 'PlayerA', 'PlayerB'], #, 'scored'],
        nullmsg=True)

    mod = LexicalUncertaintyModel(
        lexicon_iterator=ug.lexicon_iterator,
        messages=ug.messages,
        states=[worldname(w) for w in worlds],
        temperature=1.0,
        nullmsg=True,
        nullcost=5.0)

    mod.run()
    mod.listener_report()

def illustration_pred():
    players = [a,b]
    shots = [s1,s2]
    basic_states = (0,1,2)
    worlds = get_worlds(basic_states=(0,1,2), length=2, increasing=False)
    baselexicon = define_lexicon(player=players, shot=shots, worlds=worlds)

    ug = UncertaintyGrammars(
        baselexicon=baselexicon,
        messages=[("PlayerA(scored)",  "iv(PlayerA, scored)"),
                  ("PlayerB(scored)",  "iv(PlayerB, scored)"),
                  ("PlayerA(doubled)", "iv(PlayerA, doubled)"),
                  ("PlayerB(doubled)", "iv(PlayerB, doubled)")],
        worlds=worlds,
        refinable=['scored', 'doubled'],
        nullmsg=True)

    mod = LexicalUncertaintyModel(
        lexicon_iterator=ug.lexicon_iterator,
        messages=ug.messages,
        states=[worldname(w) for w in worlds],
        temperature=1.0,
        nullmsg=True,
        nullcost=5.0)

    mod.run()
    mod.listener_report(digits=5)

def experimental_assessment(
        analysis=True,
        subjs=('every_player', 'exactly_one_player', 'no_player'),
        objs=('every_shot', 'no_shot', 'some_shot'),
        refinable=('some_player', 'some_shot'),
        file_prefix = "experiment",
        experiment=Experiment(src_filename="../data/basketball-pilot-2-11-14-results-parsed.csv")):
    players = [a,b,c]
    shots = [s1,s2]
    basic_states = (0,1,2)
    worlds = get_worlds(basic_states=(0,1,2), length=3, increasing=True)
    baselexicon = define_lexicon(player=players, shot=shots, worlds=worlds)

    messages = []        
    for d1, d2 in product(subjs, objs):
        subj = d1.replace("_player", "(player)")
        obj = d2.replace("_shot", "(shot)")
        msg = "%s(made(%s))" % (subj, obj)
        formula = "iv(%s, tv(made, %s, self.worlds, player))" % (d1,  d2)       
        messages.append((msg, formula))
    
    ug = UncertaintyGrammars(
        baselexicon=baselexicon,
        messages=messages,
        worlds=worlds,
        refinable=refinable,
        nullmsg=True)

    mod = LexicalUncertaintyModel(
        lexicon_iterator=ug.lexicon_iterator,
        messages=ug.messages,
        states=[worldname(w) for w in worlds],
        temperature=1.0,
        nullmsg=True,
        nullcost=5.0)

    mod.run(n=0)
    mod.listener_report(digits=2)

    if analysis:
    
        filename_root = os.path.join('..', 'fig', '%s-' % file_prefix)
    
        Analysis(
            experiment=experiment,
            model=mod,
            listenernorm_experiment=False,
            speakernorm_experiment=False,
            likertize_model=True).listener_comparison_plot(output_filename=filename_root+"barplots.pdf", nrows=3, ncols=3)    

        Analysis(
            experiment=experiment,
            model=mod,
            listenernorm_experiment=True,
            speakernorm_experiment=False,
            likertize_model=False).listener_comparison_plot(output_filename=filename_root+"barplots-listenernorm.pdf", nrows=3, ncols=3)

        Analysis(
            experiment=experiment,
            model=mod,
            listenernorm_experiment=False,
            speakernorm_experiment=True,
            likertize_model=False).listener_comparison_plot(output_filename=filename_root+"barplots-speakernorm.pdf", nrows=3, ncols=3)

        Analysis(
            experiment=experiment,
            model=mod,
            listenernorm_experiment=False,
            speakernorm_experiment=False).listener_correlation_plot(output_filename=filename_root+"scatterplot.pdf")
    
        Analysis(
            experiment=experiment,
            model=mod,
            listenernorm_experiment=True,
            speakernorm_experiment=False).listener_correlation_plot(output_filename=filename_root+"scatterplot-listenernorm.pdf")
        
        Analysis(
            experiment=experiment,
            model=mod,
            listenernorm_experiment=False,
            speakernorm_experiment=True).listener_correlation_plot(output_filename=filename_root+"scatterplot-speakernorm.pdf")
            
######################################################################

if __name__ == '__main__':

    #illustration_subj()
    #illustration_pred()
    
    # experimental_assessment(
    #     analysis=True,
    #     subjs=('every_player', 'exactly_one_player', 'no_player'),
    #     objs=('every_shot', 'no_shot', 'some_shot'),
    #     refinable=('some_player', 'some_shot'),
    #     file_prefix = "experiment",
    #     experiment=Experiment(src_filename="../data/basketball-pilot-2-11-14-results-parsed.csv"))

    # Adding 'exactly one', like 'only', to the set of object quantifiers
    # means that we don't get the embedded scalar implicature under
    # 'exactly one' -- that reading loses out to the literal encoding.
    # The every/some case is also weakened but not totally lost.
    # experimental_assessment(
    #     analysis=False,
    #     subjs=('every_player', 'exactly_one_player', 'no_player'),
    #     objs=('every_shot', 'no_shot', 'some_shot', 'exactly_one_shot'),
    #     refinable=('some_player', 'some_shot'),
    #     file_prefix=None,
    #     experiment=None)

    
    # Modeling the 'only' experiment ('exactly one' is synonymous
    # with 'only some' in our model of the scenario):
    experimental_assessment(
        analysis=True,
        subjs=('every_player', 'exactly_one_player', 'no_player'),
        objs=('every_shot', 'no_shot', 'exactly_one_shot'),
        refinable=('some_player',),
        file_prefix="only",
        experiment=Experiment(src_filename='../data/basketball-focus-only-manip-3-17-14-results-parsed.csv',  subjectCondition="only"))

    
