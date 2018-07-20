import pytest
import numpy as np
from bayfox.modelparams.core import DrawDispenser, McmcTrace, get_draws, ForamError


class FakeTrace(McmcTrace):
    """Mimic for testing"""
    def __init__(self, array):
        self._d = dict(array)

    def grab(self, param, foram=None):
        if foram is None:
            return np.atleast_1d([self._d[param]])
        else:
            return np.atleast_1d(self._d['{}_{}'.format(param, foram)])


@pytest.fixture
def named_empty_dispenser():
    get_draws = DrawDispenser(pooled_annual=FakeTrace({'a': 1, 'b': 2, 'tau': 3}),
                              hier_annual=FakeTrace({'a_1': 4, 'b_1': 5, 'tau_1': 6}),
                              hier_seasonal=FakeTrace({'a_1': 7, 'b_1': 8, 'tau_1': 9}))
    return get_draws


@pytest.mark.parametrize('dispenser,diskws,expected', [
    (named_empty_dispenser, {'foram': None, 'seasonal_seatemp': False}, (np.array([1]), np.array([2]), np.array([3]))),  # pooled_annual
    (named_empty_dispenser, {'foram': '1', 'seasonal_seatemp': False}, (np.array([4]), np.array([5]), np.array([6]))),  # hier_annual
    (named_empty_dispenser, {'foram': '1', 'seasonal_seatemp': True}, (np.array([7]), np.array([8]), np.array([9]))),  # hier_seasonal

])
def test_dispenser_dispatch(dispenser, diskws, expected):
    """Test DrawDispenser objs correctly pull corrected from McmcTraces when called.
    """
    out = dispenser()(**diskws)
    assert out == expected


def test_bad_foram():
    """Throw error if use foram name not in draws"""
    with pytest.raises(ForamError):
        get_draws(foram='foobar')
