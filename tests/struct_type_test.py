try:
    import unittest2 as unittest
except ImportError:
    import unittest

from flightdatautilities.struct_type import Struct


class TestStruct(unittest.TestCase):
    '''
    '''

    def test_create_empty(self):
        '''
        '''
        s = Struct()
        self.assertIsInstance(s, Struct)
        self.assertEqual(s, Struct())
        s = Struct({})
        self.assertIsInstance(s, Struct)
        self.assertEqual(s, Struct())

    def test_create_from_dict(self):
        '''
        '''
        aircraft = Struct({'model': {'dist_gear_to_tail': 200}})
        self.assertEqual(aircraft.model.dist_gear_to_tail, 200)

    def test_create_from_struct(self):
        '''
        '''
        aircraft = Struct(Struct(model=Struct(dist_gear_to_tail=200)))
        self.assertEqual(aircraft.model.dist_gear_to_tail, 200)

    def test_create_from_generator(self):
        '''
        '''
        s = Struct((chr(96 + v), v) for v in [1, 2, 3])
        self.assertEqual(len(s), 3)
        self.assertEqual(s, Struct({'a': 1, 'b': 2, 'c': 3}))

    def test_setattr(self):
        '''
        '''
        s = Struct()
        self.assertEqual(len(s), 0)
        s.key = 'value'
        self.assertEqual(s.key, 'value')
        self.assertEqual(len(s), 1)

    def test_getattr(self):
        '''
        '''
        s = Struct({'key': 'value'})
        self.assertEqual(len(s), 1)
        self.assertEqual(s.key, 'value')
        self.assertEqual(len(s), 1)

    def test_delattr(self):
        '''
        '''
        s = Struct({'key': 'value'})
        self.assertEqual(len(s), 1)
        del s.key
        self.assertEqual(len(s), 0)

    # XXX: hasattr() is broken due to Struct.__getattr__()
    @unittest.expectedFailure
    def test_hasattr(self):
        '''
        '''
        s = Struct({'key': 'value'})
        self.assertEqual(len(s), 1)
        self.assertTrue(hasattr(s, 'key'))
        self.assertEqual(len(s), 1)
        self.assertFalse(hasattr(s, 'invalid'))
        self.assertEqual(len(s), 1)

    def test_setitem(self):
        '''
        '''
        s = Struct()
        self.assertEqual(len(s), 0)
        s['key'] = 'value'
        self.assertEqual(s['key'], 'value')
        self.assertEqual(len(s), 1)

    def test_getitem(self):
        '''
        '''
        s = Struct({'key': 'value'})
        self.assertEqual(len(s), 1)
        self.assertEqual(s['key'], 'value')
        self.assertEqual(len(s), 1)

    def test_delitem(self):
        '''
        '''
        s = Struct({'key': 'value'})
        self.assertEqual(len(s), 1)
        del s['key']
        self.assertEqual(len(s), 0)

    def test_hasitem(self):
        '''
        '''
        s = Struct({'key': 'value'})
        self.assertEqual(len(s), 1)
        self.assertTrue('key' in s)
        self.assertEqual(len(s), 1)
        self.assertFalse('invalid' in s)
        self.assertEqual(len(s), 1)

    def test_create_attrs_on_the_fly(self):
        '''
        '''
        # Create initial struct from a dictionary:
        aircraft = Struct({'model': {'dist_gear_to_tail': 200}})
        # Add attribute at the top level:
        aircraft.tail_number = 'G-ABCD'
        self.assertEqual(aircraft.tail_number, 'G-ABCD')
        # Add attribute at level created from dictionary earlier:
        aircraft.model.name = '737-800'
        self.assertEqual(aircraft.model.name, '737-800')
        # Add attribute on a new attribute two levels deep:
        aircraft.frame.type = '737-3C'
        self.assertEqual(aircraft.frame.type, '737-3C')
        self.assertTrue(isinstance(aircraft.frame, Struct))
        # Add attribute on non-existing attribute with lots of depth:
        aircraft.a.b.c.d.e = 'alphabet'
        # Check that a previously unreferenced attribute is created on the fly:
        self.assertEqual(aircraft.x.y.z, Struct())
        # Ensure that a non-struct attribute cannot have an unknown attribute:
        self.assertRaises(AttributeError, getattr, aircraft.a.b.c.d.e, 'f')

    def test_magic_attribute_error(self):
        '''
        '''
        s = Struct()
        self.assertRaises(AttributeError, getattr, s, '__magic__')

    def test_no_shared_references(self):
        '''
        '''
        s0 = Struct(x=Struct(x=0, y=Struct()))
        s1 = Struct(s0)
        # Check (nested) structures are not the same:
        self.assertIsNot(s0, s1)
        self.assertIsNot(s0.x, s1.x)
        # Change a value in one structure - shouldn't change in the other:
        s0.x.x = 1
        self.assertEqual(s1.x.x, 0)

    def test_to_dict(self):
        '''
        '''
        aircraft = Struct()
        aircraft.tail_number = 'G-ABCD'
        aircraft.frame.type = '737-3C'
        aircraft.model.dist_gear_to_tail = 200
        self.assertEqual(aircraft.to_dict(), {
            'tail_number': 'G-ABCD',
            'frame': {'type': '737-3C'},
            'model': {'dist_gear_to_tail': 200},
        })
