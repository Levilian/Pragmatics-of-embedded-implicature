import sys
from copy import copy
import numpy as np
try:
    from plots import *
except:
    pass
from utils import rownorm, colnorm, safelog, display_matrix

######################################################################
        
class LexicalUncertaintyModel:
    def __init__(self,
                 name="",
                 lexicon_iterator=None,
                 baselexicon=None,
                 messages=None,
                 states=None,
                 lexcount=None,
                 stateprior=None,
                 lexprior=None,
                 costs=None,
                 temperature=1.0,
                 nullmsg=True,
                 nullcost=5.0):
        self.name = name
        self.lexicon_iterator = lexicon_iterator
        self.baselexicon = baselexicon
        self.messages = messages
        self.states = states
        self.stateprior = stateprior
        self.lexprior = lexprior
        self.lexcount = lexcount
        self.costs = costs
        self.temperature = temperature
        self.nullmsg = nullmsg
        self.nullcost = nullcost
        # If no state prior is given, define a flat prior over states:
        if self.stateprior == None:
            self.stateprior = np.repeat(1.0/len(self.states), len(self.states))
        # If no lexicon prior is given, but we do know the number of lexica,
        # define a flat prior over lexica. If no count is given, we lead this
        # undefined and the lexicon prior is implicitly flat.             
        if self.lexprior == None and self.lexcount != None:
            self.lexprior = np.repeat(1.0/self.lexcount, self.lexcount)        
        if self.costs == None:
            self.costs = np.zeros(len(self.messages))
            if self.nullmsg:
                self.costs[-1] = self.nullcost
        # This is the listener matrix that we build with self.run:
        self.final_listener = np.zeros((len(self.messages), len(self.states)))
        # This will get fill in if we reason beyond the lexical uncertainty listener:
        self.final_speaker = None

    def rsa(self):
        lit = self.l0(self.baselexicon)
        spk = self.S(lit)
        lis = self.L(spk)
        return [lit, spk, lis]

    def run(self, n=0, display_progress=True):
        # If there is no lexicon prior, then this allows us to ignore it.
        lexprior_func = (lambda x : 1.0)
        # Where we have a lexicon prior, we can look up the value in self.lexprior:
        if self.lexprior != None:
            lexprior_func = (lambda lexindex : self.lexprior[lexindex])
        # Iterate through the lexica:
        for lexindex, lex in enumerate(self.lexicon_iterator()):
            if display_progress and lexindex and lexindex % 10**2 == 0:
                sys.stderr.write('\r'); sys.stderr.write('lexicon %s' % lexindex) ; sys.stderr.flush()
            self.final_listener += lexprior_func(lexindex) * self.S(self.l0(lex)).T            
        # Update or fill in the lexcount based on the iteration:
        self.lexcount = lexindex + 1
        # Final normalization and state prior incorporation:
        self.final_listener = rownorm( self.stateprior * self.final_listener)
        # Optional further iteration of L and S with no lexical uncertainty:
        for i in range(n):
            self.final_speaker = self.S(self.final_listener)
            self.final_listener = self.L(self.final_speaker)

    def l0(self, lex):
        """Literal listener normalizing the boolean lexicon and incorporating the prior."""
        return rownorm(lex * self.stateprior)    

    def L(self, spk):
        """The general listener differs from l0 only in transposing the incoming speaker matrix."""
        return self.l0(spk.T)

    def S(self, lis):
        """Bayesian speaker incorporating costs."""
        return rownorm(np.exp(self.temperature * (safelog(lis.T) - self.costs)))

    def listener_report(self, digits=4):
        print "======================================================================"
        print 'Lexica:', self.lexcount
        print 'Final listener'
        display_matrix(self.final_listener, rnames=self.messages, cnames=self.states, digits=digits)
        print '\nBest inferences:'
        best_inferences = self.get_best_inferences(digits=digits)  
        for msg, val in sorted(best_inferences.items()):
            print "\t", msg, val
        print "\nLaTeX table:\n"
        print self.final_listener2latex()

    def get_best_inferences(self, digits=4):    
        best_inferences = {}
        # Round to avoid tiny distinctions that don't even display:
        mat = np.round(copy(self.final_listener), 10)
        for i, msg in enumerate(self.messages):
            best_inferences[msg] = [(w, str(np.round(mat[i,j], digits))) for j, w in enumerate(self.states) if mat[i,j] == np.max(mat[i])]             
        return best_inferences   

    def final_listener2latex(self, digits=2):
        mat = np.round(copy(self.final_listener), digits)
        rows = []
        rows.append([''] + self.states)
        for i in range(len(self.messages)):
            rowmax = np.max(mat[i])
            def highlighter(x): return r"\graycell{%s}" % x if x == rowmax else str(x)
            vals = [highlighter(x) for x in mat[i]]            
            rows.append([self.messages[i]] + vals)
        s = ""
        s += "\\begin{tabular}[c]{r *{%s}{r} }\n" % len(self.states)
        s += "\\toprule\n"
        s += "%s\\\\\n" % " & ".join(rows[0])
        s += "\\midrule\n"
        for row in rows[1: ]:
            s += "%s\\\\\n" % " & ".join(row)
        s += "\\bottomrule\n"
        s += "\\end{tabular}"
        return s

    def final_listener2plot(self,
                            nrows=None,
                            ncols=None,
                            output_filename=None,                            
                            include_null=True,
                            indices=[]):
        if not nrows:
            nrows = 1
            ncols = len(self.messages)
        ylabel = r"$L(w \mid m)$"
        mat = copy(self.final_listener)
        if not include_null:
            mat = mat[:-1]
            ncols -= 1
        message_state_barplot(mat=mat,
                              rnames=self.messages,
                              cnames=self.states,
                              nrows=nrows,
                              ncols=ncols,
                              output_filename=output_filename,
                              indices=indices,
                              ylim=PROB_LIMS,
                              yticks=PROB_AXIS_TICKS,
                              ylabel=ylabel)

     
######################################################################

if __name__ == '__main__':

    def manner_example():
    
        def lexicon_iterator():

            nullsem = [1.0, 1.0]
            TT = [1.0, 1.0]
            TF = [1.0, 0.0]
            FT = [0.0, 1.0]
                
            lexica = [
                np.array([TT, TT, nullsem]),
                np.array([TT, TF, nullsem]),
                np.array([TT, FT, nullsem]),
                np.array([TF, TT, nullsem]),
                np.array([TF, TF, nullsem]),
                np.array([TF, FT, nullsem]),
                np.array([FT, TT, nullsem]),
                np.array([FT, TF, nullsem]),
                np.array([FT, FT, nullsem]) ]

            for lex in lexica:
                yield lex

        mod = LexicalUncertaintyModel(
            lexicon_iterator=lexicon_iterator,
            messages=['short','long','null'],
            states=['usual', 'unusual'],
            stateprior=np.array([2.0/3.0, 1.0/3.0]),
            costs=np.array([1.0, 2.0, 5.0]),
            temperature=2.0)

        mod.run(n=3)
        
        mod.listener_report()

        #mod.final_listener2plot(output_filename=None)

    manner_example()
    
