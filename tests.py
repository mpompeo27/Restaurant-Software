import unittest
import Restaurant_Business_Software as rbs
from datetime import datetime, timezone, timedelta

# Create unit testing class
class RestaurantFunctionTests(unittest.TestCase):
  # set up test fixture by wiping slate clean, resetting all dictionaries, counters, and global variables
  def setUp(self):
    rbs.tables.clear()
    rbs.tables.update({
       1: {'capacity': 2, 'status': 'available'},
       2: {'capacity': 2, 'status': 'available'},
       3: {'capacity': 4, 'status': 'available'},
       4: {'capacity': 4, 'status': 'available'},
       5: {'capacity': 4, 'status': 'available'},
       6: {'capacity': 6, 'status': 'available'},
       7: {'capacity': 8, 'status': 'available'}
    })
    rbs.reservations.clear()
    rbs.reservations.update({1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
    rbs.reservation_lookup.clear()
    rbs.Order.order_count = 0
    rbs.Reservation.reservation_count = 0
    rbs.max_capacity = 0
    for t in rbs.tables:
      rbs.max_capacity += rbs.tables[t]['capacity']
    rbs.menu = {
    "foods": {
      "Pancakes": 4.0,
      "Scrambled Eggs": 4.5,
      "Waffles": 4.5,
      "Tuna Sandwich": 3.5,
      "Turkey Club Sandwich": 5.0,
      "Ham Sandwich": 3.0,
      "Salad": 2.5,
      "Soup": 2.0,
      "Spaghetti": 6.0,
      "Pork Chops": 8.0,
      "Chicken Fingers": 5.0,
      "Steak": 8.5,
      "Bacon": 1.0,
      "Sausage": 1.0,
      "French Fries": 1.75,
      "Mashed Potatoes": 2.0,
      "Ice Cream": 2.5
    },
    "drinks": {
      "Orange Juice": 1.5,
      "Apple Juice": 1.5,
      "Coca Cola": 2.0,
      "Sprite": 2.0,
      "Grape Soda": 1.75,
      "White Wine": 5.0,
      "Red Wine": 5.0,
      "Beer": 3.5,
      "Sparkling Water": 1.75
    }}
  # test method to check the results of assigning a single table
  def test_assign_single_table(self):
    # Test a single table assignment
    rbs.assign_table(1, name='John', party_size=2)
    self.assertEqual(rbs.tables[1]['name'], 'John', 'Name \'John\' not assigned to table 2.')
    self.assertEqual(rbs.tables[1]['status'], 'occupied', 'Table 1 status not set to \'occupied\'.')
    self.assertEqual(rbs.tables[1]['num_diners'], 2, 'Table 1 num_diners not set to 2.')
    self.assertEqual(rbs.tables[1]['vip_status'], False, 'Table 1 vip_status not set to False.')
    self.assertEqual(rbs.tables[1]['reservation'], False, 'Table 1 reservation status not set to False.')
    self.assertEqual(rbs.tables[1]['seating_time'], datetime.now(timezone(timedelta(hours=-6))).strftime('%H:%M %m-%d-%Y'), 'Table 1 seating time does not equal current time.')
    self.assertEqual(rbs.tables[1]['order']['ord_number'], '00001', 'Table 1 order number status not set 00001.')
    self.assertIsNone(rbs.tables[1]['total'], 'Table 1 total is not None.')
    self.assertIn('linked_tables', rbs.tables[1], 'Key \'linked_tables\' not created on table number 1.')
    self.assertEqual(rbs.tables[1]['linked_tables'], [], 'Table 1 linked_tables not set to empty list.')
    # Confirm reservations table was not altered.
    self.assertEqual(rbs.reservations[1], [], 'Table 1 reservations modified from an empty list.')
    # Check that a different table number was not modified
    self.assertEqual(rbs.tables[2]['status'], 'available', 'Other table number 2 status set to \'occupied\'.')
    self.assertNotIn('name', rbs.tables[5], 'Other table number 5 has a \'name\' key.')
  
  def test_assign_combined_tables(self):
    rbs.assign_table(7, 3, 4, name='John', party_size=15)
    self.assertEqual(rbs.tables[7]['name'], 'John', 'Name \'John\' not assigned to primary table number 7.')
    self.assertNotIn('name', rbs.tables[3], 'Non-primary table number 3 has a \'name\' key.')
    self.assertNotIn('name', rbs.tables[4], 'Non-primary table number 4 has a \'name\' key.')
    self.assertEqual(rbs.tables[7]['status'], 'occupied', 'Table 7 status not set to \'occupied\'.')
    self.assertEqual(rbs.tables[3]['status'], 'occupied', 'Table 3 status not set to \'occupied\'.')
    self.assertEqual(rbs.tables[4]['status'], 'occupied', 'Table 4 status not set to \'occupied\'.')
    self.assertEqual(rbs.tables[7]['num_diners'], 15, 'Key \'num_diners\' on primary table number 7 not equal to party_size of 15.')
    self.assertNotIn('num_diners', rbs.tables[3], 'Non-primary table number 3 has a \'num_diners\' key.')
    self.assertNotIn('num_diners', rbs.tables[4], 'Non-primary table number 4 has a \'num_diners\' key.')
    self.assertEqual(rbs.tables[7]['vip_status'], False, 'Primary table 7 vip_status not set to False.')
    self.assertNotIn('vip_status', rbs.tables[3], 'Non-primary table number 3 has a \'vip_status\' key.')
    self.assertNotIn('vip_status', rbs.tables[4], 'Non-primary table number 4 has a \'vip_status\' key.')
    self.assertEqual(rbs.tables[7]['reservation'], False, 'Primary table 7 reservation status not set to False.')
    self.assertNotIn('reservation', rbs.tables[3], 'Non-primary table number 3 has a \'reservation\' key.')
    self.assertNotIn('reservation', rbs.tables[4], 'Non-primary table number 4 has a \'reservation\' key.')
    self.assertEqual(rbs.tables[7]['seating_time'], datetime.now(timezone(timedelta(hours=-6))).strftime('%H:%M %m-%d-%Y'), 'Primary table 7 seating time does not equal current time.')
    self.assertNotIn('seating_time', rbs.tables[3], 'Non-primary table number 3 has a \'seating_time\' key.')
    self.assertNotIn('seating_time', rbs.tables[4], 'Non-primary table number 4 has a \'seating_time\' key.')
    self.assertEqual(rbs.tables[7]['order']['ord_number'], '00001', 'Primary table 7 order number status not set 00001.')
    self.assertNotIn('order', rbs.tables[3], 'Non-primary table number 3 has an \'order\' key.')
    self.assertNotIn('order', rbs.tables[4], 'Non-primary table number 4 has an \'order\' key.')
    self.assertIsNone(rbs.tables[7]['total'], 'Primary table 7 total is not None.')
    self.assertNotIn('total', rbs.tables[3], 'Non-primary table number 3 has a \'total\' key.')
    self.assertNotIn('total', rbs.tables[4], 'Non-primary table number 4 has a \'total\' key.')
    self.assertIn('linked_tables', rbs.tables[7], 'Key \'linked_tables\' not created on primary table number 7.')
    self.assertIn('linked_tables', rbs.tables[3], 'Key \'linked_tables\' not created on additional table number 3.')
    self.assertIn('linked_tables', rbs.tables[4], 'Key \'linked_tables\' not created on additional table number 4.')
    self.assertEqual(rbs.tables[7]['linked_tables'], [3, 4], 'Table 7 linked_tables not set to list [3, 4].')
    self.assertEqual(rbs.tables[3]['linked_tables'], [7, 4], 'Table 7 linked_tables not set to list [7, 4].')
    self.assertEqual(rbs.tables[4]['linked_tables'], [7, 3], 'Table 7 linked_tables not set to list [7, 3].')
    # Confirm reservations table was not altered.
    self.assertEqual(rbs.reservations[7], [], 'Primary table 7 reservations modified from an empty list.')
    # Check that a different table number was not modified
    self.assertEqual(rbs.tables[2]['status'], 'available', 'Other table number 2 status set to \'occupied\'.')
    self.assertNotIn('name', rbs.tables[5], 'Other table number 5 has a \'name\' key.')

  def test_assign_table_arguments(self):
    # Test missing table numbers
    with self.assertRaises(ValueError, msg='Missing *table_numbers did not raise ValueError.'):
      rbs.assign_table(name='John', party_size=3, vip_status=True, reserve_status=False)
    # Test table number already occupied
    rbs.Order.order_count = 1
    rbs.tables[2] = {'capacity': 2, 'status': 'occupied', 'name': 'Customer', 'vip_status': False, 'reservation': False, 'seating_time': datetime.now(timezone(timedelta(hours=-6))).strftime('%H:%M %m-%d-%Y'), 'num_diners': 2, 'order': {'ord_number': '00001'}, 'total': None}
    # Single/primary table assignment conflict
    with self.assertRaises(ValueError, msg='Occupied single/primary table number did not raise ValueError.'):
      rbs.assign_table(2, name='John', party_size=2, vip_status=True, reserve_status=False)
    # Linked table assignment conflict
    with self.assertRaises(ValueError, msg='Occupied linked table number did not raise ValueError.'):
      rbs.assign_table(6, 2, name='John', party_size=8, vip_status=True, reserve_status=False)  
    # Test table number has upcoming reservation
    rbs.Reservation.reservation_count = 1
    rbs.reservations[5] = ['rsv-00001']
    rbs.reservation_lookup['rsv-00001'] = {'name': 'Mark', 'time': '19:00 04-30-2026', 'num_diners': 4, 'vip_status': False, 'tables': [5]}
    # Single/primary table assignment conflict
    with self.assertRaises(ValueError, msg='Seating time conflict with upcoming reservation on single/primary table did not raise ValueError.'):
      rbs.assign_table(5, name='John', party_size=3, vip_status=True, reserve_status=False, time='18:30 04-30-2026')
    # Linked table assignment conflict
    with self.assertRaises(ValueError, msg='Seating time conflict with upcoming reservation on linked table did not raise ValueError.'):
      rbs.assign_table(7, 1, 5, name='John', party_size=14, vip_status=True, reserve_status=False, time='18:30 04-30-2026')
    # Test party_size exceeds capacity
    # Single table assignment - table 5 with capacity=4 assigned to party of 5
    with self.assertRaises(ValueError, msg='Party size greater than single table capacity did not raise ValueError.'):
      rbs.assign_table(5, name='John', party_size=5, vip_status=True, reserve_status=False)
    # Combined table assignment - tables 7 and 3 with combined capacity 12 assigned to a party of 13
    with self.assertRaises(ValueError, msg='Party size greater than combined table capacity did not raise ValueError.'):
      rbs.assign_table(7, 3, name='John', party_size=13, vip_status=True, reserve_status=False)

  # Test the validation checks inside validate_params and check_param
  def test_parameter_checks(self):
    # Test invalid single table_number
    # Test for a non-integer value
    with self.assertRaises(TypeError, msg='Non-integer table_number did not raise TypeError.'):
      rbs.validate_params(table_number='five')
    # Test table_number does not exist in tables dict
    with self.assertRaises(ValueError, msg='Non-existent table_number did not raise ValueError.'):
      rbs.validate_params(table_number=9)
    # Test invalid multiple table_numbers.
    # Test for no values
    with self.assertRaises(ValueError, msg='Empty table_numbers tuple with no values did not raise ValueError.'):
      rbs.validate_params(table_numbers=())
    # Test for a non-integer value
    with self.assertRaises(TypeError, msg='Non-integer value in table_numbers tuple did not raise TypeError.'):
      rbs.validate_params(table_numbers=(2, 'five'))
    # Test for table number that does not exist in tables dict
    with self.assertRaises(ValueError, msg='Non-existent table number in table_numbers tuple did not raise ValueError.'):
      rbs.validate_params(table_numbers=(9, 4))
    # Test non-string value for name
    with self.assertRaises(TypeError, msg='Non-string name did not raise TypeError.'):
      rbs.validate_params(name=('John', 'Schwartz'))
    # Test non-boolean vip_status
    with self.assertRaises(TypeError, msg='Non-boolean vip_status did not raise TypeError.'):
      rbs.validate_params(vip_status='True')
    # Test non-boolean reserve_status
    with self.assertRaises(TypeError, msg='Non-boolean reserve_status did not raise TypeError.'):
      rbs.validate_params(reserve_status='False')
    # Test invalid time values
    # Test non-string time
    with self.assertRaises(TypeError, msg='Time not entered as a string did not raise TypeError.'):
      rbs.validate_params(time=10)
    # Test incorrectly formatted time string - required format is HH:MM mm-dd-yyyy
    with self.assertRaises(ValueError, msg='Incorrectly formatted time string did not raise TypeError.'):
      rbs.validate_params(time='04-29-2026 15:00')
    # Test invalid party_size values
    # Test non-integer party_size
    with self.assertRaises(TypeError, msg='Non-integer party_size did not raise TypeError.'):
      rbs.validate_params(party_size='four')
     # Test boolean party_size
    with self.assertRaises(TypeError, msg='Boolean party_size did not raise TypeError.'):
      rbs.validate_params(party_size=True)
    # Test non-positive integer party_size
    with self.assertRaises(ValueError, msg='Non-positive integer party_size did not raise ValueError.'):
      rbs.validate_params(party_size=-5)
    # Test party_size greater than max_capacity
    with self.assertRaises(ValueError, msg='party_size greater than max_capacity did not raise ValueError.'):
      rbs.validate_params(party_size=1000000)
    # Test single tip value
    # Test non-numeric tip
    with self.assertRaises(TypeError, msg='Non-numeric tip amount did not raise TypeError.'):
      rbs.validate_params(tip='four')
    # Test boolean tip
    with self.assertRaises(TypeError, msg='Boolean tip value did not raise TypeError.'):
      rbs.validate_params(tip=True)
    # Test negative tip amount
    with self.assertRaises(ValueError, msg='Negative tip amount did not raise ValueError.'):
      rbs.validate_params(tip=-5.73)
    # Test multiple tips values
    # Test for no values
    with self.assertRaises(ValueError, msg='Empty tips tuple with no values did not raise ValueError.'):
      rbs.validate_params(tips=())
    # Test non-numeric tip amount
    with self.assertRaises(TypeError, msg='Non-numeric value in tips tuple did not raise TypeError.'):
      rbs.validate_params(tips=('four', 3.72))
    # Test boolean tip
    with self.assertRaises(TypeError, msg='Boolean value in tips tuple did not raise TypeError.'):
      rbs.validate_params(tips=(4.23, True))
    # Test negative tip amount
    with self.assertRaises(ValueError, msg='Negative value in tips tuple did not raise ValueError.'):
      rbs.validate_params(tips=(6.24, -5.73))
    # Test invalid parameter name
    with self.assertRaises(ValueError, msg='Invalid parameter name did not raise ValueError.'):
      rbs.validate_params(table_nubmer=6)

    # tear down test fixture by wiping slate clean again and saving to the JSON to keep the file clear of any table assignments and reservations created saved to the file by the tests
  def tearDown(self):
    rbs.tables.clear()
    rbs.tables.update({
       1: {'capacity': 2, 'status': 'available'},
       2: {'capacity': 2, 'status': 'available'},
       3: {'capacity': 4, 'status': 'available'},
       4: {'capacity': 4, 'status': 'available'},
       5: {'capacity': 4, 'status': 'available'},
       6: {'capacity': 6, 'status': 'available'},
       7: {'capacity': 8, 'status': 'available'}
    })
    rbs.reservations.clear()
    rbs.reservations.update({1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []})
    rbs.reservation_lookup.clear()
    rbs.Order.order_count = 0
    rbs.Reservation.reservation_count = 0
    rbs.max_capacity = 0
    for t in rbs.tables:
      rbs.max_capacity += rbs.tables[t]['capacity']
    rbs.menu = {
    "foods": {
      "Pancakes": 4.0,
      "Scrambled Eggs": 4.5,
      "Waffles": 4.5,
      "Tuna Sandwich": 3.5,
      "Turkey Club Sandwich": 5.0,
      "Ham Sandwich": 3.0,
      "Salad": 2.5,
      "Soup": 2.0,
      "Spaghetti": 6.0,
      "Pork Chops": 8.0,
      "Chicken Fingers": 5.0,
      "Steak": 8.5,
      "Bacon": 1.0,
      "Sausage": 1.0,
      "French Fries": 1.75,
      "Mashed Potatoes": 2.0,
      "Ice Cream": 2.5
    },
    "drinks": {
      "Orange Juice": 1.5,
      "Apple Juice": 1.5,
      "Coca Cola": 2.0,
      "Sprite": 2.0,
      "Grape Soda": 1.75,
      "White Wine": 5.0,
      "Red Wine": 5.0,
      "Beer": 3.5,
      "Sparkling Water": 1.75
    }}
    rbs.save_data()

unittest.main()
