#
# SPDX-FileCopyrightText: Copyright (c) 2021-2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
try:
    import sionna
except ImportError as e:
    import sys
    sys.path.append("../")

from numpy.lib.utils import info

import unittest
import numpy as np
from os import walk # to load generator matrices from files
import re # regular expressions for generator matrix filenames
import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
print('Number of GPUs available :', len(gpus))
if gpus:
    gpu_num = 0 # Number of the GPU to be used
    try:
        tf.config.set_visible_devices(gpus[gpu_num], 'GPU')
        print('Only GPU number', gpu_num, 'used.')
        tf.config.experimental.set_memory_growth(gpus[gpu_num], True)
    except Runtime as e:
        print(e)
from sionna.fec.polar.utils import generate_5g_ranking, generate_rm_code

class TestPolarUtils(unittest.TestCase):
    """Test polar utils.

    Remark: several 5G Polar code related tests can be found in
    test_polar_encoding.py"""

    def test_invalid_inputs(self):
        """Test against invalid values of n and k"""
        param_invalid = [[-1, 32],[10,-3],[1.0, 32],[3, 32.],[33,32], [10, 31],
                         [1025, 2048], [16, 33], [7, 16], [1000, 2048]] # (k,n)
        for p in param_invalid:
            with self.assertRaises(AssertionError):
                generate_5g_ranking(p[0],p[1])

        param_valid = [[1, 512],[10,32],[1000, 1024],[3, 256], [10,64], [0,32],
                       [1024,1024]] # (k,n)
        for p in param_valid:
            generate_5g_ranking(p[0],p[1])

    def test_generate_rm(self):
        """Test that Reed-Muller Code design yields valid constructions.

        We test against the parameters from
        https://en.wikipedia.org/wiki/Reed%E2%80%93Muller_code
        """

        # r, m, n, k, d_min
        param = [[0,0,1,1,1], [1,1,2,2,1], [2,2,4,4,1], [3,3,8,8,1],
                 [4,4,16,16,1], [5,5,32,32,1], [0,1,2,1,2], [1,2,4,3,2],
                 [2,3,8,7,2], [3,4,16,15,2], [4,5,32,31,2], [0,2,4,1,4],
                 [1,3,8,4,4], [2,4,16,11,4], [3,5,32,26,4], [0,3,8,1,8],
                 [1,4,16,5,8], [2,5,32,16,8], [0,4,16,1,16], [1,5,32,6,16],
                 [0,5,32,1,32]]

        for p in param:
            frozen_pos, info_pos, n, k , d_min = generate_rm_code(p[0], p[1])

            # check against correct parameters
            self.assertEqual(n, p[2])
            self.assertEqual(k, p[3])
            self.assertEqual(d_min, p[4])
            self.assertEqual(len(frozen_pos), n-k)
            self.assertEqual(len(info_pos), k)
