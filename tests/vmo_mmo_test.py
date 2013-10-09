import unittest

import numpy as np


class TestVMO(unittest.TestCase):
    def test_get_vmo_mmo_array__vmo(self):
        from flightdatautilities.vmo_mmo import VMO

        vmo_mapping = VMO(vmo=234)

        pres_alt = np.ma.arange(10000, 15000, dtype=np.float)
        res = vmo_mapping.get_vmo_mmo_arrays(pres_alt)
        res_vmo = res[0]
        res_mmo = res[1]

        self.assertFalse(np.ma.is_masked(res_vmo))
        self.assertTrue(np.ma.is_masked(res_mmo))

        self.assertTrue(np.ma.all(res_vmo == 234))

    def test_get_vmo_mmo_array__mmo(self):
        from flightdatautilities.vmo_mmo import VMO

        vmo_mapping = VMO(mmo=0.89)

        pres_alt = np.ma.arange(10000, 15000, dtype=np.float)
        res = vmo_mapping.get_vmo_mmo_arrays(pres_alt)
        res_vmo = res[0]
        res_mmo = res[1]

        self.assertFalse(np.ma.is_masked(res_mmo))
        self.assertTrue(np.ma.is_masked(res_vmo))

        self.assertTrue(np.ma.all(res_mmo == 0.89))


class TestVMOL382(unittest.TestCase):
    def test_get_vmo_mmo(self):
        from flightdatautilities.vmo_mmo import VMOL382

        vmo_mapping = VMOL382()

        # First band is below 17500
        res = vmo_mapping.get_vmo_mmo(10000)
        self.assertEqual(res, (250 + (10000 * 4 / 17500), None))

        # Second band is 17500:32500
        res = vmo_mapping.get_vmo_mmo(30000)
        self.assertEqual(res, (254 - ((30000 - 17500) * 52 / 15000), None))

        # Third band is above 32500
        res = vmo_mapping.get_vmo_mmo(33000)
        self.assertEqual(res, (202, None))

    def test_get_vmo_mmo_array(self):
        from flightdatautilities.vmo_mmo import VMOL382

        vmo_mapping = VMOL382()

        pres_alt = np.ma.arange(9000, 35000, dtype=np.float)
        res = vmo_mapping.get_vmo_mmo_arrays(pres_alt)
        res_vmo = res[0]
        res_mmo = res[1]

        self.assertFalse(np.ma.is_masked(res_vmo))
        self.assertTrue(np.ma.is_masked(res_mmo))


class TestVMOGlobalExpress(unittest.TestCase):
    def test_get_vmo_mmo(self):
        from flightdatautilities.vmo_mmo import VMO_SERIES

        vmo_class, params = VMO_SERIES['Global Express']
        vmo_mapping = vmo_class(*params)

        # First band is below 8000
        res = vmo_mapping.get_vmo_mmo(7000)
        self.assertEqual(res, (300, None))

        # Second band is 8000:30267
        res = vmo_mapping.get_vmo_mmo(30000)
        self.assertEqual(res, (340, None))

        # Third band is 30267:35000
        res = vmo_mapping.get_vmo_mmo(34000)
        self.assertEqual(res, (None, 0.89))

        # Fourth band is 35000:41400
        res = vmo_mapping.get_vmo_mmo(40000)
        self.assertEqual(res, (None, 0.88))

        # Fifth band is 41400:47000
        res = vmo_mapping.get_vmo_mmo(45000)
        self.assertEqual(res, (None, 0.858))

        # Sixth band is above 47000
        res = vmo_mapping.get_vmo_mmo(50000)
        self.assertEqual(res, (None, 0.842))

    def test_get_vmo_mmo_array(self):
        from flightdatautilities.vmo_mmo import VMO_SERIES

        vmo_class, params = VMO_SERIES['Global Express']
        vmo_mapping = vmo_class(*params)

        pres_alt = np.ma.arange(7000, 50001, dtype=np.float)
        res_vmo, res_mmo = vmo_mapping.get_vmo_mmo_arrays(pres_alt)
        expected_vmo = np.ma.array(
            [300] * 1001 +
            [340] * (30267 - 8000)
        )
        expected_mmo = np.ma.array(
            [0.89] * (35000 - 30267) +
            [0.88] * (41400 - 35000) +
            [0.858] * (47000 - 41400) +
            [0.842] * (50000 - 47000)
        )

        self.assertTrue(np.ma.is_masked(res_vmo[pres_alt > 30267]))
        np.testing.assert_array_equal(res_vmo[pres_alt <= 30267], expected_vmo)

        self.assertTrue(np.ma.is_masked(res_mmo[pres_alt <= 30267]))
        np.testing.assert_array_equal(res_mmo[pres_alt > 30267], expected_mmo)


class TestVMOCRJ700(unittest.TestCase):
    def test_get_vmo_mmo_array(self):
        from flightdatautilities.vmo_mmo import VMO_FAMILIES

        vmo_class, params = VMO_FAMILIES['CRJ 700']
        vmo_mapping = vmo_class(*params)

        pres_alt = np.ma.arange(7000, 50001, dtype=np.float)
        res_vmo, res_mmo = vmo_mapping.get_vmo_mmo_arrays(pres_alt)
        expected = np.ma.array(
            [330] * 1001 +
            [335] * (25500 - 8000) +
            [0.8] * (28500 - 25500) +
            [315] * (31500 - 28500) +
            [0.85] * (34000 - 31500) +
            [0.84] * (50000 - 34000)
        )

        vmo_ixs = np.ma.where(expected > 1)
        mmo_ixs = np.ma.where(expected < 1)
        self.assertTrue(np.ma.is_masked(res_vmo[mmo_ixs]))
        np.testing.assert_array_equal(res_vmo[vmo_ixs].data,
                                      expected[vmo_ixs].data)

        self.assertTrue(np.ma.is_masked(res_mmo[vmo_ixs]))
        np.testing.assert_array_equal(res_mmo[mmo_ixs].data,
                                      expected[mmo_ixs].data)


class TestVMOLearjet45(unittest.TestCase):
    def test_get_vmo_mmo_array(self):
        from flightdatautilities.vmo_mmo import VMO_SERIES

        vmo_class, params = VMO_SERIES['Learjet 45']
        vmo_mapping = vmo_class(*params)

        pres_alt = np.ma.arange(25000, 27001, dtype=np.float)
        res_vmo, res_mmo = vmo_mapping.get_vmo_mmo_arrays(pres_alt)
        expected = np.ma.array(
            [330] * 1757 +
            [0.81] * (27001 - 26757)
        )

        vmo_ixs = np.ma.where(expected > 1)
        mmo_ixs = np.ma.where(expected < 1)
        self.assertTrue(np.ma.is_masked(res_vmo[mmo_ixs]))
        np.testing.assert_array_equal(res_vmo[vmo_ixs].data,
                                      expected[vmo_ixs].data)

        self.assertTrue(np.ma.is_masked(res_mmo[vmo_ixs]))
        np.testing.assert_array_equal(res_mmo[mmo_ixs].data,
                                      expected[mmo_ixs].data)


##############################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
