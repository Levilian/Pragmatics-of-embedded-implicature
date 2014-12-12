#!/usr/bin/env python

import os
import numpy as np
from collections import defaultdict
from pragmod import LexicalUncertaintyModel
from grammar import UncertaintyGrammars
from experiment import Experiment, SENTENCES
from analysis import Analysis
from fragment import *
from plots import general_comparison_plot
from utils import colors


every_some_clustering = {
    "NNN": "False",
    "NNS": "False",
    "NNA": "False",
    "NAA": "False",
    "NSA": "False",
    "NSS": "False",
    "SSS": "Local",
    "SSA": "Literal-only",
    "SAA": "Literal-only",
    "AAA": "Literal-only"}

exactlyone_some_clustering = {
    "NNN": "False",
    "NNS": "Literal/Local",
    "NNA": "Literal-only",
    "NAA": "False",
    "NSA": "Local",
    "NSS": "False",
    "SSS": "False",
    "SSA": "False",
    "SAA": "Local",
    "AAA": "False"}

######################################################################

def simplescalar():

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

    def fmt_lex(lex):
        x = map(str, lex.flatten())
        x = r"\genericscalar{%s}" % "}{".join(x)
        x = x.replace("1.0", r"\True").replace("0.0", r"\False")
        return x

    def fmt_lis(lis):
        x = num_fmt(lis)     
        return r"\genericscalar{%s}" % "}{".join(x)

    def fmt_spk(spk):
        x = num_fmt(spk)         
        return r"\scalarspeaker{%s}" % "}{".join(x)
    
    def num_fmt(x):
        x = x.flatten()
        x = np.round(x, 2)
        x = [str(y).replace("0.", r".") for y in x]
        return x

    print r"\Lex"
    for lex in lexicon_iterator():
        print fmt_lex(lex) + "\n & "
    print r"\\"
    print r"& \uparrow & \uparrow & \uparrow \\"
    print r"\listenerZero"
    for lex in lexicon_iterator():         
        print fmt_lis(mod.l0(lex)) + "\n & "
    print r"\\"
    print r"& \uparrow & \uparrow & \uparrow \\"
    print r"\speakerOne"
    for lex in lexicon_iterator():
        print fmt_spk(mod.S(lex)) + "\n & "
    print r"\\"
    print r"\UncertaintyListener"
    mod.run()    
    print fmt_lis(mod.final_listener.flatten())

######################################################################
    
def illustration_subj():
    players = [a,b]
    shots = [s1,s2]
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

def illustration_subj_large():

    players = [a,b]
    shots = [s1,s2]
    worlds = get_worlds(basic_states=(0,1,2), length=2, increasing=False)
    baselexicon = define_lexicon(player=players, shot=shots, worlds=worlds)

    messages = []
    subjs = ('PlayerA', 'PlayerB', 'some_player', 'every_player', 'no_player')
    preds = ('scored', 'aced')
    for subj, pred in product(subjs, preds):
        msg = "%s %s" % (subj.replace("_", " "), pred)        
        formula = "iv(%s, %s)" % (subj, pred)
        messages.append((msg, formula))
        
    ug = UncertaintyGrammars(
        baselexicon=baselexicon,
        messages=messages,
        worlds=worlds,
        refinable=['some_player', 'PlayerA', 'PlayerB', 'scored', 'aced'],
        nullmsg=True)

    mod = LexicalUncertaintyModel(
        lexicon_iterator=ug.lexicon_iterator,
        baselexicon=ug.baselexicon_mat,
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
        baselexicon=ug.baselexicon_mat,
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
            likertize_model=True).correlation_analysis()

        # Analysis(
        #     experiment=experiment,
        #     model=mod,
        #     listenernorm_experiment=False,
        #     speakernorm_experiment=False,
        #     likertize_model=False).to_csv('embeddedscalars-exp01-analysis-2014-12-04.csv')

        Analysis(
            experiment=experiment,
            model=mod,
            listenernorm_experiment=False,
            speakernorm_experiment=False,
            likertize_model=True).message_specific_clustered_correlation_analysis("Exactly one player hit some of his shots", exactlyone_some_clustering)

        Analysis(
            experiment=experiment,
            model=mod,
            listenernorm_experiment=False,
            speakernorm_experiment=False,
            likertize_model=True).message_specific_clustered_correlation_analysis("Every player hit some of his shots", every_some_clustering)
        
        # Analysis(
        #     experiment=experiment,
        #     model=mod,
        #     listenernorm_experiment=False,
        #     speakernorm_experiment=False,
        #     likertize_model=True).listener_comparison_plot(output_filename=filename_root+"barplots.pdf", nrows=3, ncols=3)    

        # Analysis(
        #     experiment=experiment,
        #     model=mod,
        #     listenernorm_experiment=True,
        #     speakernorm_experiment=False,
        #     likertize_model=False).listener_comparison_plot(output_filename=filename_root+"barplots-listenernorm.pdf", nrows=3, ncols=3)

        # Analysis(
        #     experiment=experiment,
        #     model=mod,
        #     listenernorm_experiment=False,
        #     speakernorm_experiment=True,
        #     likertize_model=False).listener_comparison_plot(output_filename=filename_root+"barplots-speakernorm.pdf", nrows=3, ncols=3)

        # Analysis(
        #     experiment=experiment,
        #     model=mod,
        #     listenernorm_experiment=False,
        #     speakernorm_experiment=False).listener_correlation_plot(output_filename=filename_root+"scatterplot.pdf")
    
        # Analysis(
        #     experiment=experiment,
        #     model=mod,
        #     listenernorm_experiment=True,
        #     speakernorm_experiment=False).listener_correlation_plot(output_filename=filename_root+"scatterplot-listenernorm.pdf")
        
        # Analysis(
        #     experiment=experiment,
        #     model=mod,
        #     listenernorm_experiment=False,
        #     speakernorm_experiment=True).listener_correlation_plot(output_filename=filename_root+"scatterplot-speakernorm.pdf")

    return mod


def crucial_item_mod_exp_compare(mod, exp, msg, clustering, output_filename=None, axis_width=6):    
    listener = mod.final_listener
    mod_msg = SENTENCES[msg]          
    d = defaultdict(list)
    lis_row = listener[mod.messages.index(mod_msg)]
    for j, w in enumerate(mod.states):
        d[clustering[w]].append(lis_row[j])
    cnames = sorted(set(clustering.values()))
    vals = []
    cis = []
    for cname in cnames:
        vals.append(np.mean(d[cname]))
        cis.append((0.0, 0.0))
    vals = 1.0 + (6.0 * np.array(vals))
    exp_means, exp_cis = exp.analyze_clustered_item(msg, clustering)
    general_comparison_plot(rows=[vals, exp_means],
                            confidence_intervals=[cis, exp_cis],
                            rnames=[""],
                            cnames=cnames,
                            output_filename=output_filename,
                            width=0.8,
                            gap=0.2,
                            legend=True,
                            axis_width=axis_width,
                            title=msg,
                            bbox_to_anchor=(-0.1,1.4),
                            labels=("Model", "Human"))
        
def crucial_items():

    exp1 = Experiment(src_filename='../data/basketball-pilot-2-11-14-results-parsed.csv')
    exp2a = Experiment(src_filename='../data/basketball-focus-only-manip-3-17-14-results-parsed.csv',  subjectCondition="focus")    
    exp2b = Experiment(src_filename='../data/basketball-focus-only-manip-3-17-14-results-parsed.csv',  subjectCondition="only")
    mod = experimental_assessment(
        analysis=False,
        subjs=('every_player', 'exactly_one_player', 'no_player', 'some_player'),
        objs=('every_shot', 'no_shot', 'some_shot'),
        refinable=('some_player', 'some_shot'),
        file_prefix = "experiment",
        experiment=Experiment(src_filename="../data/basketball-pilot-2-11-14-results-parsed.csv"))

    crucial_item_mod_exp_compare(
        mod,
        exp1,
        "Every player hit some of his shots",
        every_some_clustering,
        output_filename="../fig/every-some-modcmp.pdf",
        axis_width=5.2)
    crucial_item_mod_exp_compare(
        mod,
        exp1,
        "Exactly one player hit some of his shots",
        exactlyone_some_clustering,
        output_filename="../fig/exactlyone-some-modcmp.pdf",
        axis_width=7)

    mus = []
    cis = []
    for exp, sent in ((exp1, "Exactly one player hit some of his shots"),
                      (exp2a, "Exactly one player hit <b>SOME</b> of his shots"),
                      (exp2b, "Exactly one player hit only some of his shots")):
        mu, ci = exp.analyze_clustered_item(sent, exactlyone_some_clustering)
        mus.append(mu)
        cis.append(ci)
    general_comparison_plot(rows=mus,
                     confidence_intervals=cis,
                     rnames=[""],
                     cnames=sorted(set(exactlyone_some_clustering.values())),
                     output_filename="../fig/exactlyone-some-expcmp.pdf",
                     width=1.75,
                     gap=0.2,
                     legend=True,
                     axis_width=6,
                     title="Exactly one player hit some of his shots",
                     colors=[colors[0], colors[2], colors[3]])

    general_comparison_plot(rows=[mus[0]],
                            confidence_intervals=[cis[0]],
                            rnames=[""],
                            cnames=sorted(set(exactlyone_some_clustering.values())),
                            output_filename="../fig/exactlyone-some.pdf",
                            width=1.5,
                            gap=0.0,
                            legend=False,
                            axis_width=6,
                            title="Exactly one player hit some of his shots")


    mus = []
    cis = []
    for exp, sent in ((exp1, "Every player hit some of his shots"),
                      (exp2a, "Every player hit <b>SOME</b> of his shots"),
                      (exp2b, "Every player hit only some of his shots")):
        mu, ci = exp.analyze_clustered_item(sent, every_some_clustering)
        mus.append(mu)
        cis.append(ci)
    general_comparison_plot(rows=mus,
                            confidence_intervals=cis,
                            rnames=[""],
                            cnames=sorted(set(every_some_clustering.values())),
                            output_filename="../fig/every-some-expcmp.pdf",
                            width=1.5,
                            gap=0.2,
                            legend=True,
                            axis_width=5,
                            title="Every player hit some of his shots",
                            colors=[colors[0], colors[2], colors[3]])

    general_comparison_plot(rows=[mus[0]],
                            confidence_intervals=[cis[0]],
                            rnames=[""],
                            cnames=sorted(set(every_some_clustering.values())),
                            output_filename="../fig/every-some.pdf",
                            width=1.2,
                            gap=0.0,
                            legend=False,
                            axis_width=5,
                            title="Every player hit some of his shots")

######################################################################

if __name__ == '__main__':

    #crucial_items()

    #simplescalar()

    #illustration_subj_large()

    #illustration_subj()
    #illustration_pred()
    
    experimental_assessment(
        analysis=True,
        subjs=('every_player', 'exactly_one_player', 'no_player'),
        objs=('every_shot', 'no_shot', 'some_shot'),
        refinable=('some_player', 'some_shot'),
        file_prefix = "experiment",
        experiment=Experiment(src_filename="../data/basketball-pilot-2-11-14-results-parsed.csv"))

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
    # experimental_assessment(
    #     analysis=True,
    #     subjs=('every_player', 'exactly_one_player', 'no_player'),
    #     objs=('every_shot', 'no_shot', 'exactly_one_shot'),
    #     refinable=('some_player',),
    #     file_prefix="only",
    #     experiment=Experiment(src_filename='../data/basketball-focus-only-manip-3-17-14-results-parsed.csv',  subjectCondition="only"))

    
