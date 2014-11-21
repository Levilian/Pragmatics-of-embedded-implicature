from copy import copy
from pragmod import LexicalUncertaintyModel
from grammar import UncertaintyGrammars
from fragment import *
    
def illustration():
    players = [a,b]
    shots = [s1,s2]
    basic_states = (0,1)
        
    lex = copy(BASELEXICON)
    lex[("some_player", TYPE_NP)] =  (lambda Y : len(set(players) & set(Y)) > 0)
    lex[("every_player", TYPE_NP)] = (lambda Y : set(players) <= set(Y))
    lex[("no_player", TYPE_NP)] =    (lambda Y : len(set(players) & set(Y)) == 0)        

    ug = UncertaintyGrammars(
        baselexicon=lex,
        messages=["PlayerA(scored)", "PlayerB(scored)", "every_player(scored)", "no_player(scored)", "some_player(scored)"],
        worlds=WorldSet(basic_states=basic_states, p=players, s=shots, increasing=False),
        refinable={'some_player': [a,b]},
        nullmsg=True)

    mod = LexicalUncertaintyModel(
        lexicon_iterator=ug.lexicon_iterator,
        messages=ug.messages,
        states=ug.worlds.names,
        temperature=1.0,
        nullmsg=True,
        nullcost=5.0)

    mod.run()
    mod.listener_report()

######################################################################

if __name__ == '__main__':

    illustration()

