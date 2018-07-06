# deloxfox

[![Travis-CI Build Status](https://travis-ci.org/brews/deloxfox.svg?branch=master)](https://travis-ci.org/brews/deloxfox)

Experimental Bayesian planktic foraminifera calibration, for Python.

**Please note that this package is currently under development. It will eat your pet hamster.**

## Quick example

First, load key packages and an example dataset:

    import numpy as np
    import deloxfox as dfox

    example_file = dfox.get_example_data('VM21-30.csv')
    d = np.genfromtxt(example_file, delimiter=',', names=True, missing_values='NA')

This data (from [Koutavas and Joanides 2012](https://doi.org/10.1029/2012PA002378))
has three columns giving, down-core depth, sediment age (calendar years BP) and δ18O for *G. ruber* (white) (‰; VPDB). The core site is in the Eastern Equatorial Pacific.

We can make a prediction of sea-surface temperature (SST) with `predict_seatemp()`:


    prediction = dfox.predict_seatemp(d['d18O_ruber'], d18osw=0.24, prior_mean=25.1, prior_std=8.0)

`d18osw` is the δ18O for seawater (‰; VSMOW) during the modern record ([LeGrande and Schmidt 2006](https://doi.org/10.1029/2006GL026011)). We'll assume it's constand for simplicity.

To see actual numbers from the prediction, directly parse `prediction.ensemble` or use `prediction.percentile()` to get the 5%, 50% and 95% percentiles. You can also plot your prediction with `dfox.predictplot(prediction)`.

This uses the pooled Bayesian calibration model, which is calibrated on annual SSTs. We can consider foram-specific variability with:

    prediction = dfox.predict_seatemp(d['d18O_ruber'], d18osw=0.24, prior_mean=25.1, prior_std=8.0, 
                                      foram='G_ruber_white')

which uses our hierarchical model calibrated on annual SSTs. We can also estimate foram-specific seasonal effects with:

    prediction = dfox.predict_seatemp(d['d18O_ruber'], d18osw=0.24, prior_mean=25.1, prior_std=8.0, 
                                      foram='G_ruber_white', seasonal_seatemp=True)

This uses our hierarchical model calibrated on seasonal SSTs. Be sure to specify the foraminifera if you use this option.

You can also predict δ18O for planktic calcite using similar options, using the `predict_d18oc()` function.

## Installation

To install **deloxfox** with **pip**, run:


    pip install git+git://github.com/brews/deloxfox.git@master
    
To install **deloxfox** with **conda**, run:


    conda install -c sbmalev deloxfox

**deloxfox** is not compatible with Python 2.

## Support and development

- Please feel free to report bugs and issues or view the source code on GitHub (https://github.com/brews/deloxfox).


## License

**deloxfox** is available under the Open Source GPLv3 (https://www.gnu.org/licenses).
