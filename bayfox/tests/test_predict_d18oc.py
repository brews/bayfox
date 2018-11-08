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
    get_draws = DrawDispenser(pooled_annual=FakeTrace({'a': 1, 'b': 2, 'tau': 3}),
                              hier_seasonal=FakeTrace({'a_1': [1, 2], 'b_1': [2, 2], 'tau_1': [3, 3]}))
    return get_draws


@pytest.mark.parametrize('dispenser,kws,expected', [
    (test_dispenser,
     {'seatemp': [15.0], 'd18osw': [0.0], 'foram': None, 'seasonal_seatemp': False},
     np.array([[27.47310819]])),  # pooled_annual
    (test_dispenser,
     {'seatemp': [15.0], 'd18osw': [0.0], 'foram': '1', 'seasonal_seatemp': True},
     np.array([[27.47310819, 34.72203634]])),  # hier_seasonal, multiple parameter draws.
    (test_dispenser,
     {'seatemp': [15.0, 0.0], 'd18osw': [0.0], 'foram': '1', 'seasonal_seatemp': True},
     np.array([[27.47310819, 34.722036], [1.578935, -2.788884]])),  # hier_seasonal, multiple seatemps
    (test_dispenser,
     {'seatemp': [15.0, 0.0], 'd18osw': [0.0, 1.0], 'foram': '1', 'seasonal_seatemp': True},
     np.array([[27.47310819, 34.722036], [2.578935, -1.788884]])),  # hier_seasonal, multiple d18osw & seatemps
])
def test_predict_d18oc(dispenser, kws, expected):
    """Test predict_d18oc() under basic inputs.
    """
    np.random.seed(123)
    get_draws = dispenser()
    victim = bfox.predict_d18oc(drawsfun=get_draws, **kws)
    np.testing.assert_allclose(victim.ensemble, expected, rtol=0, atol=1e-4)
