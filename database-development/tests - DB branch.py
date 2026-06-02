import unittest
import Restaurant_Business_Software as rbs
from datetime import datetime, timezone, timedelta
import json, os
from unittest.mock import patch
from io import StringIO
from decimal import Decimal, ROUND_HALF_UP

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
  
  # test the load_data function
  def test_load_data(self):
    # store the original database file to a new variable before changing the DB_file value to the copy needed for this test - relevant for the test feature tearDown, which resets all values and runs save_data
    original_db = rbs.DB_FILE
    # set the DB_file to copy of the JSON specifically for testing load_data
    rbs.DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'restaurant_data - test_load_data.json')
    # since load_data adds each table capacity to max_capacity with += and the test setUp sets max_capacity = 30 for use in other tests, we need to reset max_capacity to 0 here before running load_data
    rbs.max_capacity = 0 
    rbs.load_data()
    # Check that tables dictionary loaded correctly - all table numbers should exist with correct capacity and all statuses 'available'
    self.assertEqual(rbs.tables, {
       1: {'capacity': 2, 'status': 'available'},
       2: {'capacity': 2, 'status': 'available'},
       3: {'capacity': 4, 'status': 'available'},
       4: {'capacity': 4, 'status': 'available'},
       5: {'capacity': 4, 'status': 'available'},
       6: {'capacity': 6, 'status': 'available'},
       7: {'capacity': 8, 'status': 'available'}
    }, 'Load_data did not correctly populate the tables dict.')
    # Check that reservations dictionary updated correctly with reservation ID rsv-00001 added to table 1 reservations list with no other values added and empty lists for all other table numbers
    self.assertEqual(rbs.reservations, {1: ['rsv-00001'], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}, 'Load_data did not correctly populate the reservations dict.')
    # Check that reservation_lookup updated correctly with reservation ID rsv-00001 added as a key with all the correct reservation info and no additional reservations or data.
    self.assertEqual(rbs.reservation_lookup, {
      "rsv-00001": {
        "name": "Mark", 
        "reserved_time": "19:00 05-07-2026", 
        "num_diners": 2, 
        "vip_status": False, 
        "tables": [1]}
      }, 'Load_data did not correctly populate the reservation_lookup dict.')
    # Check that the menu dictionary updated correctly with all items and prices and nothing extra.
    self.assertEqual(rbs.menu, {
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
        "Ice Cream": 2.5},
      "drinks": {
        "Orange Juice": 1.5,
        "Apple Juice": 1.5,
        "Coca Cola": 2.0,
        "Sprite": 2.0,
        "Grape Soda": 1.75,
        "White Wine": 5.0,
        "Red Wine": 5.0,
        "Beer": 3.5,
        "Sparkling Water": 1.75}
      }, 'Load_data did not correctly populate the menu dict.')
    # Check that globacl variable max_capacity has correct value of 30 from summing tables' capacities
    self.assertEqual(rbs.max_capacity, 30, 'Load_data did not correctly calculate value for max_capacity.')
    # Check that order_count and reservation_count have correct values from the JSON of 3 and 1, resepectively
    self.assertEqual(rbs.Order.order_count, 3, 'Load_data did not correctly set the value of order_count.')
    self.assertEqual(rbs.Reservation.reservation_count, 1, 'Load_data did not correctly set the value of reservation_count.')
    # reset the DB_file to original before test tearDown
    rbs.DB_FILE = original_db
  
  # test save_data functions
  def test_save_data(self):
    # store the original database file to a new variable before changing the DB_file value to the copy needed for this test - relevant for the test feature tearDown, which resets all values and runs save_data
    original_db = rbs.DB_FILE
    # set the DB_file to copy of the JSON specifically for testing save_data
    rbs.DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'restaurant_data - test_save_data.json')
    # Write an empty dict to the JSON copy to ensure that the file is in a known wrong state prior to saving
    with open(rbs.DB_FILE, 'w') as f:
      json.dump({}, f)
    # Manually set alternate values to be saved - add a single reservationa and adjust the order and reservation counters. The rest will remain unchanged from the baseline set by the test feature setUp
    rbs.Order.order_count = 3
    rbs.Reservation.reservation_count = 1
    rbs.reservations = {1: ['rsv-00001'], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}
    rbs.reservation_lookup = {
      "rsv-00001": {
        "name": "Mark", 
        "reserved_time": "19:00 05-07-2026", 
        "num_diners": 2, 
        "vip_status": False, 
        "tables": [1]
      }
    }
    # run save_data
    rbs.save_data()
    # Use context manager to read the data from the newly saved file independently of the load_data function. Don't want test for save_data to inadvertently fail due to an issue with load_data.
    with open(rbs.DB_FILE, 'r') as f:
      data = json.load(f)
    # Check that tables dictionary saved correctly - all table numbers should exist with correct capacity and all statuses 'available'. The string value table number keys used in the JSON must be converted to integer value keys when doing this comparison.
    self.assertEqual({int(k): v for k, v in data['tables'].items()}, {
       1: {'capacity': 2, 'status': 'available'},
       2: {'capacity': 2, 'status': 'available'},
       3: {'capacity': 4, 'status': 'available'},
       4: {'capacity': 4, 'status': 'available'},
       5: {'capacity': 4, 'status': 'available'},
       6: {'capacity': 6, 'status': 'available'},
       7: {'capacity': 8, 'status': 'available'}
      }, 'Save_data did not correctly write the data from the tables dict to the JSON.')
    # Check that reservations dictionary saved correctly with reservation ID rsv-00001 added to table 1 reservations list with no other values added and empty lists for all other table numbers. The string value table number keys used in the JSON must be converted to integer value keys when doing this comparison.
    self.assertEqual({int(k): v for k, v in data['reservations'].items()}, {1: ['rsv-00001'], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}, 'Save_data did not correctly write the data from the reservations dict to the JSON.')
    # Check that reservation_lookup saved correctly with reservation ID rsv-00001 added as a key with all the correct reservation info and no additional reservations or data.
    self.assertEqual(data['reservation_lookup'], {
      "rsv-00001": {
        "name": "Mark", 
        "reserved_time": "19:00 05-07-2026", 
        "num_diners": 2, 
        "vip_status": False, 
        "tables": [1]}
      }, 'Save_data did not correctly write the data from reservation_lookup dict to the JSON.')
    # Check that the menu dictionary saved correctly with all items and prices and nothing extra.
    self.assertEqual(data['menu'], {
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
        "Ice Cream": 2.5},
      "drinks": {
        "Orange Juice": 1.5,
        "Apple Juice": 1.5,
        "Coca Cola": 2.0,
        "Sprite": 2.0,
        "Grape Soda": 1.75,
        "White Wine": 5.0,
        "Red Wine": 5.0,
        "Beer": 3.5,
        "Sparkling Water": 1.75}
      }, 'Save_data did not correctly write the data from the menu dict to the JSON.')
    # Check that order_count and reservation_count saved to the JSON with correct values of 3 and 1, resepectively
    self.assertEqual(data['order_count'], 3, 'Save_data did not correctly write the value of order_count to the JSON.')
    self.assertEqual(data['reservation_count'], 1, 'Save_data did not correctly write the value of reservation_count to the JSON.')
    # reset the DB_file to original before test tearDown
    rbs.DB_FILE = original_db
  
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

  # test check_seating_capacity helper function
  def test_check_seating_capacity(self):
    # Test single table capacity
    with self.assertRaises(ValueError, msg='Party_size greater than single table capacity did not raise ValueError.'):
      rbs.check_seating_capacity(party_size=6, table_numbers=(1,))
    # Test combined table capacity
    with self.assertRaises(ValueError, msg='Party_size greater than combined table capacity did not raise ValueError.'):
      rbs.check_seating_capacity(party_size=10, table_numbers=(1, 4))
  
  # test check_time_conflict helper functions
  def test_check_time_conflict(self):
    # Set mock reservations
    rbs.Reservation.reservation_count = 2
    rbs.reservations[5] = ['rsv-00001']
    rbs.reservations[2] = ['rsv-00002']
    rbs.reservations[7] = ['rsv-00002']
    rbs.reservation_lookup['rsv-00001'] = {'name': 'Mark', 'reserved_time': '20:00 04-30-2026', 'num_diners': 4, 'vip_status': False, 'tables': [5]}
    rbs.reservation_lookup['rsv-00002'] = {'name': 'Dave', 'reserved_time': '19:00 05-01-2026', 'num_diners': 10, 'vip_status': False, 'tables': [2, 7]}
    # Test case for future_only comparison, single table, no exclusion, with conflicting reservation in the future
    with self.assertRaises(ValueError, msg='Seating time conflict with upcoming reservation on single table did not raise ValueError.'):
      rbs.check_time_conflict(time='19:30 04-30-2026', table_numbers=(5,), future_only=True)
    # Test case for future_only comparison, combined tables, no exclusion, with conflicting reservation in the future
    with self.assertRaises(ValueError, msg='Seating time conflict with upcoming reservation on combined tables did not raise ValueError.'):
      rbs.check_time_conflict(time='19:30 04-30-2026', table_numbers=(4, 5), future_only=True)
    # Test case for future_only comparison to confirm it does not raise an error based on a reservation time in the past (e.g. in the event of reservation no-show, staff should have the discretion to seat someone else at the table without being blocked by the function)
    # Single table scenario
    try:
      rbs.check_time_conflict(time='20:30 04-30-2026', table_numbers=(5,), future_only=True)
    except ValueError:
      self.fail('check_time_conflict incorrectly flagged a conflict for future_only with a reservation in the past on single table.')
    # Combined table scenario
    try:
      rbs.check_time_conflict(time='20:30 04-30-2026', table_numbers=(4, 5), future_only=True)
    except ValueError:
      self.fail('check_time_conflict incorrectly flagged a conflict for future_only with a reservation in the past on linked table.')
    # Test case for both directions comparison, single table, no exclusion
    with self.assertRaises(ValueError, msg='Reservation time conflict with existing reservation on single table did not raise ValueError.'):
      rbs.check_time_conflict(time='19:30 04-30-2026', table_numbers=(5,))
    # Test case for both directions comparison, combined tables, no exclusion
    with self.assertRaises(ValueError, msg='Reservation time conflict with existing reservation on combined table did not raise ValueError.'):
      rbs.check_time_conflict(time='19:30 05-01-2026', table_numbers=(5, 2))
    # Test case for both directions comparison, single table, with exclusion and no other conflict - expectation is that this will NOT raise an error for the excluded reservation conflicting with itself
    try:
      rbs.check_time_conflict(time='20:30 04-30-2026', table_numbers=(5,), exclude_id='rsv-00001')
    except ValueError:
      self.fail('check_time_conflict incorrectly flagged a conflict with the excluded reservation ID on single table.')
    # Test case for both directions comparison, combined tables, with exclusion of a single-table reservation
    try:
      rbs.check_time_conflict(time='20:30 04-30-2026', table_numbers=(4, 5), exclude_id='rsv-00001')
    except ValueError:
      self.fail('check_time_conflict incorrectly flagged a conflict with the excluded reservation ID on linked table.')
    # Test case for both directions comparison, combined tables, with exclusion of a multi-table reservation
    try:
      rbs.check_time_conflict(time='19:30 05-01-2026', table_numbers=(5, 2, 7), exclude_id='rsv-00002')
    except ValueError:
      self.fail('check_time_conflict incorrectly flagged a conflict with the excluded multi-table reservation ID on linked tables.')
    # Test case to check that only the excluded reservation ID is omitted - should still raise an error
    with self.assertRaises(ValueError, msg='Reservation time conflict with existing reservation on combined table did not raise ValueError.'):
      rbs.check_time_conflict(time='19:30 05-01-2026', table_numbers=(5, 2), exclude_id='rsv-00001')

  # test to check the results of assigning a single table
  def test_assign_single_table(self):
    # Test a single table assignment
    rbs.assign_table(1, name='John', party_size=2)
    self.assertEqual(rbs.tables[1]['name'], 'John', 'Name \'John\' not assigned to table 2.')
    self.assertEqual(rbs.tables[1]['status'], 'occupied', 'Table 1 status not set to \'occupied\'.')
    self.assertEqual(rbs.tables[1]['num_diners'], 2, 'Table 1 num_diners not set to 2.')
    self.assertEqual(rbs.tables[1]['vip_status'], False, 'Table 1 vip_status not set to False.')
    self.assertEqual(rbs.tables[1]['has_reservation'], False, 'Table 1 reservation status not set to False.')
    self.assertEqual(rbs.tables[1]['seating_time'], datetime.now(timezone(timedelta(hours=-6))).strftime('%H:%M %m-%d-%Y'), 'Table 1 seating time does not equal current time.')
    self.assertEqual(rbs.tables[1]['order']['ord_number'], '00001', 'Table 1 order number status not set 00001.')
    self.assertIsNone(rbs.tables[1]['total'], 'Table 1 total is not None.')
    self.assertIn('linked_tables', rbs.tables[1], 'Key \'linked_tables\' not created on table number 1.')
    self.assertEqual(rbs.tables[1]['linked_tables'], [], 'Table 1 linked_tables not set to empty list.')
    # Check the full table assignment info in the tables dict to confirm no extra keys or values were created
    self.assertEqual(rbs.tables[1], {'capacity': 2, 'status': 'occupied', 'name': 'John', 'num_diners': 2, 'vip_status': False, 'has_reservation': False, 'seating_time': datetime.now(timezone(timedelta(hours=-6))).strftime('%H:%M %m-%d-%Y'), 'order': {'ord_number': '00001'}, 'total': None, 'linked_tables': []}, 'Full single table assignment info for table 2 does not match expected values.')
    # Confirm reservations table was not altered.
    self.assertEqual(rbs.reservations[1], [], 'Table 1 reservations modified from an empty list.')
    # Check full tables dict to confirm no other tables were modified
    self.assertEqual(rbs.tables, {
      1: {'capacity': 2, 'status': 'occupied', 'name': 'John', 'num_diners': 2, 'vip_status': False, 'has_reservation': False, 'seating_time': datetime.now(timezone(timedelta(hours=-6))).strftime('%H:%M %m-%d-%Y'), 'order': {'ord_number': '00001'}, 'total': None, 'linked_tables': []},
      2: {'capacity': 2, 'status': 'available'},
      3: {'capacity': 4, 'status': 'available'},
      4: {'capacity': 4, 'status': 'available'},
      5: {'capacity': 4, 'status': 'available'},
      6: {'capacity': 6, 'status': 'available'},
      7: {'capacity': 8, 'status': 'available'}
    }, 'Full tables dict does not match expected values after single table assignment.')

  # test to check the results of assigning combined tables
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
    self.assertEqual(rbs.tables[7]['has_reservation'], False, 'Primary table 7 reservation status not set to False.')
    self.assertNotIn('has_reservation', rbs.tables[3], 'Non-primary table number 3 has a \'has_reservation\' key.')
    self.assertNotIn('has_reservation', rbs.tables[4], 'Non-primary table number 4 has a \'has_reservation\' key.')
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
    # Check full table assignment info to confirm no extra keys or values were created
    self.assertEqual(rbs.tables[7], {'capacity': 8, 'status': 'occupied', 'name': 'John', 'num_diners': 15, 'vip_status': False, 'has_reservation': False, 'seating_time': datetime.now(timezone(timedelta(hours=-6))).strftime('%H:%M %m-%d-%Y'), 'order': {'ord_number': '00001'}, 'total': None, 'linked_tables': [3, 4]}, 'Full table assignment info for primary table 7 does not match expected values.')
    self.assertEqual(rbs.tables[3], {'capacity': 4, 'status': 'occupied', 'linked_tables': [7, 4]}, 'Full table assignment info for non-primary table 3 does not match expected values.')
    self.assertEqual(rbs.tables[4], {'capacity': 4, 'status': 'occupied', 'linked_tables': [7, 3]}, 'Full table assignment info for non-primary table 4 does not match expected values.')
    # Confirm reservations table was not altered.
    self.assertEqual(rbs.reservations[7], [], 'Primary table 7 reservations modified from an empty list.')
    # Check full tables dict to confirm no other tables were modified
    self.assertEqual(rbs.tables, {
      1: {'capacity': 2, 'status': 'available'},
      2: {'capacity': 2, 'status': 'available'},
      3: {'capacity': 4, 'status': 'occupied', 'linked_tables': [7, 4]},
      4: {'capacity': 4, 'status': 'occupied', 'linked_tables': [7, 3]},
      5: {'capacity': 4, 'status': 'available'},
      6: {'capacity': 6, 'status': 'available'},
      7: {'capacity': 8, 'status': 'occupied', 'name': 'John', 'num_diners': 15, 'vip_status': False, 'has_reservation': False, 'seating_time': datetime.now(timezone(timedelta(hours=-6))).strftime('%H:%M %m-%d-%Y'), 'order': {'ord_number': '00001'}, 'total': None, 'linked_tables': [3, 4]}
    }, 'Full tables dict does not match expected values after combined table assignment.')

  # test for the contextual checks of the assign_table arguments
  def test_assign_table_arguments(self):
    # Test missing table numbers
    with self.assertRaises(ValueError, msg='Missing *table_numbers did not raise ValueError.'):
      rbs.assign_table(name='John', party_size=3, vip_status=True, reserve_status=False)
    # Test table number already occupied
    rbs.Order.order_count = 1
    rbs.tables[2] = {'capacity': 2, 'status': 'occupied', 'name': 'Customer', 'vip_status': False, 'has_reservation': False, 'seating_time': datetime.now(timezone(timedelta(hours=-6))).strftime('%H:%M %m-%d-%Y'), 'num_diners': 2, 'order': {'ord_number': '00001'}, 'total': None}
    # Single/primary table assignment conflict
    with self.assertRaises(ValueError, msg='Occupied single/primary table number did not raise ValueError.'):
      rbs.assign_table(2, name='John', party_size=2, vip_status=True, reserve_status=False)
    # Linked table assignment conflict
    with self.assertRaises(ValueError, msg='Occupied linked table number did not raise ValueError.'):
      rbs.assign_table(6, 2, name='John', party_size=8, vip_status=True, reserve_status=False)  
    # Confirm empty name string coerced to default value 'Customer'
    rbs.assign_table(3, name='', party_size=4)
    self.assertEqual(rbs.tables[3]['name'], 'Customer', 'Empty name string in assign_table was not coerced to default value \'Customer\'.')
    # Test table number has upcoming reservation to confirm successful call of check_time_conflict helper function
    rbs.Reservation.reservation_count = 1
    rbs.reservations[5] = ['rsv-00001']
    rbs.reservation_lookup['rsv-00001'] = {'name': 'Mark', 'reserved_time': '19:00 04-30-2026', 'num_diners': 4, 'vip_status': False, 'tables': [5]}
    # Table 5 assigned at a time of 18:30 04-30-2026 with upcoming reservation on the table at 19:00 04-30-2026
    with self.assertRaises(ValueError, msg='Seating time conflict with upcoming reservation did not raise ValueError. Check_time_conflict call failed.'):
      rbs.assign_table(5, name='John', party_size=3, vip_status=True, reserve_status=False, time='18:30 04-30-2026')
    # Test party_size exceeds capacity to confirm successful call of check_seating_capacity helper function
    # Table 5 with capacity=4 assigned to party of 5
    with self.assertRaises(ValueError, msg='Party size greater than single table capacity did not raise ValueError. Check_seating_capacity call failed.'):
      rbs.assign_table(5, name='John', party_size=5, vip_status=True, reserve_status=False)
    
  # test the reservation counter reset functionality of the Reservation class
  def test_reservation_counter_reset(self):
    # set the reservation_count to maximum allowed value before reset
    rbs.Reservation.reservation_count = 99999
    # instantiate a new instance of the Reservation class
    rsv = rbs.Reservation()
    self.assertEqual(rbs.Reservation.reservation_count, 1, 'Reservation counter did not reset to 1 after reaching 99999.')
    self.assertEqual(rsv.ID, 'rsv-00001', 'Reservation ID after counter reset is not rsv-00001.')
  
  # Test add_reservation for single table
  def test_add_single_table_reservation(self):
    # Add reservation with single table number.
    rbs.add_reservation(6, time='19:00 05-10-2026', name='Mark', party_size=5, vip_status=True)
    # Confirm reservation class object created increasing the reservation_count
    self.assertEqual(rbs.Reservation.reservation_count, 1, 'Adding single table reservation did not initialize new reservation class object and reservation counter not increased.')
    # Check reservation ID added to the table's reservation list in the reservations dict
    self.assertIn('rsv-00001', rbs.reservations[6], 'Reservation ID not added to table reservation list in reservations dict for single table reservation.')
    # Check reservation ID was NOT added to a different table's reservation list in the reservations dict
    self.assertNotIn('rsv-00001', rbs.reservations[7], 'Reservation ID incorrectly added to other table number 7 in reservations dict.')
    # Check reservation ID added as a key in reservation_lookup dict
    self.assertIn('rsv-00001', rbs.reservation_lookup, 'Reservation ID not added to reservation_lookup for single table reservation.')
    # Check values within reservation ID's sub-dictionary in reservation_lookup
    self.assertEqual(rbs.reservation_lookup['rsv-00001']['name'], 'Mark', 'Name \'Mark\' not assigned to rsv-00001 in reservation_lookup.')
    self.assertEqual(rbs.reservation_lookup['rsv-00001']['reserved_time'], '19:00 05-10-2026', 'Time \'19:00 05-10-2026\' not assigned to rsv-00001 in reservation_lookup.')
    self.assertEqual(rbs.reservation_lookup['rsv-00001']['num_diners'], 5, 'Party size 5 not assigned to \'num_diners\' for rsv-00001 in reservation_lookup.')
    self.assertEqual(rbs.reservation_lookup['rsv-00001']['tables'], [6], 'Table number 6 not assigned to \'tables\' for rsv-00001 in reservation_lookup.')
    self.assertEqual(rbs.reservation_lookup['rsv-00001']['vip_status'], True, 'Vip_status not set to True for rsv-00001 in reservation_lookup.')
    # Check full reservation info to confirm no extraneous keys or values were created
    self.assertEqual(rbs.reservation_lookup['rsv-00001'], {'name': 'Mark', 'reserved_time': '19:00 05-10-2026', 'num_diners': 5, 'tables': [6], 'vip_status': True}, 'Full reservation info for rsv-00001 does not match expected values for single table reservation.')
    # Check that the main tables dict was not modified by add_reservation
    self.assertEqual(rbs.tables[6], {'capacity': 6, 'status': 'available'}, 'Tables dict entry for table 6 was incorrectly modified by add_reservation.')
  
  def test_add_combined_tables_reservation(self):
    # Add reservation with multiple table numbers.
    rbs.add_reservation(6, 1, 5, time='19:00 05-07-2026', name='John', party_size=11)
    # Confirm reservation class object created increasing the reservation_count
    self.assertEqual(rbs.Reservation.reservation_count, 1, 'Adding combined table reservation did not initialize new reservation class object and reservation counter not increased.')
    # Check reservation ID added to the all tables' reservation lists in the reservations dict
    self.assertIn('rsv-00001', rbs.reservations[6], 'Reservation ID not added to table 6 reservation list in reservations dict for combined table reservation.')
    self.assertIn('rsv-00001', rbs.reservations[1], 'Reservation ID not added to table 1 reservation list in reservations dict for combined table reservation.')
    self.assertIn('rsv-00001', rbs.reservations[5], 'Reservation ID not added to table 5 reservation list in reservations dict for combined table reservation.')
    # Check reservation ID was NOT added to a different table's reservation list in the reservations dict
    self.assertNotIn('rsv-00001', rbs.reservations[7], 'Reservation ID incorrectly added to other table number 7 in reservations dict on combined table reservation.')
    # Check reservation ID added as a key in reservation_lookup dict
    self.assertIn('rsv-00001', rbs.reservation_lookup, 'Reservation ID not added to reservation_lookup for combined table reservation.')
    # Check values within reservation ID's sub-dictionary in reservation_lookup
    self.assertEqual(rbs.reservation_lookup['rsv-00001']['name'], 'John', 'Name \'John\' not assigned to rsv-00001 in reservation_lookup when adding combined tables reservation.')
    self.assertEqual(rbs.reservation_lookup['rsv-00001']['reserved_time'], '19:00 05-07-2026', 'Time \'19:00 05-07-2026\' not assigned to rsv-00001 in reservation_lookup when adding combined tables reservation.')
    self.assertEqual(rbs.reservation_lookup['rsv-00001']['num_diners'], 11, 'Party size 11 not assigned to \'num_diners\' for rsv-00001 in reservation_lookup when adding combined tables reservation.')
    self.assertEqual(rbs.reservation_lookup['rsv-00001']['tables'], [6, 1, 5], 'One or more table numbers not added to \'tables\' list for rsv-00001 in reservation_lookup.')
    self.assertEqual(rbs.reservation_lookup['rsv-00001']['vip_status'], False, 'Vip_status not set to False for rsv-00001 in reservation_lookup.')
    # Check full reservation info to confirm no extraneous keys or values were created
    self.assertEqual(rbs.reservation_lookup['rsv-00001'], {'name': 'John', 'reserved_time': '19:00 05-07-2026', 'num_diners': 11, 'tables': [6, 1, 5], 'vip_status': False}, 'Full reservation info for rsv-00001 does not match expected values for combined table reservation.')
    # Check that the main tables dict was not modified by add_reservation
    self.assertEqual(rbs.tables[6], {'capacity': 6, 'status': 'available'}, 'Tables dict entry for table 6 was incorrectly modified by add_reservation with combined tables.')
    self.assertEqual(rbs.tables[1], {'capacity': 2, 'status': 'available'}, 'Tables dict entry for table 1 was incorrectly modified by add_reservation with combined tables.')
    self.assertEqual(rbs.tables[5], {'capacity': 4, 'status': 'available'}, 'Tables dict entry for table 5 was incorrectly modified by add_reservation with combined tables.')

  def test_add_reservation_parameters(self):
    # Check empty string name entry
    with self.assertRaises(ValueError, msg='Blank name string did not return value error when adding reservation.'):
      rbs.add_reservation(4, time='19:00 05-07-2026', name='   ', party_size=4)
    # Test table number has upcoming reservation to confirm successful call of check_time_conflict helper function
    rbs.Reservation.reservation_count = 1
    rbs.reservations[5] = ['rsv-00001']
    rbs.reservation_lookup['rsv-00001'] = {'name': 'Mark', 'reserved_time': '19:00 05-02-2026', 'num_diners': 4, 'vip_status': False, 'tables': [5]}
    # New reservation on table 5 for 18:30 05-02-2026 only 30 min before existing reservation
    with self.assertRaises(ValueError, msg='Requested reservation time conflict with existing reservation did not raise ValueError. Check_time_conflict call failed.'):
      rbs.add_reservation(5, time='18:30 05-02-2026', name='John', party_size=4)
    # Test party_size exceeds capacity to confirm successful call of check_seating_capacity helper function
    # Table 2 with capacity=2 used for reservation of party of 4
    with self.assertRaises(ValueError, msg='Reservation party size greater than table capacity did not raise ValueError. Check_seating_capacity call failed.'):
      rbs.add_reservation(2, time='18:30 05-02-2026', name='John', party_size=4)

  # test find_reservation function
  def test_find_reservation(self):
    # create reservation to search for
    rbs.Reservation.reservation_count = 1
    rbs.reservations[5] = ['rsv-00001']
    rbs.reservation_lookup['rsv-00001'] = {'name': 'Mark', 'reserved_time': '19:00 05-02-2026', 'num_diners': 4, 'vip_status': False, 'tables': [5]}
    # check reservation ID successfully returned
    self.assertEqual(rbs.find_reservation('Mark', '19:00 05-02-2026'), 'rsv-00001', 'find_reservation did not correctly return the reservation ID.')
    # Confirm that the search only read data from reservation_lookup without modifying it - use a full dict equality check
    self.assertEqual(rbs.reservation_lookup, {'rsv-00001': {'name': 'Mark', 'reserved_time': '19:00 05-02-2026', 'num_diners': 4, 'vip_status': False, 'tables': [5]}}, 'find_reservation inadvertently modified reservation_lookup.')
    # Check empty name string
    with self.assertRaises(ValueError, msg='Blank name string did not return ValueError in find_reservation.'):
      rbs.find_reservation('', '19:00 05-02-2026')
    # Check no matching reservation for the given name and time
    self.assertIsNone(rbs.find_reservation('Mark', '19:00 05-10-2026'), 'find_reservation did not return None when searching a name and time with no corresponding reservation.')

  # test canceL_reservation function
  def test_cancel_reservation(self):
    # create two reservations to cancel - one single table, one combined tables - and one that won't be canceled
    rbs.Reservation.reservation_count = 3
    rbs.reservations[5] = ['rsv-00001']
    rbs.reservation_lookup['rsv-00001'] = {'name': 'Mark', 'reserved_time': '19:00 05-10-2026', 'num_diners': 4, 'vip_status': False, 'tables': [5]}
    rbs.reservations[1] = ['rsv-00002']
    rbs.reservations[3] = ['rsv-00002']
    rbs.reservations[7] = ['rsv-00002']
    rbs.reservation_lookup['rsv-00002'] = {'name': 'John', 'reserved_time': '19:00 05-10-2026', 'num_diners': 14, 'vip_status': False, 'tables': [7, 1, 3]}
    rbs.reservations[4] = ['rsv-00003']
    rbs.reservation_lookup['rsv-00003'] = {'name': 'Dave', 'reserved_time': '19:00 05-10-2026', 'num_diners': 4, 'vip_status': True, 'tables': [4]}
    # check non-string reservation ID
    with self.assertRaises(TypeError, msg='Non-string reservation ID did not return TypeError from cancel_reservation.'):
      rbs.cancel_reservation(1)
    # check reservation ID not found
    with self.assertRaises(ValueError, msg='Non-existent reservation ID did not return ValueError from cancel_reservation.'):
      rbs.cancel_reservation('rsv-00005')  
    # check cancel single table reservation
    rbs.cancel_reservation('rsv-00001')
    self.assertNotIn('rsv-00001', rbs.reservations[5], 'Reservation ID rsv-00001 was not removed from table 5 reservations list when single table reservation canceled.')
    self.assertNotIn('rsv-00001', rbs.reservation_lookup, 'Reservation ID rsv-00001 was not removed from reservation_lookup when reservation canceled.')
    # check cancel combined tables reservation
    rbs.cancel_reservation('rsv-00002')
    self.assertNotIn('rsv-00002', rbs.reservations[7], 'Reservation ID rsv-00002 was not removed from primary table 7 reservations list when reservation canceled.')
    self.assertNotIn('rsv-00002', rbs.reservations[1], 'Reservation ID rsv-00002 was not removed from linked table 1 reservations list when reservation canceled.')
    self.assertNotIn('rsv-00002', rbs.reservations[3], 'Reservation ID rsv-00002 was not removed from linked table 3 reservations list when reservation canceled.')
    self.assertNotIn('rsv-00002', rbs.reservation_lookup, 'Reservation ID rsv-00002 was not removed from reservation_lookup when combined table reservation canceled.')
    # check that cancelations made no other modifications to reservations and reservation_lookup dicts
    self.assertEqual(rbs.reservations, {1: [], 2: [], 3: [], 4: ['rsv-00003'], 5: [], 6: [], 7: []}, 'Canceling reservations incorrectly made other modifications to reservations dict.')
    self.assertEqual(rbs.reservation_lookup, {'rsv-00003': {'name': 'Dave', 'reserved_time': '19:00 05-10-2026', 'num_diners': 4, 'vip_status': True, 'tables': [4]}}, 'Canceling reservations incorrectly made other modifications to reservation_lookup dict.')

  # test assign_table_from_reservation
  def test_assign_table_from_reservation(self):
    # Create reservations to use for test - most will be assigned for the test and one will remain unassigned to check the reservations and reservation_lookup dicts after others are assigned
    rbs.Reservation.reservation_count = 4
    rbs.reservations[5] = ['rsv-00001']
    rbs.reservation_lookup['rsv-00001'] = {'name': 'Mark', 'reserved_time': '19:00 05-7-2026', 'num_diners': 4, 'vip_status': False, 'tables': [5]}
    rbs.reservations[1] = ['rsv-00002']
    rbs.reservations[3] = ['rsv-00002']
    rbs.reservations[7] = ['rsv-00002']
    rbs.reservation_lookup['rsv-00002'] = {'name': 'John', 'reserved_time': '19:00 05-7-2026', 'num_diners': 14, 'vip_status': False, 'tables': [7, 1, 3]}
    rbs.reservations[4] = ['rsv-00003', 'rsv-00004']
    rbs.reservation_lookup['rsv-00003'] = {'name': 'Dave', 'reserved_time': '19:00 05-7-2026', 'num_diners': 4, 'vip_status': True, 'tables': [4]}    
    rbs.reservation_lookup['rsv-00004'] = {'name': 'Lisa', 'reserved_time': '19:00 05-10-2026', 'num_diners': 4, 'vip_status': False, 'tables': [4]}   
    # Test non-string reservation ID
    with self.assertRaises(TypeError, msg='Non-string reservation ID did not raise a TypeError when assigning table from reservation.'):
      rbs.assign_table_from_reservation('rsv-00001', 2)
    # Test single reservation ID input
    rbs.assign_table_from_reservation('rsv-00001')
    # Check that internal assign_table call worked by confirming tables dict updated
    self.assertEqual(rbs.tables[5], {'capacity': 4, 'status': 'occupied', 'name': 'Mark', 'vip_status': False, 'has_reservation': True, 'seating_time': '19:00 05-7-2026', 'num_diners': 4, 'order': {'ord_number': '00001'}, 'total': None, 'linked_tables': []}, 'Assigning table from reservation ID rsv-00001 did not correctly update tables dict.')
    # Check that the reservation ID was removed from the table's reservations list and from the reservation_lookup dict on successful assignment
    self.assertNotIn('rsv-00001', rbs.reservations[5], 'Assigning table from reservation did not remove reservation ID rsv-00001 from table 5 reservations list.')
    self.assertNotIn('rsv-00001', rbs.reservation_lookup, 'Assigning table from reservation did not remove reservation ID rsv-00001 from reservation_lookup dict.')
    # Test multiple reservation IDs input with one non-existent ID in the middle to confirm it gets skipped without raising error and the rest still process.
    rbs.assign_table_from_reservation('rsv-00002', 'rsv-00005', 'rsv-00003')
    # Confirm the first valid reservation ID table assignment worked by checking tables dict
    # Check primary table
    self.assertEqual(rbs.tables[7], {'capacity': 8, 'status': 'occupied', 'name': 'John', 'vip_status': False, 'has_reservation': True, 'seating_time': '19:00 05-7-2026', 'num_diners': 14, 'order': {'ord_number': '00002'}, 'total': None, 'linked_tables': [1, 3]}, 'With multiple reservation IDs input, assigning table from reservation ID rsv-00002 did not correctly update tables dict on primary table 7.')
    # Check linked tables
    self.assertEqual(rbs.tables[1], {'capacity': 2, 'status': 'occupied', 'linked_tables': [7, 3]}, 'With multiple reservation IDs input, assigning table from reservation ID rsv-00002 did not correctly update tables dict on linked table 1.')
    self.assertEqual(rbs.tables[3], {'capacity': 4, 'status': 'occupied', 'linked_tables': [7, 1]}, 'With multiple reservation IDs input, assigning table from reservation ID rsv-00002 did not correctly update tables dict on linked table 3.')
    # Check reservation ID removed from all three tables reservations lists and from reservation_lookup
    self.assertNotIn('rsv-00002', rbs.reservations[7], 'With multiple reservation IDs input, assigning tables from reservation did not remove reservation ID rsv-00002 from primary table 7 reservations list.')
    self.assertNotIn('rsv-00002', rbs.reservations[1], 'With multiple reservation IDs input, assigning tables from reservation did not remove reservation ID rsv-00002 from linked table 1 reservations list.')
    self.assertNotIn('rsv-00002', rbs.reservations[3], 'With multiple reservation IDs input, assigning tables from reservation did not remove reservation ID rsv-00002 from linked table 3 reservations list.')
    self.assertNotIn('rsv-00002', rbs.reservation_lookup, 'With multiple reservation IDs input, assigning tables from reservation did not remove reservation ID rsv-00002 from reservation_lookup dict.')
    # Confirm non-existing ID skipped and remaining valid reservation ID table assignment worked
    self.assertEqual(rbs.tables[4], {'capacity': 4, 'status': 'occupied', 'name': 'Dave', 'vip_status': True, 'has_reservation': True, 'seating_time': '19:00 05-7-2026', 'num_diners': 4, 'order': {'ord_number': '00003'}, 'total': None, 'linked_tables': []}, 'Following non-existent reservation ID, assigning table from reservation ID rsv-00003 did not correctly update tables dict.')
    self.assertNotIn('rsv-00003', rbs.reservations[4], 'Following non-existent reservation ID, assigning table from reservation did not remove reservation ID rsv-00003 from table 4 reservations list.')
    self.assertNotIn('rsv-00003', rbs.reservation_lookup, 'Following non-existent reservation ID, assigning table from reservation did not remove reservation ID rsv-00003 from reservation_lookup dict.')
    # Check full values of tables, reservations, and reservation_lookup dicts to confirm no other values incorrectly added or modified
    self.assertEqual(rbs.tables, {
      1: {'capacity': 2, 'status': 'occupied', 'linked_tables': [7, 3]},
      2: {'capacity': 2, 'status': 'available'},
      3: {'capacity': 4, 'status': 'occupied', 'linked_tables': [7, 1]},
      4: {'capacity': 4, 'status': 'occupied', 'name': 'Dave', 'vip_status': True, 'has_reservation': True, 'seating_time': '19:00 05-7-2026', 'num_diners': 4, 'order': {'ord_number': '00003'}, 'total': None, 'linked_tables': []},
      5: {'capacity': 4, 'status': 'occupied', 'name': 'Mark', 'vip_status': False, 'has_reservation': True, 'seating_time': '19:00 05-7-2026', 'num_diners': 4, 'order': {'ord_number': '00001'}, 'total': None, 'linked_tables': []},
      6: {'capacity': 6, 'status': 'available'},
      7: {'capacity': 8, 'status': 'occupied', 'name': 'John', 'vip_status': False, 'has_reservation': True, 'seating_time': '19:00 05-7-2026', 'num_diners': 14, 'order': {'ord_number': '00002'}, 'total': None, 'linked_tables': [1, 3]}
    }, 'Final tables dict does not match expected values after assign_table_from_reservation calls.')
    self.assertEqual(rbs.reservations, {1: [], 2: [], 3: [], 4: ['rsv-00004'], 5: [], 6: [], 7: []}, 'Final reservations dict does not match expected values after assign_table_from_reservation calls.')
    self.assertEqual(rbs.reservation_lookup, {'rsv-00004': {'name': 'Lisa', 'reserved_time': '19:00 05-10-2026', 'num_diners': 4, 'vip_status': False, 'tables': [4]}}, 'Final reservation_lookup dict does not match expected values after assign_table_from_reservation calls.')    

  # test modify_reservation
  def test_modify_reservation(self):
    # Create dummy reservations to be modified - when checks require another reservation with some conflict, additional dummy reservations will be created for those specific checks
    rbs.reservations[5] = ['rsv-00001']
    rbs.reservation_lookup['rsv-00001'] = {'name': 'Mark', 'reserved_time': '19:00 05-12-2026', 'num_diners': 4, 'vip_status': False, 'tables': [5]}
    rbs.reservations[1] = ['rsv-00002']
    rbs.reservations[3] = ['rsv-00002']
    rbs.reservations[7] = ['rsv-00002']
    rbs.reservation_lookup['rsv-00002'] = {'name': 'John', 'reserved_time': '19:00 05-15-2026', 'num_diners': 14, 'vip_status': False, 'tables': [7, 1, 3]}
    # Set reservation count based on the highest number used in the test
    rbs.Reservation.reservation_count = 5
    # Validate reservation_ID
    # Check non-string reservation ID
    with self.assertRaises(TypeError, msg='Non-string reservation ID passed to modify_reservation did not raise TypeError.'):
      rbs.modify_reservation(1, new_time='19:00 05-13-2026')
    # Check non-existent reservation ID
    with self.assertRaises(ValueError, msg='Non-existent reservation ID passed to modify_reservation did not raise ValueError.'):
      rbs.modify_reservation('rsv-00100', new_time='19:00 05-13-2026')
    # Test no changes made, reservation ID is only argument passed
    # Validate output message printed for the user - use patch() from unittest.mock to create a mock object of the sys.stdout created using StringIO to read the output text from the print()
    with patch('sys.stdout', new_callable=StringIO) as mock_out:
      rbs.modify_reservation('rsv-00001')
    self.assertEqual(mock_out.getvalue(), 'No changes were made. Please provide at least one value to update.\n', 'modify_reservation call with no info being changed did not print output message.')
    # Full dict equality checks to confirm nothing changed in reservations and reservation_lookup
    self.assertEqual(rbs.reservations, {1: ['rsv-00002'], 2: [], 3: ['rsv-00002'], 4: [], 5: ['rsv-00001'], 6: [], 7: ['rsv-00002']}, 'Reservations dict incorrectly altered by modify_reservation when only reservation ID provided with no changes.')
    self.assertEqual(rbs.reservation_lookup, {
      'rsv-00001': {'name': 'Mark', 'reserved_time': '19:00 05-12-2026', 'num_diners': 4, 'vip_status': False, 'tables': [5]},
      'rsv-00002': {'name': 'John', 'reserved_time': '19:00 05-15-2026', 'num_diners': 14, 'vip_status': False, 'tables': [7, 1, 3]} 
      }, 'reservation_lookup dict incorrectly altered by modify_reservation when only reservation ID provided with no changes.')
    # Test isolated changes to arguments with no conditional dependencies to other arguments
    # Test new_name by itself
    # Check blank name string
    with self.assertRaises(ValueError, msg='Blank string for new_name in modify_reservation did not raise ValueError.'):
      rbs.modify_reservation('rsv-00002', new_name='  ')
    # Confirm updated ‘name’ in reservation_lookup with no other changes
    rbs.modify_reservation('rsv-00002', new_name='John Smith')    
    self.assertEqual(rbs.reservation_lookup['rsv-00002'], {'name': 'John Smith', 'reserved_time': '19:00 05-15-2026', 'num_diners': 14, 'vip_status': False, 'tables': [7, 1, 3]}, 'Full reservation info does not match expected values after modifying rsv-00002 with new name only.')
    # Test new_vip_status by itself
    rbs.modify_reservation('rsv-00001', new_vip_status=True)
    # Check updated 'vip_status' in reservation_lookup with no other changes    
    self.assertEqual(rbs.reservation_lookup['rsv-00001'], {'name': 'Mark', 'reserved_time': '19:00 05-12-2026', 'num_diners': 4, 'vip_status': True, 'tables': [5]}, 'Full reservation info does not match expected values after modifying rsv-00001 with new_vip_status only.')
    # Test isolated changes to arguments with conditional dependencies
    # Test new_table_numbers by itself
    # Check non-list table numbers
    with self.assertRaises(TypeError, msg='Non-list input for new_table_numbers in modify_reservation did not raise TypeError.'):
      rbs.modify_reservation('rsv-00001', new_table_numbers=4)
    # Confirm successful call of check_seating_capacity for new_table_numbers that cannot fit existing party size
    with self.assertRaises(ValueError, msg='New table numbers that cannot fit existing party size did not raise ValueError on isolated change with modify_reservation.'):
      rbs.modify_reservation('rsv-00002', new_table_numbers=[7, 1, 2])
    # Create another dummy reservation for time conflict check
    rbs.reservations[2] = ['rsv-00003']
    rbs.reservation_lookup['rsv-00003'] = {'name': 'Lisa', 'reserved_time': '19:00 05-15-2026', 'num_diners': 2, 'vip_status': False, 'tables': [2]}
    # Confirm successful call of check_time_conflict for new_table_numbers with a conflict against other reservation
    with self.assertRaises(ValueError, msg='New table numbers with time conflict against other reservation did not raise ValueError on isolated change with modify_reservation.'):
      rbs.modify_reservation('rsv-00002', new_table_numbers=[7, 2, 3])
    # Check updated 'tables' in reservation_lookup with no other changes.
    rbs.modify_reservation('rsv-00002', new_table_numbers=[4, 1, 3, 5])    
    self.assertEqual(rbs.reservation_lookup['rsv-00002'], {'name': 'John Smith', 'reserved_time': '19:00 05-15-2026', 'num_diners': 14, 'vip_status': False, 'tables': [4, 1, 3, 5]}, 'Full reservation info does not match expected values after modifying rsv-00002 with new_table_numbers only.')
    # Check reservation ID removed from old tables reservation lists and added to new tables reservation lists with no other changes   
    self.assertEqual(rbs.reservations, {1: ['rsv-00002'], 2: ['rsv-00003'], 3: ['rsv-00002'], 4: ['rsv-00002'], 5: ['rsv-00001', 'rsv-00002'], 6: [], 7: []}, 'Reservations dict does not match expected values after modifying rsv-00002 with new_table_numbers only.')
    # Test new_party_size
    # Confirm successful call of check_seating_capacity for new_party_size greater than existing tables' capacity
    with self.assertRaises(ValueError, msg='New party size larger than existing tables capacity did not raise ValueError on isolated change with modify_reservation.'):
      rbs.modify_reservation('rsv-00001', new_party_size=6)
    # Confirm updated 'num_diners' in reservation lookup with no other changes
    rbs.modify_reservation('rsv-00001', new_party_size=3)    
    self.assertEqual(rbs.reservation_lookup['rsv-00001'], {'name': 'Mark', 'reserved_time': '19:00 05-12-2026', 'num_diners': 3, 'vip_status': True, 'tables': [5]}, 'Full reservation info does not match expected values after modifying rsv-00001 with new_party_size only.')
    # Test new_time    
    # Create new dummy reservation for time conflict
    rbs.reservations[5].append('rsv-00004')
    rbs.reservation_lookup['rsv-00004'] = {'name': 'Dave', 'reserved_time': '17:45 05-12-2026', 'num_diners': 4, 'vip_status': False, 'tables': [5]}
    # Confirm successful call of check_time_conflict for new_time with a conflict against other reservation
    with self.assertRaises(ValueError, msg='New time with conflict against other reservation did not raise ValueError on isolated change with modify_reservation.'):
      rbs.modify_reservation('rsv-00001', new_time='18:00 05-12-2026')
    # Confirm updated 'reserve_time' in reservation_lookup with no other changes
    rbs.modify_reservation('rsv-00001', new_time='20:00 05-12-2026')    
    self.assertEqual(rbs.reservation_lookup['rsv-00001'], {'name': 'Mark', 'reserved_time': '20:00 05-12-2026', 'num_diners': 3, 'vip_status': True, 'tables': [5]}, 'Full reservation info does not match expected values after modifying rsv-00001 with new_time only.')
    # Check combinations of arguments with conditional dependencies
    # Combo 1: new_table_numbers + new_party_size
    # Confirm successful call of check_seating_capacity for new party size too large for capacity of new table numbers
    with self.assertRaises(ValueError, msg='New party size larger than new tables\' capacity did not raise ValueError on combo change with modify_reservation.'):
      rbs.modify_reservation('rsv-00001', new_table_numbers=[4], new_party_size=6)
    # Confirm updated 'tables' and 'num_diners' in reservation_lookup with no other changes
    rbs.modify_reservation('rsv-00002', new_table_numbers=[4, 1, 6], new_party_size=12)
    self.assertEqual(rbs.reservation_lookup['rsv-00002'], {'name': 'John Smith', 'reserved_time': '19:00 05-15-2026', 'num_diners': 12, 'vip_status': False, 'tables': [4, 1, 6]}, 'Full reservation info does not match expected values after modifying rsv-00002 with new_table_numbers and new_party_size.')
    # Confirm reservation ID removed from old tables reservation lists and added to new tables reservation lists with no other changes
    self.assertEqual(rbs.reservations, {1: ['rsv-00002'], 2: ['rsv-00003'], 3: [], 4: ['rsv-00002'], 5: ['rsv-00001', 'rsv-00004'], 6: ['rsv-00002'], 7: []}, 'Reservations dict does not match expected values after modifying rsv-00002 with new_table_numbers and new_party_size.')
    # Combo 2: new_table_numbers + new_time
    # Create another dummy reservation for time conflict check
    rbs.reservations[3] =  ['rsv-00005']
    rbs.reservation_lookup['rsv-00005'] = {'name': 'Marie Curie', 'reserved_time': '19:45 05-13-2026', 'num_diners': 4, 'vip_status': True, 'tables': [3]}
    # Confirm successful call of check_time_conflict for new table numbers and new time with a conflict against other reservation
    with self.assertRaises(ValueError, msg='New table number and new time with conflict against other reservation did not raise ValueError on combo change with modify_reservation.'):
      rbs.modify_reservation('rsv-00001', new_table_numbers=[3], new_time='19:00 05-13-2026')
    # Confirm updated 'tables' and 'reserved_time' in reservation_lookup with no other changes
    rbs.modify_reservation('rsv-00001', new_table_numbers=[3], new_time='18:30 05-13-2026')
    self.assertEqual(rbs.reservation_lookup['rsv-00001'], {'name': 'Mark', 'reserved_time': '18:30 05-13-2026', 'num_diners': 3, 'vip_status': True, 'tables': [3]}, 'Full reservation info does not match expected values after modifying rsv-00001 with new_table_numbers and new_time.')
    # Confirm reservation ID removed from old table's reservation list and added to new table's reservation list with no other changes
    self.assertEqual(rbs.reservations, {1: ['rsv-00002'], 2: ['rsv-00003'], 3: ['rsv-00005', 'rsv-00001'], 4: ['rsv-00002'], 5: [ 'rsv-00004'], 6: ['rsv-00002'], 7: []}, 'Reservations dict does not match expected values after modifying rsv-00001 with new_table_numbers and new_time.')
    # Combo 3: all three at once new_table_numbers + new_party_size + new_time
    # Confirm updated 'tables', 'num_diners', and 'reserved_time' in reservation_lookup with no other changes
    rbs.modify_reservation('rsv-00002', new_table_numbers=[7, 2], new_party_size=10, new_time='20:00 05-15-2026')
    self.assertEqual(rbs.reservation_lookup['rsv-00002'], {'name': 'John Smith', 'reserved_time': '20:00 05-15-2026', 'num_diners': 10, 'vip_status': False, 'tables': [7, 2]}, 'Full reservation info does not match expected values after modifying rsv-00002 with new_table_numbers, new_party_size, and new_time.')
    # Confirm reservation ID removed from old tables' reservation lists and added to new tables' reservation lists
    self.assertEqual(rbs.reservations, {1: [], 2: ['rsv-00003', 'rsv-00002'], 3: ['rsv-00005', 'rsv-00001'], 4: [], 5: ['rsv-00004'], 6: [], 7: ['rsv-00002']}, 'Reservations dict does not match expected values after modifying rsv-00002 with new_table_numbers, new_party_size, and new_time.')
    # Test change to all arguments simultaneously
    rbs.modify_reservation('rsv-00001', new_name='Mark Wise', new_table_numbers=[4], new_party_size=4, new_time='19:00 05-14-2026', new_vip_status=False)
    # Confirm all keys correctly updated in reservation_lookup
    self.assertEqual(rbs.reservation_lookup['rsv-00001'], {'name': 'Mark Wise', 'reserved_time': '19:00 05-14-2026', 'num_diners': 4, 'vip_status': False, 'tables': [4]}, 'Full reservation info does not match expected values after modifying rsv-00001 with all arguments.')
    # Full dict equality check for reservations
    self.assertEqual(rbs.reservations, {1: [], 2: ['rsv-00003', 'rsv-00002'], 3: ['rsv-00005'], 4: ['rsv-00001'], 5: ['rsv-00004'], 6: [], 7: ['rsv-00002']}, 'Full reservations dict does not match expected values after all reservation modifications.')
    # Full dict equality check for reservation_lookup
    self.assertEqual(rbs.reservation_lookup, {
      'rsv-00001': {'name': 'Mark Wise', 'reserved_time': '19:00 05-14-2026', 'num_diners': 4, 'vip_status': False, 'tables': [4]},
      'rsv-00002': {'name': 'John Smith', 'reserved_time': '20:00 05-15-2026', 'num_diners': 10, 'vip_status': False, 'tables': [7, 2]},
      'rsv-00003': {'name': 'Lisa', 'reserved_time': '19:00 05-15-2026', 'num_diners': 2, 'vip_status': False, 'tables': [2]},
      'rsv-00004': {'name': 'Dave', 'reserved_time': '17:45 05-12-2026', 'num_diners': 4, 'vip_status': False, 'tables': [5]},
      'rsv-00005': {'name': 'Marie Curie', 'reserved_time': '19:45 05-13-2026', 'num_diners': 4, 'vip_status': True, 'tables': [3]}
    }, 'Final reservation_lookup dict does not match expected values after all modifications.')

  # Test add_order_items function
  def test_add_order_items(self):
    # Create dummy table assignments and orders - one with no current order items and one with existing items already added
    rbs.Order.order_count = 2
    rbs.tables[1] = {'capacity': 2, 'status': 'occupied', 'name': 'Customer', 'vip_status': False, 'has_reservation': False, 'seating_time': '14:30 05-11-2026', 'num_diners': 2, 'order': {'ord_number': '00001', 'food_items': ['Tuna Sandwich', 'Turkey Club Sandwich'], 'drinks': ['Coca Cola', 'Sprite']}, 'total': None, 'linked_tables': []}
    rbs.tables[3] = {'capacity': 4, 'status': 'occupied', 'name': 'Customer', 'vip_status': False, 'has_reservation': False, 'seating_time': '15:00 05-11-2026', 'num_diners': 4, 'order': {'ord_number': '00002'}, 'total': None, 'linked_tables': []}
    # Check table number that has no order
    with self.assertRaises(LookupError, msg='Table number with no order did not raise LookupError when adding order items.'):
      rbs.add_order_items(5, food=['Spaghetti'], drinks=['Sparkling Water'])
    # Check non-list values for food and drinks
    with self.assertRaises(TypeError, msg='Non-list value for food did not raise TypeError when adding order items.'):
      rbs.add_order_items(1, food='Spaghetti', drinks=['Sparkling Water'])
    with self.assertRaises(TypeError, msg='Non-list value for drinks did not raise TypeError when adding order items.'):
      rbs.add_order_items(1, food=['Spaghetti'], drinks='Sparkling Water')
    # Check non-string food name in food list
    with self.assertRaises(TypeError, msg='Non-string value in food list did not raise TypeError when adding order items.'):
      rbs.add_order_items(1, food=[('Spaghetti',)])
    # Check food not on the menu
    with self.assertRaises(LookupError, msg='Non-existent food item did not raise LookupError when adding order items.'):
      rbs.add_order_items(1, food=['French Toast'])
    # Check non-string drink name in drinks list
    with self.assertRaises(TypeError, msg='Non-string value in drinks list did not raise TypeError when adding order items.'):
      rbs.add_order_items(1, drinks=[('Sparkling Water',)])
    # Check drink not on the menu
    with self.assertRaises(LookupError, msg='Non-existent drink item did not raise LookupError when adding order items.'):
      rbs.add_order_items(1, drinks=['Root Beer'])
    # Add food and drink items to an empty order
    rbs.add_order_items(3, food=['Spaghetti', 'Ham Sandwich', 'Salad', 'Chicken Fingers'], drinks=['Sparkling Water', 'Sparkling Water', 'Sprite', 'Grape Soda'])
    # Confirm updated order in the table's dict with no other changes
    self.assertEqual(rbs.tables[3], {
      'capacity': 4, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '15:00 05-11-2026', 
      'num_diners': 4, 
      'order': {'ord_number': '00002', 'food_items': ['Spaghetti', 'Ham Sandwich', 'Salad', 'Chicken Fingers'], 'drinks':['Sparkling Water', 'Sparkling Water', 'Sprite', 'Grape Soda']}, 
      'total': None, 
      'linked_tables': []},
      'Table 3 dictionary does not match expected values after adding food and drink items to empty order.')
    # Add additional items to an order with pre-existing foods and drinks
    rbs.add_order_items(1, food=['French Fries', 'Ice Cream'], drinks=['Sparkling Water'])
    # Confirm updated order in the table's dict with no other changes
    self.assertEqual(rbs.tables[1], {
      'capacity': 2, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '14:30 05-11-2026', 
      'num_diners': 2, 
      'order': {'ord_number': '00001', 'food_items': ['Tuna Sandwich', 'Turkey Club Sandwich', 'French Fries', 'Ice Cream'], 'drinks': ['Coca Cola', 'Sprite', 'Sparkling Water']}, 
      'total': None, 
      'linked_tables': []},
      'Table 1 dictionary does not match expected values after adding items to order with pre-existing foods and drinks.')
    # Check adding foods only
    rbs.add_order_items(3, food=['French Fries'])
    self.assertEqual(rbs.tables[3], {
      'capacity': 4, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '15:00 05-11-2026', 
      'num_diners': 4, 
      'order': {'ord_number': '00002', 'food_items': ['Spaghetti', 'Ham Sandwich', 'Salad', 'Chicken Fingers', 'French Fries'], 'drinks':['Sparkling Water', 'Sparkling Water', 'Sprite', 'Grape Soda']}, 
      'total': None, 
      'linked_tables': []},
      'Table 3 dictionary does not match expected values after adding food only to order.')
    # Check adding drinks only
    rbs.add_order_items(3, drinks=['Beer'])    
    self.assertEqual(rbs.tables[3], {
      'capacity': 4, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '15:00 05-11-2026', 
      'num_diners': 4, 
      'order': {'ord_number': '00002', 'food_items': ['Spaghetti', 'Ham Sandwich', 'Salad', 'Chicken Fingers', 'French Fries'], 'drinks':['Sparkling Water', 'Sparkling Water', 'Sprite', 'Grape Soda', 'Beer']}, 
      'total': None, 
      'linked_tables': []},
      'Table 3 dictionary does not match expected values after adding drink only to order.')
    # Full equality check of the tables dict to confirm no other tables modified incorrectly
    self.assertEqual(rbs.tables,{
       1: {
      'capacity': 2, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '14:30 05-11-2026', 
      'num_diners': 2, 
      'order': {'ord_number': '00001', 'food_items': ['Tuna Sandwich', 'Turkey Club Sandwich', 'French Fries', 'Ice Cream'], 'drinks': ['Coca Cola', 'Sprite', 'Sparkling Water']}, 
      'total': None, 
      'linked_tables': []},
       2: {'capacity': 2, 'status': 'available'},
       3: {
      'capacity': 4, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '15:00 05-11-2026', 
      'num_diners': 4, 
      'order': {'ord_number': '00002', 'food_items': ['Spaghetti', 'Ham Sandwich', 'Salad', 'Chicken Fingers', 'French Fries'], 'drinks':['Sparkling Water', 'Sparkling Water', 'Sprite', 'Grape Soda', 'Beer']}, 
      'total': None, 
      'linked_tables': []},
       4: {'capacity': 4, 'status': 'available'},
       5: {'capacity': 4, 'status': 'available'},
       6: {'capacity': 6, 'status': 'available'},
       7: {'capacity': 8, 'status': 'available'}
    }, 'Final tables dict does not match expected values after all order items added.')
  
  # Test remove_order_items function
  def test_remove_order_items(self):
    # Create dummy table assignments and orders - one with no current order items and one with existing items already added
    rbs.Order.order_count = 2
    rbs.tables[1] = {'capacity': 2, 'status': 'occupied', 'name': 'Customer', 'vip_status': False, 'has_reservation': False, 'seating_time': '14:30 05-11-2026', 'num_diners': 2, 'order': {'ord_number': '00001', 'food_items': ['Tuna Sandwich', 'Turkey Club Sandwich', 'French Fries', 'Ice Cream'], 'drinks': ['Coca Cola', 'Sprite', 'Sparkling Water']}, 'total': None, 'linked_tables': []}
    rbs.tables[3] = {'capacity': 4, 'status': 'occupied', 'name': 'Customer', 'vip_status': False, 'has_reservation': False, 'seating_time': '15:00 05-11-2026', 'num_diners': 4, 'order': {'ord_number': '00002'}, 'total': None, 'linked_tables': []}
    # Check table number that has no order
    with self.assertRaises(LookupError, msg='Table number with no order did not raise LookupError when removing order items.'):
      rbs.remove_order_items(5, food=['Spaghetti'], drinks=['Sparkling Water'])
    # Check removing food from order that has no foods to remove
    with self.assertRaises(LookupError, msg='Table number with no foods on the order did not raise LookupError when removing food items.'):
      rbs.remove_order_items(3, food=['Spaghetti'])
    # Check removing drink from order that has no drinks to remove
    with self.assertRaises(LookupError, msg='Table number with no drinks on the order did not raise LookupError when removing drink items.'):
      rbs.remove_order_items(3, drinks=['Sparkling Water'])
    # Check non-list values for food and drinks
    with self.assertRaises(TypeError, msg='Non-list value for food did not raise TypeError when removing order items.'):
      rbs.remove_order_items(1, food='Ice Cream', drinks=['Sparkling Water'])
    with self.assertRaises(TypeError, msg='Non-list value for drinks did not raise TypeError when removing order items.'):
      rbs.remove_order_items(1, food=['Ice Cream'], drinks='Sparkling Water')
    # Check non-string food name in food list
    with self.assertRaises(TypeError, msg='Non-string value in food list did not raise TypeError when removing order items.'):
      rbs.remove_order_items(1, food=[('Ice Cream',)])
    # Check non-string drink name in drinks list
    with self.assertRaises(TypeError, msg='Non-string value in drinks list did not raise TypeError when removing order items.'):
      rbs.remove_order_items(1, drinks=[('Sparkling Water',)])
    # Remove food and drink items from order, including some items that are not part of the order to confirm they are skipped cleanly without raising an error and the remaining items are removed
    rbs.remove_order_items(1, food=['French Fries', 'Spaghetti', 'Ice Cream'], drinks=['Grape Soda', 'Sparkling Water'])
    # Confirm updated order in the table's dict with no other changes
    self.assertEqual(rbs.tables[1], {
      'capacity': 2, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '14:30 05-11-2026', 
      'num_diners': 2, 
      'order': {'ord_number': '00001', 'food_items': ['Tuna Sandwich', 'Turkey Club Sandwich'], 'drinks': ['Coca Cola', 'Sprite']}, 
      'total': None, 
      'linked_tables': []},
      'Table 1 dictionary does not match expected values after removing food and drink items.')
    # Validate output message printed for the user when food or drink item not in the order gets skipped
    with patch('sys.stdout', new_callable=StringIO) as mock_out:
      rbs.remove_order_items(1, food=['Spaghetti'])
    self.assertIn('Cannot remove food ', mock_out.getvalue(), 'Removing food not on the order did not print output message.')
    with patch('sys.stdout', new_callable=StringIO) as mock_out:
      rbs.remove_order_items(1, drinks=['Grape Soda'])
    self.assertIn('Cannot remove drink ', mock_out.getvalue(), 'Removing drink not on the order did not print output message.')
    # Remove food only and check table's dict
    rbs.remove_order_items(1, food=['Tuna Sandwich'])
    self.assertEqual(rbs.tables[1], {
      'capacity': 2, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '14:30 05-11-2026', 
      'num_diners': 2, 
      'order': {'ord_number': '00001', 'food_items': ['Turkey Club Sandwich'], 'drinks': ['Coca Cola', 'Sprite']}, 
      'total': None, 
      'linked_tables': []},
      'Table 1 dictionary does not match expected values after removing food and drink items.')
    # Remove drinks only and check table's dict
    rbs.remove_order_items(1, drinks=['Sprite'])
    self.assertEqual(rbs.tables[1], {
      'capacity': 2, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '14:30 05-11-2026', 
      'num_diners': 2, 
      'order': {'ord_number': '00001', 'food_items': ['Turkey Club Sandwich'], 'drinks': ['Coca Cola']}, 
      'total': None, 
      'linked_tables': []},
      'Table 1 dictionary does not match expected values after removing food and drink items.')
    # Full equality check of the tables dict to confirm no other updates made incorrectly
    self.assertEqual(rbs.tables,{
       1: {
      'capacity': 2, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '14:30 05-11-2026', 
      'num_diners': 2, 
      'order': {'ord_number': '00001', 'food_items': ['Turkey Club Sandwich'], 'drinks': ['Coca Cola']}, 
      'total': None, 
      'linked_tables': []},
       2: {'capacity': 2, 'status': 'available'},
       3: {
      'capacity': 4, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '15:00 05-11-2026', 
      'num_diners': 4, 
      'order': {'ord_number': '00002'}, 
      'total': None, 
      'linked_tables': []},
       4: {'capacity': 4, 'status': 'available'},
       5: {'capacity': 4, 'status': 'available'},
       6: {'capacity': 6, 'status': 'available'},
       7: {'capacity': 8, 'status': 'available'}
    }, 'Final tables dict does not match expected values after all order items removed.')

  # test iterate_items
  def test_iterate_items(self):
    # Create table assignments with orders for testing
    rbs.Order.order_count = 3
    # Order with food and drinks
    rbs.tables[1] = {
      'capacity': 2, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '17:30 05-23-2026', 
      'num_diners': 2, 
      'order': {'ord_number': '00001', 'food_items': ['Tuna Sandwich', 'Turkey Club Sandwich'], 'drinks': ['Coca Cola', 'Sparkling Water']}, 
      'total': None, 
      'linked_tables': []}
    # Note the correct total for order 00001 should be 3.5 + 5.0 + 2.0 + 1.75 = 12.25 or $12.25
    # Order with food only
    rbs.tables[2] = {
      'capacity': 2, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '17:30 05-23-2026', 
      'num_diners': 2, 
      'order': {'ord_number': '00002', 'food_items': ['Tuna Sandwich', 'Turkey Club Sandwich']}, 
      'total': None, 
      'linked_tables': []}    
    # Note the correct total for order 00002 should be 3.5 + 5.0 = 8.5 or $8.50
    # Order with drinks only
    rbs.tables[3] = {
      'capacity': 4, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '17:30 05-23-2026', 
      'num_diners': 2, 
      'order': {'ord_number': '00003', 'drinks': ['Coca Cola', 'Sparkling Water']}, 
      'total': None, 
      'linked_tables': []}
    # Note the correct total for order 00003 should be 2.0 + 1.75 = 3.75 or $3.75
    # Check correct total returned with the 'add' operation
    # Both food and drinks
    self.assertEqual(rbs.iterate_items(1, 'add'), 12.25, 'iterate_items add operation did not return correct total for order with food and drinks.')
    # Foods only
    self.assertEqual(rbs.iterate_items(2, 'add'), 8.5, 'iterate_items add operation did not return correct total for order with food only.')
    # Drinks only
    self.assertEqual(rbs.iterate_items(3, 'add'), 3.75, 'iterate_items add operation did not return correct total for order with drinks only.')
    # Check correct item name and price printing with the 'print' operation
    # Both food and drinks
    with patch('sys.stdout', new_callable=StringIO) as mock_out:
      rbs.iterate_items(1, 'print')
    self.assertIn(f'{'Tuna Sandwich':<25}{f'{3.50:.2f}':>10}', mock_out.getvalue(), 'iterate_items print operation did not correctly print first food item name and price for order with food and drinks.')
    self.assertIn(f'{'Turkey Club Sandwich':<25}{f'{5.00:.2f}':>10}', mock_out.getvalue(), 'iterate_items print operation did not correctly print second food item name and price for order with food and drinks.')    
    self.assertIn(f'{'Coca Cola':<25}{f'{2.00:.2f}':>10}', mock_out.getvalue(), 'iterate_items print operation did not correctly print first drink item name and price for order with food and drinks.')
    self.assertIn(f'{'Sparkling Water':<25}{f'{1.75:.2f}':>10}', mock_out.getvalue(), 'iterate_items print operation did not correctly print second drink item name and price for order with food and drinks.')
    # Foods only
    with patch('sys.stdout', new_callable=StringIO) as mock_out:
      rbs.iterate_items(2, 'print')
    self.assertIn(f'{'Tuna Sandwich':<25}{f'{3.50:.2f}':>10}', mock_out.getvalue(), 'iterate_items print operation did not correctly print first food item name and price for food-only order.')
    self.assertIn(f'{'Turkey Club Sandwich':<25}{f'{5.00:.2f}':>10}', mock_out.getvalue(), 'iterate_items print operation did not correctly print second food item name and price for food-only order.')
    # Drinks only
    with patch('sys.stdout', new_callable=StringIO) as mock_out:
      rbs.iterate_items(3, 'print')
    self.assertIn(f'{'Coca Cola':<25}{f'{2.00:.2f}':>10}', mock_out.getvalue(), 'iterate_items print operation did not correctly print first drink item name and price for drinks-only order.')
    self.assertIn(f'{'Sparkling Water':<25}{f'{1.75:.2f}':>10}', mock_out.getvalue(), 'iterate_items print operation did not correctly print second drink item name and price for drinks-only order.')

  # test calc_total
  def test_calc_total(self):
    # Create table assignment with order and items
    rbs.Order.order_count = 2
    rbs.tables[1] = {
      'capacity': 2, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '17:30 05-23-2026', 
      'num_diners': 2, 
      'order': {'ord_number': '00001', 'food_items': ['Tuna Sandwich', 'Turkey Club Sandwich'], 'drinks': ['Coca Cola', 'Sparkling Water']}, 
      'total': None, 
      'linked_tables': []}
    # Note the correct total for this order should be 3.5 + 5.0 + 2.0 + 1.75 = 12.25 or $12.25
    # Create table assignment with an order but no items added
    rbs.tables[3] = {
      'capacity': 4, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '17:45 05-23-2026', 
      'num_diners': 4, 
      'order': {'ord_number': '00002'}, 
      'total': None, 
      'linked_tables': []}
    # Check non-exist
    # Confirm error returned for table number with no order
    with self.assertRaises(LookupError, msg='calc_total did not raise LookupError for table number with no order.'):
      rbs.calc_total(4)
    # Confirm error returned for table number whose order has no items
    with self.assertRaises(LookupError, msg='calc_total did not raise LookupError for table number whose order has no items.'):
      rbs.calc_total(3)
    # Run calc_total on the order and set equal to a variable
    test_total = rbs.calc_total(1)
    # Confirm correct total returned
    self.assertEqual(test_total, Decimal('12.25'), 'calc_total did not return correct total.')
    # Confirm value of 'total' key correctly updated in the table's dict
    self.assertEqual(rbs.tables[1]['total'], '$12.25', 'Table 1 total not correctly updated in tables dict with value from calc_total.')
    # Full tables dict equality check to confirm nothing else updated in error
    self.assertEqual(rbs.tables, {
    1: {
      'capacity': 2, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '17:30 05-23-2026', 
      'num_diners': 2, 
      'order': {'ord_number': '00001', 'food_items': ['Tuna Sandwich', 'Turkey Club Sandwich'], 'drinks': ['Coca Cola', 'Sparkling Water']}, 
      'total': '$12.25', 
      'linked_tables': []},
    2: {
      'capacity': 2, 
      'status': 'available'},
    3: {
      'capacity': 4, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '17:45 05-23-2026', 
      'num_diners': 4, 
      'order': {'ord_number': '00002'}, 
      'total': None, 
      'linked_tables': []},
    4: {
      'capacity': 4, 
      'status': 'available'},
    5: {
      'capacity': 4, 
      'status': 'available'},
    6: {
      'capacity': 6, 
      'status': 'available'},
    7: {
      'capacity': 8, 
      'status': 'available'}
    }, 'Full tables dict does not match expected values after running calc_total.')

  # test print_bill for single payor
  def test_print_bill(self):    
    # Create table assignment with order and items
    rbs.Order.order_count = 1
    rbs.tables[1] = {
      'capacity': 2, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '17:30 05-23-2026', 
      'num_diners': 2, 
      'order': {'ord_number': '00001', 'food_items': ['Tuna Sandwich', 'Turkey Club Sandwich'], 'drinks': ['Coca Cola', 'Sparkling Water']}, 
      'total': None, 
      'linked_tables': []}
    # Note the correct total for this order should be 3.5 + 5.0 + 2.0 + 1.75 = 12.25 or $12.25
    # Check validations for split argument
    with self.assertRaises(TypeError, msg='Non-integer split did not raise TypeError for printing bill.'):
      rbs.print_bill(1, '2')
    with self.assertRaises(ValueError, msg='Non-positive integer split did not raise ValueError for printing bill.'):
      rbs.print_bill(1, 0)
    # Check printing single bill with split=1    
    with patch('sys.stdout', new_callable=StringIO) as mock_out:
      rbs.print_bill(1, split=1)
    # Confirm order number printed
    self.assertIn('Order Number: 00001', mock_out.getvalue(), 'Order number did not print correctly on the bill bill.')
    # Confirm sub-total text and amount printed
    self.assertIn(f'{'Sub-total:':<25}{'$12.25':>10}', mock_out.getvalue(), 'Sub-total text did not print correctly on unsplit bill.')
    # Confirm split price line DID NOT print on unsplit bill
    self.assertNotIn(f'{'Your amount:':<25}{'$12.25':>10}', mock_out.getvalue(), 'Split price line incorrectly printed for split=1.')
    # Confirm tip text printed with line for customer to write-in amount
    self.assertIn(f'{'Tip:':<25}__________', mock_out.getvalue(), 'Tip line did not print correctly on unsplit bill.')
    # Confirm final total text printed with line for customer to write-in amount
    self.assertIn(f'{'Total:':<25}__________', mock_out.getvalue(), 'Total line did not print correctly on unsplit bill.')
    # Confirm no split entered defaults to 1 and prints identically
    with patch('sys.stdout', new_callable=StringIO) as mock_out_default:
      rbs.print_bill(1)
    self.assertEqual(mock_out_default.getvalue(), mock_out.getvalue(), 'Unspecified split did not correctly default to 1 and print identical bill.')
    # Check printing split bill
    with patch('sys.stdout', new_callable=StringIO) as mock_out_split:
      rbs.print_bill(1, split=2)
    # Confirm the split_price line printed correctly
    self.assertIn(f'{'Your amount:':<25}{'$6.13':>10}', mock_out_split.getvalue(), 'Split price text and amount did not princt correctly.')
    # Confirm bill printed exactly twice
    self.assertEqual(mock_out_split.getvalue().count(f'{'Your amount:':<25}{'$6.13':>10}'), 2)

  def test_clear_tables(self):
    rbs.Order.order_count = 5
    rbs.tables = {
       1: {
      'capacity': 2, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '14:30 05-22-2026', 
      'num_diners': 2, 
      'order': {'ord_number': '00001', 'food_items': ['Tuna Sandwich', 'Turkey Club Sandwich'], 'drinks': ['Coca Cola', 'Sprite']}, 
      'total': None, 
      'linked_tables': []},
       2: {
      'capacity': 2, 
      'status': 'occupied',
      'name': 'Joe Thomas', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '15:30 05-22-2026', 
      'num_diners': 2, 
      'order': {'ord_number': '00005', 'food_items': ['Tuna Sandwich', 'Turkey Club Sandwich'], 'drinks': ['Coca Cola', 'Sprite']}, 
      'total': None, 
      'linked_tables': []},
       3: {
      'capacity': 4, 
      'status': 'occupied', 
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '15:00 05-22-2026', 
      'num_diners': 4, 
      'order': {'ord_number': '00002'}, 
      'total': None, 
      'linked_tables': []},
       4: {
      'capacity': 4, 
      'status': 'occupied',
      'name': 'Customer', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '15:20 05-22-2026', 
      'num_diners': 3, 
      'order': {'ord_number': '00004', 'food_items': ['Tuna Sandwich', 'Turkey Club Sandwich', 'Chicken Fingers'], 'drinks': ['Coca Cola', 'Sprite', 'Apple Juice']}, 
      'total': None, 
      'linked_tables': []},
       5: {
      'capacity': 4, 
      'status': 'occupied',
      'name': 'Roger', 
      'vip_status': False, 
      'has_reservation': True, 
      'seating_time': '15:00 05-22-2026', 
      'num_diners': 18, 
      'order': {'ord_number': '00003'}, 
      'total': None, 
      'linked_tables': [6, 7]},
       6: {'capacity': 6, 'status': 'occupied', 'linked_tables': [5, 7]},
       7: {'capacity': 8, 'status': 'occupied', 'linked_tables': [5, 6]}
    }
    # Check non-integer table number input
    with self.assertRaises(TypeError, msg='Non-integer table number did not raise TypeError when clearing tables.'):
      rbs.clear_tables('one', 3)
    # Check non-existent table number prints message and skips without error and remaining table(s) cleared with message printed
    with patch('sys.stdout', new_callable=StringIO) as mock_out:
      rbs.clear_tables(10, 3)
    self.assertIn('There is no table number 10', mock_out.getvalue(), 'Non-existent table number did not print message correctly when clearing tables.')
    self.assertEqual(rbs.tables[3], {'capacity': 4, 'status': 'available'}, 'Non-existent table number in clear_tables did not skip and clear remaining table.')
    self.assertIn('Table number 3 has been cleared', mock_out.getvalue(), 'Table cleared after non-existent table skipped did not print message.')
    # Check already empty table number prints message and skips without error and remaining table(s) cleared with message printed
    with patch('sys.stdout', new_callable=StringIO) as mock_out:
      rbs.clear_tables(3, 1)
    self.assertIn('Table number 3 is already empty', mock_out.getvalue(), 'Already empty table number did not print message correctly when clearing tables.')    
    self.assertEqual(rbs.tables[1], {'capacity': 2, 'status': 'available'}, 'Already empty table number in clear_tables did not skip and clear remaining table.')
    self.assertIn('Table number 1 has been cleared', mock_out.getvalue(), 'Table cleared after empty table skipped did not print message.')
    # Confirm successful clear of multiple non-linked tables
    rbs.clear_tables(2, 4)
    self.assertEqual(rbs.tables[2], {'capacity': 2, 'status': 'available'}, 'First table number not cleared correctly when clearing two non-linked tables.')
    self.assertEqual(rbs.tables[4], {'capacity': 4, 'status': 'available'}, 'Second table not cleared correctly when clearing two non-linked tables.')
    # Check full state of tables dict after all non-linked tables cleared
    self.assertEqual(rbs.tables, {
      1: {'capacity': 2, 'status': 'available'},
      2: {'capacity': 2, 'status': 'available'},
      3: {'capacity': 4, 'status': 'available'},
      4: {'capacity': 4, 'status': 'available'},
      5: {
      'capacity': 4, 
      'status': 'occupied',
      'name': 'Roger', 
      'vip_status': False, 
      'has_reservation': True, 
      'seating_time': '15:00 05-22-2026', 
      'num_diners': 18, 
      'order': {'ord_number': '00003'}, 
      'total': None, 
      'linked_tables': [6, 7]},
      6: {'capacity': 6, 'status': 'occupied', 'linked_tables': [5, 7]},
      7: {'capacity': 8, 'status': 'occupied', 'linked_tables': [5, 6]}
      }, 'Full tables dict does not match expected values after non-linked tables cleared.')
    # Confirm linked tables successfully cleared from primary table number and message printed for each table.
    with patch('sys.stdout', new_callable=StringIO) as mock_out:
      rbs.clear_tables(5)
    self.assertEqual(rbs.tables[5], {'capacity': 4, 'status': 'available'}, 'Primary table number 5 not cleared correctly when clearing linked tables from primary table number.')
    self.assertIn('Table number 5 has been cleared', mock_out.getvalue(), 'First table cleared did not print message when clearing linked tables.')
    self.assertEqual(rbs.tables[6], {'capacity': 6, 'status': 'available'}, 'Linked table number 6 not cleared correctly when clearing linked tables from primary table number.')
    self.assertIn('Linked table 6 has been cleared', mock_out.getvalue(), 'First linked table did not print message when clearing linked tables.')
    self.assertEqual(rbs.tables[7], {'capacity': 8, 'status': 'available'}, 'Linked table number 7 not cleared correctly when clearing linked tables.')
    self.assertIn('Linked table 7 has been cleared', mock_out.getvalue(), 'Second linked table did not print message when clearing linked tables from primary table number.')
    # Check full tables dict and confirm all tables cleared and available
    self.assertEqual(rbs.tables, {
      1: {'capacity': 2, 'status': 'available'},
      2: {'capacity': 2, 'status': 'available'},
      3: {'capacity': 4, 'status': 'available'},
      4: {'capacity': 4, 'status': 'available'},
      5: {'capacity': 4, 'status': 'available'},
      6: {'capacity': 6, 'status': 'available'},
      7: {'capacity': 8, 'status': 'available'}
    }, 'Full table dict does not match expected values after all tables cleared.')
    # Create new mock table assignments for more linked tables
    rbs.Order.order_count = 6
    rbs.tables = {
       1: {
      'capacity': 2, 
      'status': 'occupied', 
      'name': 'Mark', 
      'vip_status': False, 
      'has_reservation': False, 
      'seating_time': '15:45 05-22-2026', 
      'num_diners': 6, 
      'order': {'ord_number': '00006', 'food_items': ['Tuna Sandwich', 'Turkey Club Sandwich'], 'drinks': ['Coca Cola', 'Sprite']}, 
      'total': None, 
      'linked_tables': [3]},
       2: {'capacity': 2, 'status': 'available'},
       3: {
      'capacity': 4, 
      'status': 'occupied',      
      'linked_tables': [1]},
       4: {'capacity': 4, 'status': 'available'},
       5: {'capacity': 4, 'status': 'available'},
       6: {'capacity': 6, 'status': 'available'},
       7: {'capacity': 8, 'status': 'available'}
    }
    # Confirm linked table numbers successfully cleared from just linked table number.
    rbs.clear_tables(3)
    self.assertEqual(rbs.tables[1], {'capacity': 2, 'status': 'available'}, 'Primary table 1 not cleared correctly when clearing linked tables from a linked table number.')
    self.assertEqual(rbs.tables[3], {'capacity': 4, 'status': 'available'}, 'Linked table 3 not cleared correctly when clearing linked tables from a linked table number.')
    # Final full tables dict equality check
    self.assertEqual(rbs.tables, {
      1: {'capacity': 2, 'status': 'available'},
      2: {'capacity': 2, 'status': 'available'},
      3: {'capacity': 4, 'status': 'available'},
      4: {'capacity': 4, 'status': 'available'},
      5: {'capacity': 4, 'status': 'available'},
      6: {'capacity': 6, 'status': 'available'},
      7: {'capacity': 8, 'status': 'available'}
    }, 'Full table dict does not match expected values after clearing linked tables using linked table number.') 

  # tear down test fixture by wiping slate clean again and saving to the JSON to keep the file clear of any table assignments and reservations created and saved to the file by the tests
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