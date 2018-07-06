import matplotlib.pylab as plt


def predictplot(prediction, ylabel=None, x=None, xlabel=None, ax=None):
    """Simple plot of prediction with 90% interval.

    Parameters
    ----------
    prediction : Prediction
        MCMC prediciton to be plotted.
    ylabel : str or None, optional
        y-axis label.
    x : array-like, optional
        x-axis values to draw, must equal length of ``prediction``.
    xlabel : str or None, optional
        x-axis label.
    ax : matplotlib.axes.Axes or None, optional
        Optional matplotlib Axes to plot onto.

    Returns
    -------
    ax : matplotlib.axes.Axes
        Axes that was plotted onto.
    """
    if ax is None:
        ax = plt.gca()

    if x is None:
        x = list(range(len(prediction.ensemble)))

    perc = prediction.percentile(q=[5, 50, 95])

    ax.fill_between(x, perc[:, 0], perc[:, 2], alpha=0.25,
                    label='90% uncertainty', color='C0')

    ax.plot(x, perc[:, 1], label='Median', color='C0')
    ax.plot(x, perc[:, 1], marker='.', color='C0')

    if ylabel is not None:
        ax.set_ylabel(ylabel)
    if xlabel is not None:
        ax.set_xlabel(xlabel)

    return ax
