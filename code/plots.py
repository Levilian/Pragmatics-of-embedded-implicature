import itertools
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

plt.style.use('ggplot')
COLORS = matplotlib.colors.cnames.values()


def message_state_barplot(mat=None,
                          confidence_intervals=None,
                          rnames=[],
                          cnames=[],
                          nrows=None,
                          ncols=None,
                          output_filename=None,                          
                          indices=[],
                          xlim=None,
                          ylim=None,
                          yaxis=None,
                          ylabel="",
                          width=1.0,
                          axis_width=7,
                          axis_height=3):
    if not nrows:
        nrows = 1
        ncols = len(rnames)           
    fig, axarray = plt.subplots(nrows=nrows, ncols=ncols)
    fig.set_figheight(axis_height*nrows)
    fig.set_figwidth(axis_width*ncols)    
    fig.subplots_adjust(bottom=-1.0)
    # If indices doesn't specify an ordering, create an array of
    # axis coordinate pairs for the plot:
    if not indices:
        indices = list(itertools.product(range(nrows), range(ncols)))
    # Left edges of the bars:
    pos = np.arange(0.0, len(cnames)*width, width)
    # Plot each row as an axis:
    for i, row in enumerate(mat):
        axindex = indices[i]
        ax = axarray[axindex]
        ax.bar(pos, row, width)
        ax.set_title(rnames[i])
        # Axis label only for the leftmost plots
        if axindex[1] == 0:
            ax.set_ylabel(ylabel, fontsize=14)
        if xlim != None:
            ax.set_xlim(xlim)
        if ylim != None:
            ax.set_ylim(ylim)
        ax.set_xticks(pos+(width/2.0))
        ax.set_xticklabels(cnames, fontsize=14, rotation='vertical', color='black')
        if yaxis != None:
            ax.set_yticks(yaxis)
            ax.set_yticklabels(yaxis)
        # Confidence intervals:
        if confidence_intervals:
            add_confidence_intervals(ax=ax, pos=pos, cis=confidence_intervals[i], width=width)
    # Output:
    if output_filename:
        plt.savefig(output_filename, bbox_inches='tight')
    else:
        plt.show()


def add_confidence_intervals(ax=None, pos=None, cis=None, width=None):
    for j, xpos in enumerate(pos):
        xpos += width/2.0
        ax.plot([xpos, xpos], cis[j], linewidth=2, color='black') 

                
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
                    ylim=None,
                    yaxis=None,
                    ylabel="",
                    width=0.5,
                    gap=0.2,
                    axis_width=7,
                    axis_height=3):
    if not nrows:
        nrows = 1
        ncols = len(rnames)           
    fig, axarray = plt.subplots(nrows=nrows, ncols=ncols)
    fig.set_figheight(axis_height*nrows)
    fig.set_figwidth(axis_width*ncols)
    fig.subplots_adjust(bottom=-0.5)
    # Plot dimensions:
    xlim = [0.0, len(cnames)+((len(cnames)-1)*gap)]    
    # If indices doesn't specify an ordering, create an array of
    # axis coordinate pairs for the plot:
    if not indices:
        indices = list(itertools.product(range(nrows), range(ncols)))
    barsetwidth = (width*2)+gap
    pos = np.arange(0, len(cnames)+barsetwidth, barsetwidth)
    # Plot each row as an axis:
    for i, row in enumerate(modmat):
        axindex = indices[i]
        ax = axarray[axindex]
        ax.bar(pos, row, width, label="Model")
        ax.bar(pos+width, expmat[i], width, color="#A60628", label="Human")
        ax.set_title(rnames[i])
        ax.set_ylabel(ylabel, fontsize=14)                 
        ax.set_xlim(xlim)
        ax.set_xticks(pos+(barsetwidth/2.0))
        ax.set_xticklabels(cnames, fontsize=14,  rotation='vertical', color='black')
        if ylim != None:
            ax.set_ylim(ylim)
        if yaxis != None:
            ax.set_yticks(yaxis)
            ax.set_yticklabels(yaxis)
        # Confidence intervals:
        if confidence_intervals:
            add_confidence_intervals(ax=ax, pos=pos+width, cis=confidence_intervals[i], width=width)
        # Correlation annotations:
        if correlation_texts:            
            ax.text(0, ylim[1], correlation_texts[i], fontsize=14, verticalalignment='top', horizontalalignment='left')
    plt.legend(loc='upper left', bbox_to_anchor=(-2.5, 3.7), ncol=2, fontsize=16)
    # Output:
    if output_filename:
        plt.savefig(output_filename, bbox_inches='tight')
    else:
        plt.show()             
                    

def correlation_plot(xmat=None,                     
                     ymat=None,
                     xlabel=None,
                     ylabel=None,
                     xaxis=None,
                     yaxis=None,                     
                     alpha=1.0,
                     correlation_text=None,
                     output_filename=None):
    xlim = axis_buffer(xmat)
    ylim = axis_buffer(ymat)
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_figheight(5)
    fig.set_figwidth(10)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    for i, row in enumerate(xmat):
        ax.plot(row, ymat[i], alpha=alpha, color=COLORS[i], markersize=6, marker='o', linestyle='')    
    ax.set_xlabel(xlabel, fontsize=14)                
    ax.set_ylabel(ylabel, fontsize=14)
    if correlation_text:
        ax.text(xlim[1], ylim[0], correlation_text, fontsize=14, verticalalignment='bottom', horizontalalignment='right')
    if output_filename:
        plt.savefig(output_filename, bbox_inches='tight')
    else:
        plt.show()

               
def axis_buffer(vals, buffer_percentage=0.05):
    buff = np.max(vals)*buffer_percentage
    return [np.min(vals)-buff, np.max(vals)+buff]

