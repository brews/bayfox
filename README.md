# bayfox

[![Travis-CI Build Status](https://travis-ci.org/brews/bayfox.svg?branch=master)](https://travis-ci.org/brews/bayfox)

Experimental Bayesian planktic foraminifera calibration, for Python.

**Please note that this package is currently under development. It will eat your pet hamster.**

## Quick example

First, load key packages and an example dataset:

    import numpy as np
    import bayfox as bfox

    example_file = bfox.get_example_data('VM21-30.csv')
    d = np.genfromtxt(example_file, delimiter=',', names=True, missing_values='NA')

This data (from [Koutavas and Joanides 2012](https://doi.org/10.1029/2012PA002378))
has three columns giving, down-core depth, sediment age (calendar years BP) and δ18O for *G. ruber* (white) (‰; VPDB). 
The core site is in the Eastern Equatorial Pacific.

We can make a prediction of sea-surface temperature (SST) with `predict_seatemp()`:

    prediction = bfox.predict_seatemp(d['d18O_ruber'], d18osw=0.239, prior_mean=24.9, prior_std=7.81)

The values we're using for priors are roughly based on the range of SSTs we've seen for *G. ruber* (white) sediment 
core in the modern period, though prior standard deviation is twice`d18osw` is twice the spread we see in the modern 
record. δ18O for seawater (‰; VSMOW) during the modern record 
([LeGrande and Schmidt 2006](https://doi.org/10.1029/2006GL026011)). We'll assume it's constant -- for simplicity. 
We're also not correcting these proxies for changes in global ice volume, so these numbers will be off. Ideally we'd make 
this correction to δ18Oc series before the prediction. See the 
[`erebusfall` package](https://github.com/brews/erebusfall) for simple ice-volume correction in Python.

To see actual numbers from the prediction, directly parse `prediction.ensemble` or use `prediction.percentile()` to get 
the 5%, 50% and 95% percentiles. You can also plot your prediction with `dfox.predictplot(prediction)`.

This uses the pooled Bayesian calibration model, which is calibrated on annual SSTs. We can consider foram-specific 
variability with:

    prediction = bfox.predict_seatemp(d['d18O_ruber'], d18osw=0.239, prior_mean=24.9, prior_std=7.81, 
                                      foram='G_ruber_white')

which uses our hierarchical model calibrated on annual SSTs. We can also estimate foram-specific seasonal effects with:

    prediction = bfox.predict_seatemp(d['d18O_ruber'], d18osw=0.239, prior_mean=24.9, prior_std=7.81, 
                                      foram='G_ruber_white', seasonal_seatemp=True)

This uses our hierarchical model calibrated on seasonal SSTs. Be sure to specify the foraminifera if you use this option.

You can also predict δ18O for planktic calcite using similar options, using the `predict_d18oc()` function.

## Installation

To install **bayfox** with *pip*, run:

    pip install bayfox


To install **bayfox** with *conda*, run:

    conda install -c sbmalev bayfox

**bayfox** is not compatible with Python 2.

## Support and development

- Please feel free to report bugs and issues or view the source code on GitHub (https://github.com/brews/bayfox).


## License

**bayfox** is available under the Open Source GPLv3 (https://www.gnu.org/licenses).
