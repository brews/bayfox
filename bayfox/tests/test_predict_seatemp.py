import pytest
import numpy as np
import bayfox as bfox
from bayfox.modelparams.core import DrawDispenser, McmcTrace


class FakeTrace(McmcTrace):
    """Mimic for testing"""
    def __init__(self, array):
        self._d = dict(array)

    def grab(self, param, foram=None):
        if foram is None:
            return np.atleast_1d(self._d[param])
        else:
            return np.atleast_1d(self._d['{}_{}'.format(param, foram)])


@pytest.fixture
def test_dispenser():
    get_draws = DrawDispenser(pooled_annual=FakeTrace({'a': 1.0, 'b': 2.0, 'tau': 3.0}),
                              hier_seasonal=FakeTrace({'a_1': [1.0, 2.0], 'b_1': [2.0, 2.0], 'tau_1': [3.0, 3.0]}))
    return get_draws


@pytest.mark.parametrize('dispenser,kws,expected', [
    (test_dispenser,
     {'d18oc': [-3.75], 'd18osw': [0.0], 'foram': None, 'seasonal_seatemp': False},
     np.array([[-3.767453]])),  # pooled_annual
    (test_dispenser,
     {'d18oc': [-3.75], 'd18osw': [0.0], 'foram': '1', 'seasonal_seatemp': True},
     np.array([[-3.767453, -1.148942]])),  # hier_seasonal, multiple parameter draws.
    (test_dispenser,
     {'d18oc': [-3.75, 0.0], 'd18osw': [0.0], 'foram': '1', 'seasonal_seatemp': True},
     np.array([[-3.767453, -1.148942], [0.144224, -3.029373]])),  # hier_seasonal, multiple seatemps
    (test_dispenser,
     {'d18oc': [-3.75, 0.0], 'd18osw': [0.0, 1.0], 'foram': '1', 'seasonal_seatemp': True},
     np.array([[-3.767453, -1.148942], [-0.35298, -3.526576]])),  # hier_seasonal, multiple d18osw & seatemps
])
def test_predict_seatemp(dispenser, kws, expected):
    """Test predict_seatemp() under basic inputs.
    """
    np.random.seed(123)
    get_draws = dispenser()
    victim = bfox.predict_seatemp(drawsfun=get_draws, prior_mean=15, prior_std=20, **kws)
    np.testing.assert_allclose(victim.ensemble, expected, rtol=0, atol=1e-4)
