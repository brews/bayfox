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
        Foraminifera group name of ``d18oc`` sample. Can be 'G. ruber pink',
        'G. ruber white', 'G. sacculifer', 'N. pachyderma sinistral',
        'G. bulloides', 'N. incompta' or ``None``. If ``None``, pooled
        calibration model is used.
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
    seatemp = np.asanyarray(seatemp)
    d18osw = np.asanyarray(d18osw)
    seasonal_seatemp = bool(seasonal_seatemp)

    alpha, beta, tau = drawsfun(foram=foram, seasonal_seatemp=seasonal_seatemp)

    n_draws = len(tau)

    # Unit adjustment.
    d18osw_adj = d18osw - 0.27

    # TODO(brews): Might be able to vectorize loop below.
    y = np.empty((len(seatemp), n_draws))
    y[:] = np.nan
    for i in range(n_draws):
        mu = alpha[i] + seatemp * beta[i] + d18osw_adj
        y[:, i] = np.random.normal(mu, tau[i])

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
        Foraminifera group name of ``d18oc`` sample. Can be 'G. ruber pink',
        'G. ruber white', 'G. sacculifer', 'N. pachyderma sinistral',
        'G. bulloides', 'N. incompta' or ``None``. If ``None``, pooled
        calibration model is used.
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
    d18oc = np.asanyarray(d18oc)
    d18osw = np.asanyarray(d18osw)
    seasonal_seatemp = bool(seasonal_seatemp)

    alpha, beta, tau = drawsfun(foram=foram, seasonal_seatemp=seasonal_seatemp)

    # Unit adjustment.
    d18osw_adj = d18osw - 0.27

    nd = len(d18oc)
    n_draws = len(tau)

    pmu = np.ones(nd) * prior_mean
    pinv_cov = np.eye(nd) * prior_std ** -2

    # TODO(brews): Might be able to vectorize loop below.
    y = np.empty((nd, n_draws))
    y[:] = np.nan
    for i in range(n_draws):
        y[:, i] = _target_timeseries_pred(d18osw_now=d18osw_adj, alpha_now=alpha[i],
                                          beta_now=beta[i], tau_now=tau[i],
                                          proxy_ts=d18oc, prior_mu=pmu,
                                          prior_inv_cov=pinv_cov)

    return Prediction(ensemble=y)


def _target_timeseries_pred(d18osw_now, alpha_now, beta_now, tau_now, proxy_ts,
                            prior_mu, prior_inv_cov):
    """

    Parameters
    ----------
    d18osw_now : scalar
    alpha_now : scalar
    beta_now : scalar
    tau_now : float
        Current value of the residual standard deviation.
    proxy_ts : ndarray
        Time series of the proxy. Assume no temporal structure for now, as
        timing is not equal.
    prior_mu : ndarray
        Prior means for each element of the time series.
    prior_inv_cov: ndarray
        Inverse of the prior covariance matrix for the time series.

    Returns
    -------
    Sample of target time series vector conditional on the rest.
    """
    # TODO(brews): Above docstring is based on original MATLAB. Needs cleanup.
    n_ts = len(proxy_ts)

    # Inverse posterior covariance matrix
    precision = tau_now ** -2
    post_inv_cov = prior_inv_cov + precision * beta_now ** 2 * np.eye(n_ts)

    post_cov = np.linalg.inv(post_inv_cov)
    # Get first factor for the mean
    mean_first_factor = prior_inv_cov @ prior_mu + precision * beta_now * (proxy_ts - alpha_now - d18osw_now)
    mean_full = mean_first_factor @ post_cov

    timeseries_pred = np.random.normal(loc=mean_full,
                                       scale=np.sqrt(post_cov.diagonal()))

    return timeseries_pred
