import numpy as np
from bayfox.predict import Prediction


def test_prediction_precentile():
    goal = np.array([[0, 2, 4], [5, 7, 9]])
    ens = np.reshape(np.arange(10), (2, 5))
    pred = Prediction(ensemble=ens)
    victim = pred.percentile()
    np.testing.assert_equal(victim, goal)
