import numpy as np
import attr
from bayfox.modelparams import get_draws


@attr.s()
class Prediction:
    ensemble = attr.ib()

    def percentile(self, q=None, interpolation='nearest'):
        """Compute the qth ranked percentile from ensemble members.

        Parameters
        ----------
        q : float ,sequence of floats, or None, optional
            Percentiles (i.e. [0, 100]) to compute. Default is 5%, 50%, 95%.
        interpolation : str, optional
            Passed to numpy.percentile. Default is 'nearest'.

        Returns
        -------
        perc : ndarray
            A 2d (nxm) array of floats where n is the number of predictands in
            the ensemble and m is the number of percentiles ('len(q)').
        """
        if q is None:
            q = [5, 50, 95]
        q = np.array(q, dtype=np.float64, copy=True)

        # Because analog ensembles have 3 dims
        target_axis = list(range(self.ensemble.ndim))[1:]

        perc = np.percentile(self.ensemble, q=q, axis=target_axis,
                             interpolation=interpolation)
        return perc.T


def predict_d18oc(seatemp, d18osw, foram=None, seasonal_seatemp=False,
                  drawsfun=get_draws):
    """Predict δ18O of foram calcite given seawater temperature and seawater δ18O.

    Parameters
    ----------
    seatemp : array_like or scalar
        n-length array or scalar of sea-surface temperature (°C).
    d18osw : array_like or scalar
        n-length array or scalar of δ18O of seawater (‰; VSMOW). If not scalar,
        must be the same length as ``seatemp``.
    foram : str, optional
        Foraminifera group name of ``d18oc`` sample. Can be 'T. sacculifer',
        'N. pachyderma', 'G. bulloides', 'N. incompta' or ``None``.
        If ``None``, pooled calibration model is used.
    seasonal_seatemp : bool, optional
        Indicates whether sea-surface temperature is annual or seasonal
        estimate. If ``True``, ``foram`` must be specified.
    drawsfun : function-like, optional
        For debugging and testing. Object to be called to get MCMC model
        parameter draws. Don't mess with this.

    Returns
    -------
    prediction : Prediction
        Model prediction estimating δ18O of planktic foraminiferal calcite
        (‰; VPDB).
    """
    seatemp = np.atleast_1d(seatemp)
    d18osw = np.atleast_1d(d18osw)
    seasonal_seatemp = bool(seasonal_seatemp)

    alpha, beta, tau = drawsfun(foram=foram, seasonal_seatemp=seasonal_seatemp)

    # Unit adjustment.
    d18osw_adj = d18osw - 0.27

    mu = alpha + seatemp[:, np.newaxis] * beta + d18osw_adj[:, np.newaxis]
    y = np.random.normal(mu, tau)

    return Prediction(ensemble=y)



def predict_seatemp(d18oc, d18osw, prior_mean, prior_std, foram=None,
                    seasonal_seatemp=False, drawsfun=get_draws):
    """Predict sea-surface temperature given δ18O of calcite and seawater δ18O.

    Parameters
    ----------
    d18oc : array_like or scalar
        n-length array or scalar of δ18O of planktic foraminiferal calcite
        (‰; VPDB).
    d18osw : array_like or scalar
        n-length array or scalar of δ18O of seawater (‰; VSMOW). If not scalar, must be the same length as
        ``d18oc``.
    prior_mean : scalar
        Prior mean of sea-surface temperature (°C).
    prior_std : scalar
        Prior standard deviation of sea-surface temperature (°C).
    foram : str, optional
        Foraminifera group name of ``d18oc`` sample. Can be 'T. sacculifer',
        'N. pachyderma', 'G. bulloides', 'N. incompta' or ``None``.
        If ``None``, pooled calibration model is used.
    seasonal_seatemp : bool, optional
        Indicates whether sea-surface temperature is annual or seasonal
        estimate. If ``True``, ``foram`` must be specified.
    drawsfun : function-like, optional
        For debugging and testing. Object to be called to get MCMC model
        parameter draws. Don't mess with this.

    Returns
    -------
    prediction : Prediction
        Model prediction giving estimated sea-surface temperature (°C).
    """
    d18oc = np.atleast_1d(d18oc)
    d18osw = np.atleast_1d(d18osw)
    seasonal_seatemp = bool(seasonal_seatemp)

    alpha, beta, tau = drawsfun(foram=foram, seasonal_seatemp=seasonal_seatemp)

    # Unit adjustment.
    d18osw_adj = d18osw - 0.27

    prior_mean = np.atleast_1d(prior_mean)
    prior_inv_cov = np.atleast_1d(prior_std).astype(float) ** -2

    precision = tau ** -2
    post_inv_cov = prior_inv_cov[..., np.newaxis] + precision * beta ** 2
    post_cov = 1 / post_inv_cov
    mean_first_factor = ((prior_inv_cov * prior_mean)[:, np.newaxis] + precision
                         * beta * ((d18oc - d18osw_adj)[:, np.newaxis] - alpha))
    mean_full = post_cov * mean_first_factor

    y = np.random.normal(loc=mean_full, scale=np.sqrt(post_cov))
    return Prediction(ensemble=y)
