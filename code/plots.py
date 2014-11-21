import itertools
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

##plt.style.use('ggplot')
COLORS = matplotlib.colors.cnames.values()

PROB_LIMS = [0, 1.1]
LIKERT_LIMS = [0, 8]
PROB_AXIS_TICKS = np.arange(0.0, 1.1, 0.1)
LIKERT_AXIS_TICKS = np.arange(0.0, 8.0, 1.0)

######################################################################

def message_state_barplot(mat=None,
                          confidence_intervals=None,
                          rnames=[],
                          cnames=[],
                          nrows=None,
                          ncols=None,
                          output_filename=None,                          
                          indices=[],
                          ylim=None,
                          yticks=None,
                          ylabel="",
                          width=1.0,
                          axis_width=7,
                          axis_height=3):
    # Default to a single row of plots if no guidance was given:
    if not nrows:
        nrows = 1
        ncols = len(rnames)
    # Basic figure dimensions and design:
    fig, axarray = plt.subplots(nrows=nrows, ncols=ncols)
    fig.set_figheight(axis_height*nrows)
    fig.set_figwidth(axis_width*ncols)    
    fig.subplots_adjust(bottom=-1.0)
    # Axes:
    pos = np.arange(0.0, len(cnames)*width, width)
    xlim = [0.0, len(cnames)*width]
    xticks = pos+(width/2.0)    
    # If indices doesn't specify an ordering, create an array of
    # axis coordinate pairs for the plot:
    if not indices:
        if nrows == 1:
            indices = list(range(ncols))
        else:
            indices = list(itertools.product(range(nrows), range(ncols)))
    # Left edges of the bars:    
    # Plot each row as an axis:
    for i, row in enumerate(mat):
        axindex = indices[i]
        ax = axarray[axindex]
        ax.bar(pos, row, width)
        ax.set_title(rnames[i])
        # Axis label only for the leftmost plots:
        if (isinstance(axindex, int) and axindex == 0) or (isinstance(axindex, tuple) and axindex[1] == 0):
            ax.set_ylabel(ylabel, fontsize=14)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_xticks(xticks)
        ax.set_xticklabels(cnames, fontsize=14, rotation='vertical', color='black')
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticks)
        # Confidence intervals:
        if confidence_intervals:
            add_confidence_intervals(ax=ax, pos=pos+(width/2.0), cis=confidence_intervals[i])
    # Output:
    if output_filename:
        plt.savefig(output_filename, bbox_inches='tight')
    else:
        plt.show()

######################################################################
                        
def comparison_plot(modmat=None,
                    expmat=None,
                    confidence_intervals=None,
                    correlation_texts=None,
                    rnames=None,
                    cnames=None,
                    nrows=None,
                    ncols=None,
                    output_filename=None,                          
                    indices=[],                    
                    ylabel="",
                    ylim=None,
                    yticks=None,
                    width=0.5,
                    gap=0.2,
                    axis_width=7,
                    axis_height=3):
    # Default to a single row of plots if no guidance was given:
    if not nrows:
        nrows = 1
        ncols = len(rnames)
    # Basic figure dimensions and design:
    fig, axarray = plt.subplots(nrows=nrows, ncols=ncols)
    fig.set_figheight(axis_height*nrows)
    fig.set_figwidth(axis_width*ncols)
    fig.subplots_adjust(bottom=-0.5)
    # Plot dimensions:
    barsetwidth = (width*2)+gap
    pos = np.arange(0, len(cnames)+barsetwidth, barsetwidth)
    xlim = [0.0, len(cnames)+((len(cnames)-1)*gap)]       
    xticks = pos+(barsetwidth/2.0)
    # If indices doesn't specify an ordering, create an array of
    # axis coordinate pairs for the plot:
    if not indices:
        indices = list(itertools.product(range(nrows), range(ncols)))    
    # Plot each row as an axis:
    for i, row in enumerate(modmat):
        axindex = indices[i]
        ax = axarray[axindex]
        ax.bar(pos, row, width, label="Model")
        ax.bar(pos+width, expmat[i], width, color="#A60628", label="Human")
        ax.set_title(rnames[i])
        ax.set_ylabel(ylabel, fontsize=14)                 
        ax.set_xlim(xlim)
        ax.set_xticks(xticks)
        ax.set_xticklabels(cnames, fontsize=14,  rotation='vertical', color='black')
        ax.set_ylim(ylim)
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticks)
        # Confidence intervals:
        if confidence_intervals:
            add_confidence_intervals(ax=ax, pos=pos+(width*1.5), cis=confidence_intervals[i])
        # Correlation annotations:
        if correlation_texts:            
            ax.text(0, ylim[1], correlation_texts[i], fontsize=14, verticalalignment='top', horizontalalignment='left')
    plt.legend(loc='upper left', bbox_to_anchor=(-2.5, 3.7), ncol=2, fontsize=16)
    # Output:
    if output_filename:
        plt.savefig(output_filename, bbox_inches='tight')
    else:
        plt.show()             

######################################################################
                          
def correlation_plot(xmat=None,                     
                     ymat=None,
                     xlabel=None,
                     ylabel=None,
                     alpha=1.0,
                     correlation_text=None,
                     confidence_intervals=None,
                     output_filename=None):
    # Axis set-up:
    xlim = axis_buffer(xmat)
    ylim = axis_buffer(ymat)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    # Figure set-up:
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_figheight(5)
    fig.set_figwidth(10)
    # Plots:
    for i, row in enumerate(xmat):
        ax.plot(row, ymat[i], alpha=alpha, color=COLORS[i], markersize=6, marker='o', linestyle='')
        # Confidence intervals:
        if confidence_intervals:
            add_confidence_intervals(ax=ax, pos=row, cis=confidence_intervals[i])   
    ax.set_xlabel(xlabel, fontsize=14)                
    ax.set_ylabel(ylabel, fontsize=14)
    # Add correlation analysis summary if available:
    if correlation_text:
        ax.text(xlim[1], ylim[0], correlation_text, fontsize=14, verticalalignment='bottom', horizontalalignment='right')    
    # Output:
    if output_filename:
        plt.savefig(output_filename, bbox_inches='tight')
    else:
        plt.show()

######################################################################
               
def axis_buffer(vals, buffer_percentage=0.05):
    buff = np.max(vals)*buffer_percentage
    return [np.min(vals)-buff, np.max(vals)+buff]

def add_confidence_intervals(ax=None, pos=None, cis=None):
    for j, xpos in enumerate(pos):
        ax.plot([xpos, xpos], cis[j], linewidth=2, color='black') 
