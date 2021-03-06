# -*- coding: utf-8 -*-
""" Phase Locking Value

One of the pioneer methods called Phase Locking Value (*PLV*) is discussed in
[Lachaux1998]_; it utilizes the Hilbert representation (consult
:py:mod:`dyfunconn.analytic_signal` for more details) an EEG time
series (of :math:`N_{sensors}`) and quantifies their interaction based on their
instantaneous phase in a specific band frequency.

So, for a pair of Instantaneous Phases of two time series of equal length,
:math:`\phi_{j1}(t)` and :math:`\phi_{j2}(t)`, the Phase Locking Value for each
sample in time (:math:`t`) is computed as:

.. math::
    e^{i (\phi_{j1}(t)  - \phi_{j2}(t))}

A value of zero means that no coupling (or negligible) observed between two
phases, while a value of one denotes a perfect synchronization.

|

-----

.. [Lachaux1998] Lachaux, J., Rodriguez, E., Martinerie, J., Varela, F., & others,. (1999). Measuring phase synchrony in brain signals. Human Brain Mapping, 8(4), 194-208.
"""
# Author: Avraam Marimpis <avraam.marimpis@gmail.com>

from .estimator import Estimator
from ..analytic_signal import analytic_signal

import numpy as np


def plv(data, fb, fs, pairs=None):
    """ Phase Locking Value

    Compute the PLV for the given :attr:`data`, between the :attr:`pairs` (if given)
    of channels.


    Parameters
    ----------
    data : array-like, shape(n_channels, n_samples)
        Multichannel recording data.

    fb : list of length 2
        The lower and upper frequency.

    fs : float
        Sampling frequency.

    pairs : array-like or `None`
        - If an `array-like` is given, notice that each element is a tuple of length two.
        - If `None` is passed, complete connectivity will be assumed.


    Returns
    -------
    ts : complex array-like, shape(n_channels, n_channels, n_samples)
        Estimated PLV time series.

    avg : array-like, shape(n_channels, n_channels)
        Average PLV.


    See also
    --------
    dyfunconn.fc.PLV: Phase Locking Value (Class Estimator)
    dyfunconn.fc.iplv: Imaginary part of PLV
    dyfunconn.fc.pli: Phase Lag Index
    """
    estimator = PLV(fb, fs, pairs)
    pp_data = estimator.preprocess(data)

    return estimator.estimate(pp_data)


class PLV(Estimator):
    """ Phase Locking Value (PLV)


    See also
    --------
    dyfunconn.fc.plv: Phase Locking Value
    dyfunconn.tvfcg: Time-Varying Functional Connectivity Graphs
    """

    def __init__(self, fb, fs, pairs=None):
        Estimator.__init__(self, fs, pairs)

        self.fb = fb
        self.fs = fs
        self.data_type = np.complex

    def preprocess(self, data):
        _, _, u_phases = analytic_signal(data, self.fb, self.fs)

        return u_phases

    def estimate_pair(self, signal1, signal2):
        """

        Returns
        -------
        ts : array-like, shape(1, n_samples)
            Estimated PLV time series (real valued).

        avg : float
            Average PLV.


        Notes
        -----
        Called from :mod:`dyfunconn.tvfcgs.tvfcg`.
        """
        n_samples = len(signal1)

        ts_plv = np.exp(1j * (signal1 - signal2))
        avg_plv = np.abs(np.sum((ts_plv))) / float(n_samples)

        return ts_plv, avg_plv

    def mean(self, ts):
        l = float(np.shape(ts)[0])
        return np.abs(np.sum(ts)) / l

    def estimate(self, data, data_against=None):
        """


        Returns
        -------
        ts : complex array-like, shape(n_channels, n_channels, n_samples)
            Estimated PLV time series (complex valued).

        avg : array-like, shape(n_channels, n_channels)
            Average PLV.


        Notes
        -----
        Called from :mod:`dyfunconn.tvfcgs.tvfcg`.
        """
        n_channels, n_samples = np.shape(data)

        ts = np.zeros((n_channels, n_channels, n_samples), dtype=np.complex)
        avg = np.zeros((n_channels, n_channels))

        if self.pairs is None:
            self.pairs = [(r1, r2) for r1 in range(n_channels)
                          for r2 in range(r1, n_channels)
                          if r1 != r2]

        for pair in self.pairs:
            u_phases1, u_phases2 = data[pair, ]
            ts_plv = np.exp(1j * (u_phases1 - u_phases2))
            avg_plv = np.abs(np.sum((ts_plv))) / float(n_samples)

            ts[pair] = ts_plv
            avg[pair] = avg_plv

        return ts, avg
