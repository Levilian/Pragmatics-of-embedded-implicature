from pragmod import LexicalUncertaintyModel
from grammar import UncertaintyGrammars
from experiment import *
from fragment import *
from analysis import *


def experimental_assessment(
        subjs=('every_player', 'exactly_one_player', 'no_player'),
        objs=('every_shot', 'no_shot', 'some_shot'),
        refinable={'some_player': ['exactly_one_player'], 'some_shot': ['exactly_one_shot']},
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
        msg = "%s(hit(%s))" % (subj, obj)
        formula = "iv(%s, tv(hit, %s, self.worlds, player))" % (d1,  d2)       
        messages.append((msg, formula))

    ug = UncertaintyGrammars(
        baselexicon=baselexicon,
        messages=messages,
        worlds=worlds,        
        refinable=refinable,
        nullmsg=True)
    
    mod = LexicalUncertaintyModel(
        name="Neo-Gricean",
        lexicon_iterator=ug.lexicon_iterator,
        baselexicon=ug.baselexicon_mat,
        messages=ug.messages,
        states=[worldname(w) for w in worlds],
        temperature=1.0,
        nullmsg=True,
        nullcost=5.0)
    
    mod.run(n=0)
    #mod.listener_report(digits=2)
    
    analysis = Analysis(
        experiment=Experiment(src_filename="../data/basketball-pilot-2-11-14-results-parsed.csv"),
        models=[mod])
    
    #analysis.overall_analysis()
    #analysis.analysis_by_message()
    analysis.comparison_plot(output_filename='temp.pdf')
        

experimental_assessment()
