import unittest
import Restaurant_Business_Software as rbs
from datetime import datetime, timezone, timedelta
import json, os

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
    # Check that a different table number was not modified
    self.assertEqual(rbs.tables[2]['status'], 'available', 'Other table number 2 status set to \'occupied\'.')
    self.assertNotIn('name', rbs.tables[5], 'Other table number 5 has a \'name\' key.')
  
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
    # Check that a different table number was not modified
    self.assertEqual(rbs.tables[2]['status'], 'available', 'Other table number 2 status set to \'occupied\'.')
    self.assertNotIn('name', rbs.tables[5], 'Other table number 5 has a \'name\' key.')

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
    self.assertEqual(rbs.tables[1], {'capacity': 2, 'status': 'available'}, 'Tables dict entry for table 6 was incorrectly modified by add_reservation with combined tables.')
    self.assertEqual(rbs.tables[5], {'capacity': 4, 'status': 'available'}, 'Tables dict entry for table 6 was incorrectly modified by add_reservation with combined tables.')

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
