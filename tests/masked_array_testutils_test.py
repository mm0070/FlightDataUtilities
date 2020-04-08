import pytest
import numpy as np

from flightdatautilities.masked_array_testutils import assert_mapped_array_equal
from flightdataaccessor import MappedArray


class TestAssertMappedArrayEqual:
    def test_arrays_equal(self):
        m1 = MappedArray([0, 0, 1], values_mapping={0: 'False', 1: 'True'})
        m2 = MappedArray([0, 0, 1], values_mapping={0: 'False', 1: 'True'})
        assert_mapped_array_equal(m1, m2)

    def test_arrays_different(self):
        m1 = MappedArray([0, 0, 1], values_mapping={0: 'False', 1: 'True'})
        m2 = MappedArray([0, 0, 2], values_mapping={0: 'False', 1: 'True'})
        with pytest.raises(AssertionError) as err:
            assert_mapped_array_equal(m1, m2)
        err_msg = err.value.args[0]
        assert 'Mapped array data are not equivalent' in err_msg

    def test_masks_different(self):
        m1 = MappedArray([0, 0, 1], values_mapping={0: 'False', 1: 'True'})
        m2 = MappedArray([0, np.ma.masked, 1], values_mapping={0: 'False', 1: 'True'})
        with pytest.raises(AssertionError) as err:
            assert_mapped_array_equal(m1, m2)
        err_msg = err.value.args[0]
        assert 'Masks are not equivalent' in err_msg

    def test_values_mapping_different(self):
        m1 = MappedArray([0, 0, 1], values_mapping={0: 'False', 1: 'True'})
        m2 = MappedArray([0, 0, 1], values_mapping={0: 'False', 1: 'Really'})
        with pytest.raises(AssertionError) as err:
            assert_mapped_array_equal(m1, m2)
        err_msg = err.value.args[0]
        assert 'Values mapping are not equivalent' in err_msg