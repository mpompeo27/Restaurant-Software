from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP

import json, os

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'restaurant_data.json')

tables = {}

reservations = {}

reservation_lookup = {}

menu = {}

max_capacity = 0

# Create function to load data from our json file
def load_data():
  global max_capacity
  # Validate the path for the database file
  if os.path.exists(DB_FILE):
    try:
      # Open the database file and load the data from the json
      with open(DB_FILE, 'r') as db:
        data = json.load(db)
      # Restore global state
      tables.update({int(k): v for k, v in data['tables'].items()}) # repopulate tables dict
      for t in tables:
        max_capacity += tables[t]['capacity']
      reservations.update({int(k): v for k, v in data['reservations'].items()})
      reservation_lookup.update(data['reservation_lookup'])
      Order.order_count = data['order_count']
      Reservation.reservation_count = data['reservation_count']
      menu.update(data['menu'])
    except PermissionError:
      print(f"Error: Permission denied when reading '{DB_FILE}'.")
    except json.JSONDecodeError:
      print(f"Error: '{DB_FILE}' is corrupted or not valid JSON. Starting with empty data.")
    except KeyError as e:
      print(f"Error: Expected key {e} not found in '{DB_FILE}'. The file may be from an incompatible version. Starting with empty data.")

# Create function to save data to our json file
def save_data():
  # Assign data to a dictionary that matches the json file.
  data = {
    'tables': tables,
    'reservations': reservations,
    'reservation_lookup': reservation_lookup,
    'order_count': Order.order_count,
    'reservation_count': Reservation.reservation_count,
    'menu': menu
  }
  # open the database file and write the updated data, with formatting
  with open(DB_FILE, 'w') as db:
    json.dump(data, db, indent=2)

# Create function to handle repeated validation checks of common function parameter inputs and reduce repeated if statements and error returns elsewhere in the code. It will take in a variable number of parameters with ** and use a nested function to check each of those parameters individually.
def validate_params(**params):
  # Nested function to take in the name and value for an individual parameter and run an appropriate check on the value based on the name.
  def check_param(name, value):
    if name == 'table_number':
      # Confirm table number is an integer and it exists in the tables dict. 
      if not isinstance(value, int):
        raise TypeError(f"Invalid table number \'{value}\'. Must be an integer number.")
      if value not in tables:
        raise ValueError(f"There is no table number {value}!")
    elif name == 'table_numbers':
      # Confirm at least one table number was entered
      if not value:
        raise ValueError("At least one table number must be provided.")
      # Check each table in the tuple for integer value that exists in the tables dict
      for table in value:
        # Confirm table number is an integer and it exists in the tables dict. 
        if not isinstance(table, int):
          raise TypeError(f"Invalid table number \'{table}\'. Must be an integer number.")
        if table not in tables:
          raise ValueError(f"There is no table number {table}!")
    elif name == 'name':
      # Confirm name is a string.
      if not isinstance(value, str):
        raise TypeError(f"Invalid name {value}. Must be a string.")      
    elif name == 'vip_status':
      # Confirm vip_status is a boolean.
      if not isinstance(value, bool):
        raise TypeError(f"Invalid VIP status {value}. Must be True or False.")
    elif name == 'reserve_status':
      # Confirm reservation status is a boolean.
      if not isinstance(value, bool):
        raise TypeError(f"Invalid reservation status {value}. Must be True or False.")
    elif name == 'time':
      # Confirm time is a string
      if not isinstance(value, str):
        raise TypeError(f"Invalid seating time {value}. Time must be a string formatted as HH:MM mm-dd-yyyy (e.g. '14:30 03-20-2026').")
      # Validate time string formatted correctly as 24 hr time and date HH:MM mm-dd-yyyy.
      try:
        datetime.strptime(value, '%H:%M %m-%d-%Y')
      except ValueError:
        raise ValueError("Seating time must be formatted as HH:MM mm-dd-yyyy (e.g. '14:30 03-20-2026').")
    elif name == 'party_size':
      # Confirm party_size is an integer and non-boolean.
      if (not isinstance(value, int)) or isinstance(value, bool):
        raise TypeError(f"Invalid party size \'{value}\'. Must be a positive integer.")
      # Confirm integer value is positive      
      if value <= 0:
        raise ValueError(f"Invalid party size {value}. Must be a positive integer.")
      # Check edge case for party_size greater than maximum capacity.
      if value > max_capacity:
        raise ValueError(f"Invalid party size. {value} exceeds maximum restaurant capacity of {max_capacity} persons.")
    elif name == 'tip':
      # Confirm tip is a number and non-boolean.
      if (not isinstance(value, (int, float))) or isinstance(value, bool):
        raise TypeError(f"\'{value}\' is not a valid tip amount. Must be a number.")
      # Confirm tip is a non-negative number.
      if value < 0:
        raise ValueError(f"\'{value}\' is not a valid tip amount. Cannot be a negative number.")
    elif name == 'tips':
      # Confirm at least one tip amount was entered
      if not value:
        raise ValueError("At least one tip amount must be provided.")
      # Confirm each tip in the tuple is a non-negative number.
      for tip in value:
        if (not isinstance(tip, (int, float))) or isinstance(tip, bool):
            raise TypeError(f"\'{tip}\' is not a valid tip amount. Must be a non-negative number.")
        if tip < 0:
            raise ValueError(f"{tip} is not a valid tip amount. Must be a non-negative number.")
    else:
      # Final error if there is an invalid parameter entirely.
      raise ValueError(f"{name} is not a valid parameter.")
  
  # Iterate through items in **params and call check_param for each one.
  for param_name, param_value in params.items():
    check_param(param_name, param_value)

# Create an Order class for generating a unique order number using a class variable order_count to ensure the counter is not modified elsewhere in the code outside the class constructor.
class Order:
  # Create the class variable for order count.  
  order_count = 0

  # Create a class constructor to increment the order count and create a unique string for the order number padded with leading zeros to at least 5 digits. 
  def __init__(self):
    Order.order_count += 1
    self.order_number = str(Order.order_count).zfill(5)
    if Order.order_count == (602 * 10**21):
      print("Congratulations! You've just reached 1 mol of orders! Wow! You're the most popular and successful restaurant in the universe!")

# Define a function to assign tables that will take variable *table_numbers to accommodate combining tables, the guest name, the size of the party, whether they have VIP status, if they have a reservation, and the time of their seating. If unspecified, name will default to 'Customer', VIP status and reservation will default to false and seating time will default to None before being set inside the function to the current time in UTC-6.
def assign_table(*table_numbers, name='Customer', party_size, vip_status=False, reserve_status=False, time=None): 
  # Set the actual default value for time to the current time.
  if time is None:
    time = datetime.now(timezone(timedelta(hours=-6))).strftime('%H:%M %m-%d-%Y')
  # Force blank name entries '' or '    ' to the default value 'Customer'
  if not name.strip():
    name = 'Customer'
  # Call the validate_params function to run standard checks.
  validate_params(table_numbers=table_numbers, name=name, party_size=party_size, vip_status=vip_status, reserve_status=reserve_status, time=time)
  # Initialize datetime object from the time argument before entering loop. Value remains constant and does not need to be repeated on each loop iteration.
  time_obj = datetime.strptime(time, '%H:%M %m-%d-%Y')
  # Initialize variable for the combined capacity of all tables.
  combined_capacity = 0
  # Iterate through table numbers to check each one's status and compare seating time to upcoming reservations.
  for table_number in table_numbers:
    # Check if table is already occupied.
    if tables[table_number]['status'] == 'occupied':
      raise ValueError(f"Table {table_number} is currently occupied.")   
    # If table is being assigned without a reservation, check the seating time against existing reservations to make sure there is no conflict with an upcoming reservation within 1 hour for which the table needs to remain open. This check is not needed if the table is being assigned from a reservation because the reservation system already checks to ensure reservations for a given table are sufficiently spaced out.
    if reserve_status == False:      
      for r in reservations[table_number]:
        existing_time = datetime.strptime(reservation_lookup[r]['time'], '%H:%M %m-%d-%Y')
        if timedelta(0) < (existing_time - time_obj) < timedelta(hours=1):
          raise ValueError(f"Table {table_number} has an upcoming reservation at {reservation_lookup[r]['time']} and cannot be seated. Table must remain open for the reservation.")
    # If no errors raised for the table status being occupied or time conflict with a reservation, add the table's capacity to combined_capacity
    combined_capacity += tables[table_number]['capacity']
  # Check the size of the party against the combined capacity of tables given.
  if party_size > combined_capacity:
    raise ValueError(f"Party size {party_size} is too large for table(s) {', '.join(str(t) for t in table_numbers)}. Seating capacity is only {combined_capacity}.")
  # If all validation checks are passed, select first table number as the primary for the party.
  primary_num = table_numbers[0]
  primary_table = tables[primary_num] # assign the primary table's dictionary to a reference variable for improved readability on repeated calls below
  primary_table['name'] = name
  primary_table['vip_status'] = vip_status
  primary_table['reservation'] = reserve_status
  primary_table['seating_time'] = time
  primary_table['num_diners'] = party_size
  new_order = Order()
  primary_table['order'] = {'ord_number': new_order.order_number}
  primary_table['total'] = None
  # Check if only 1 table and if yes, set primary table's status to occupied and set 'linked_tables' key to an empty list
  if len(table_numbers) == 1:
    primary_table['status'] = 'occupied'
    primary_table['linked_tables'] = []
  # Otherwise iterate through table_numbers to set all statuses to 'occupied' and create data linkage between the combined tables 
  else:
    for table_number in table_numbers:
      tables[table_number]['status'] = 'occupied'
      # Use list comprehension to set the table's 'linked_tables' key to a list of only the other table numbers
      tables[table_number]['linked_tables'] = [t for t in table_numbers if t != table_number]
  save_data()

# Function to assign food and drink items to the order for a specific table, taking in the table number and the ordered items with **kwargs used to allow for variable keyword arguments for food and drinks separately. Items must be provided in a list format.
def add_order_items(table_number, **order_items):
  # Validate table number.
  validate_params(table_number=table_number)
  # Validate order items provided in list form.
  if not all(isinstance(v, list) for v in order_items.values()):
    raise TypeError("All order items must be provided in separate lists for food and drinks.")
  # assign the table's order info from the tables dict to a reference variable for improved readability on subsequent calls
  try:
    order = tables[table_number]['order']
  # Raise an error if no order found for the given table
  except LookupError:
    raise LookupError(f"No order found for table {table_number}.")
  # Check if there is food in the order and if yes assign the 'food' parameter to a variable called 'foods'.
  if 'food' in order_items:
    foods = order_items.get('food')
    # Check that all items in the foods list are strings. Return ValueError if not.
    if not all(isinstance(item, str) for item in foods):
      raise TypeError("All food items must be strings.")
    # Check that all items in foods are on the menu. Return LookupError if not.
    if not all(item in menu['foods'] for item in foods):
      raise LookupError("One or more food items are not on the menu.")
    # If all items in foods are properly entered as strings and on the menu, proceed to add to the order.
    # Validate if order already has food items and append to the list if yes.
    if 'food_items' in order:
      for f in foods:
        order['food_items'].append(f)
    # Otherwise create the 'food_items' key for this order and set it equal to the list of foods.
    else:
      order['food_items'] = foods
  # Repeat the same for drinks.
  if 'drinks' in order_items:
    drinks = order_items.get('drinks')
    if not all(isinstance(item, str) for item in drinks):
      raise TypeError("All drinks must be strings.")
    if not all(item in menu['drinks'] for item in drinks):
      raise LookupError("One or more drinks are not on the menu.")
    if 'drinks' in order:
      for d in drinks:
        order['drinks'].append(d)
    else:
      order['drinks'] = drinks
  save_data()
      
# Function to remove food and drink items from a table's order in the case of mistakes, taking in the table number and the items to remove with **kwargs used to allow for variable keyword arguments for food and drinks separately. Items must be provided in a list format.
def remove_order_items(table_number, **removed_items):
  # Validate table number.
  validate_params(table_number=table_number)
  # Validate order items provided in list form.
  if not all(isinstance(v, list) for v in removed_items.values()):
    raise TypeError("All items to remove must be provided in separate lists for food and drinks.")  
  # Check if there is food in the removed items. If yes, assign the 'food' argument to a variable called 'remove_foods'.
  if 'food' in removed_items:
    remove_foods = removed_items.get('food')
    # Check that all items in the removed foods list are strings. Return ValueError if not, otherwise remove foods from the order in the tables dictionary.
    if not all(isinstance(item, str) for item in remove_foods):
      raise TypeError("All food items must be strings.")
    else:
      for food in remove_foods:
        if food not in tables[table_number]['order']['food_items']:
          print(f"Cannot remove food {food} because it is not in the order.")
        else:
          tables[table_number]['order']['food_items'].remove(food)
  # Repeat the same for drinks.
  if 'drinks' in removed_items:  
    remove_drinks = removed_items.get('drinks')  
    if not all(isinstance(item, str) for item in remove_drinks):
      raise TypeError("All drinks must be strings.")   
    else:
      for drink in remove_drinks:
        if drink not in tables[table_number]['order']['drinks']:
          print(f"Cannot remove drink {drink} because it is not in the order.")
        else:
          tables[table_number]['order']['drinks'].remove(drink)
  save_data()

# Function that will take in the table number and an operation - either 'add' or 'print' - to iterate through items in the table's order and either sum the prices to get the total or print them all with formatting for the bill.
def iterate_items(table_number, op):
  # Store the table's order info in a variable to visually clean up repeated calls below
  order = tables[table_number]['order']
  if op == 'add':
    # Initialize total to 0.
    total = Decimal(0)
    # Check if the table's order has food, and if yes, iterate through the food_items and add each one's price to the total.
    if 'food_items' in order:
      for food in order['food_items']:
        item_price = menu['foods'][food]
        total += Decimal(item_price)
    # Repeat for drinks.
    if 'drinks' in order:
      for drink in order['drinks']:
        item_price = menu['drinks'][drink]
        total += Decimal(item_price)
    return total
  elif op == 'print':
    if 'food_items' in order:
      for food in order['food_items']:
        item_price = menu['foods'][food]
        print(f"{food:<25}{f'{item_price:.2f}':>10}")
    # Repeat for drinks.
    if 'drinks' in order:
      for drink in order['drinks']:
        item_price = menu['drinks'][drink]
        print(f"{drink:<25}{f'{item_price:.2f}':>10}")

# Function to calculate the total bill for a table, taking in just the table number as an argument.
def calc_total(table_number):
  # Validate table number.
  validate_params(table_number=table_number)
  # Check that the table has any order at all.
  if not any(key in tables[table_number]['order'] for key in ('food_items', 'drinks')):
    raise LookupError(f"Table {table_number} has no order items to calculate the total.")
  # Get total using iterate_items with the 'add' op.
  total = iterate_items(table_number, 'add')
  tables[table_number]['total'] = "$" + str(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
  save_data()
  return total

# Function to print the table's bill. Takes in the table number and optional number of payors splitting the bill (defaulted to 1), prints the order number at the top, the list of order items and prices, the sub total, per-person split if needed, and then blank lines for the customer to write in their tip and final total.
def print_bill(table_number, split=1):
  validate_params(table_number=table_number)
  # Validate the value of the split parameter if not defaulted.
  if not isinstance(split, int):
    raise TypeError(f"Number of people splitting the bill must be a positive integer.")
  if split <= 0:
    raise ValueError(f"Number of people splitting the bill must be a positive integer.")
  # Calculate the sub-total of the order items before tip is added
  sub_total = calc_total(table_number).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
  # Calculate the split_price outside the print loop
  split_price = (sub_total / split).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
  # Print the bill n times for the number of people splitting the bill
  for n in range(split):
    # Print the order number at the top of the bill.
    print(f"Order Number: {tables[table_number]['order']['ord_number']}\n")
    iterate_items(table_number, 'print')    
    # Print messages for the order total, tip, and total bill.
    print(f"\n{'Order:':<25}{f'${sub_total}':>10}")
    # Check if bill is being split multiple ways
    if split > 1:
      # If yes, print a line with the individual split amount before the tip line
      print(f"{f'Your amount:':<25}{f'${split_price}':>10}")
    print(f"{f'Tip:':<25}__________")
    print(f"{'Total:':<25}__________\n")

# Create Reservation class for generating unique reservation IDs using a class variable reservation_count to ensure the counter is not modified elsewhere in the code outside the class constructor.
class Reservation:
  # Create the class variable for reservation count.  
  reservation_count = 0

  # Create a class constructor to increment the reservation count and create a unique string for the reservation ID. 
  def __init__(self):
    # Check the size of reservation count and reset to zero when about to reach 100k
    if Reservation.reservation_count >= 99999:
      Reservation.reservation_count = 0
      print('Reservation max reached. Reservation ID counter reset.')
    # Increment reservation count and create unique reservation ID string
    Reservation.reservation_count += 1
    self.ID = 'rsv-' + str(Reservation.reservation_count).zfill(5)

# Function to add a reservation to the reservations queue. It will take in the table number, the time of the reservation, the customer name, and their VIP status and create a Reservation class object to generate a reservation ID. If not specified, VIP status will default to False. The reservation ID will be added to the reservations dictionary in a list for the designated table, and the reservation info details will be added to the reservation_lookup dictionary under the reservation number. A message will print confirming the reservation was made successfully.
def add_reservation(*table_numbers, time, name, party_size, vip_status=False):  
  # Call the validate_params function to run standard checks.
  validate_params(table_numbers=table_numbers, time=time, name=name, party_size=party_size, vip_status=vip_status)
  # Check for blank name entry like '' or '   ' and return error
  if not name.strip():
    raise ValueError('Name must not be blank. Please enter valid name.')
  # Initialize variable for combined capacity of table numbers
  combined_capacity = 0
  #Initialize variable for datetime object from the time argument to use in check against existing reservation times
  requested_time = datetime.strptime(time, '%H:%M %m-%d-%Y') 
  # Iterate through the given table numbers
  for table_number in table_numbers:
    # Check that the requested reservation time isn't too close to an existing reservation for the same table so customers with reservations are not waiting for the table to become available when they arrive.    
    for r in reservations[table_number]:
      existing_time = datetime.strptime(reservation_lookup[r]['time'], '%H:%M %m-%d-%Y')
      if abs(requested_time - existing_time) < timedelta(hours=1):
        raise ValueError(f"Table {table_number} already has a reservation at {reservation_lookup[r]['time']}, which is less than 1 hour from {time}.")
    # Add current table capacity to combined_capacity
    combined_capacity += tables[table_number]['capacity']
  # Check that the size of the party fits the given table.
  if party_size > combined_capacity:
    raise ValueError(f"Party size {party_size} is too large for table(s) {', '.join(str(t) for t in table_numbers)}. Seating capacity is only {combined_capacity}.")
  # Create the reservation class object to generate the reservation ID.
  reserve_obj = Reservation()
  # Generate list of the reserved table numbers
  reserved_tables = list(table_numbers)
  # Call the reservation's info dictionary attribute
  reservation_ID = reserve_obj.ID
  reservation_info = {'name': name, 'time': time, 'num_diners': party_size, 'vip_status': vip_status, 'tables': reserved_tables}
  for table in reserved_tables:
    reservations[table].append(reservation_ID)
  reservation_lookup[reservation_ID] = reservation_info
  print(f"Reservation number {reservation_ID} created for {name} at {time} on table(s) {', '.join(str(t) for t in reserved_tables)}. Their VIP status is {vip_status}.")
  save_data()

# Function to find a customer's reservation ID from their name and reservation time.
def find_reservation(name, time):
  # Call the validate_params function to run standard checks.
  validate_params(name=name, time=time)
  # Check for blank name entry like '' or '   ' and return error
  if not name.strip():
    raise ValueError('Name must not be blank. Please enter valid name.')
  # Iterate through each reservation in the lookup dictionary and match by name and time.
  for rsv in reservation_lookup:
    if reservation_lookup[rsv]['name'] == name and reservation_lookup[rsv]['time'] == time:
      print(f"The reservation number is {rsv}.")
      return rsv
  print(f"No reservation found for {name} at {time}.")

# Placeholder for function to modify an existing reservation. Note for the future, kwarg new_table will need to become *new_tables or accept a list input. 
def modify_reservation(reservation_ID, new_table=None, new_name=None, new_party_size=None, new_time=None, new_vip_status=None):
  pass

# Function to cancel an existing reservation. Will take in the reservation ID, clear that ID from all relevant tables in the reservations dict, and clear the reservation ID's dict from reservation_lookup.
def cancel_reservation(reservation_ID):
  # Validate reservation_ID entered as a string
  if not isinstance(reservation_ID, str):
    raise TypeError("Reservation ID must be a string.")
  # Validate that the reservation ID exists
  elif reservation_ID not in reservation_lookup:
    raise ValueError(f"No reservation found with ID {reservation_ID}.")
  # If checks passed, remove the reservation from all linked tables in the reservations dict and clear it from reservation_lookup
  else:
    reserved_tables = reservation_lookup[reservation_ID]['tables']
    for t in reserved_tables:
      reservations[t].remove(reservation_ID)
    del reservation_lookup[reservation_ID]
  save_data()

# Function to assign tables from reservation IDs when customers arrive at the restaurant. Use *args to take in any number of reservation IDs at once.
def assign_table_from_reservation(*reservation_IDs):
  # Validate reservation IDs correctly entered and return a ValueError if not.
  if not all(isinstance(rsv_ID, str) for rsv_ID in reservation_IDs):
      raise TypeError("All reservation IDs must be strings.")
  # Iterate through the the provided reservation IDs.
  for rsv_ID in reservation_IDs:
    # Check if the reservation ID exists and print a message if not then continue to remaining IDs.
    if rsv_ID not in reservation_lookup:
      print(f"No reservation found with ID {rsv_ID}.")
      continue
    # For each valid reservation ID, pull the relevant info from the reservation lookup dict and call the assign_table function using the reservation info for the arguments.
    else:
      rsv = reservation_lookup[rsv_ID]
      name = rsv['name']
      vip_status = rsv['vip_status']
      time = rsv['time']
      table_numbers = rsv['tables']
      party_size = rsv['num_diners']
      assign_table(*table_numbers, name=name, party_size=party_size, vip_status=vip_status, reserve_status=True, time=time)
      # Remove the reservation ID from the reservations and reservation_lookup dictionaries now that the guests have arrived and been assigned to the table.
      for table_number in table_numbers:
        reservations[table_number].remove(rsv_ID)
      del reservation_lookup[rsv_ID]
  save_data()

# Placeholder for function to close an order, taking in the order_number and the tip amount(s) left by the party. Uses variable *tips to account for split bills to enter each payor's tip amount.
def close_order(order_number, *tips):
  # Check tip amounts
  validate_params(tips=tips)
  pass

# Function to remove tables' guests when they leave the restaurant. Uses *args to accept a variable amount of table numbers to remove at once.
def clear_tables(*table_numbers):
  # Validate that all table number arguments are integer numbers.
  if not all(isinstance(num, int) for num in table_numbers):
    raise TypeError("All table numbers must be integers.")
  # Iterate through the table numbers. 
  for num in table_numbers:
    # Validate the table number exists. If not print a message and continue.
    if num not in tables:
      print(f"There is no table number {num}!")
    # Validate the table has an assignment that can be removed. If not, print a message and continue.
    elif tables[num]['status'] == 'available':
      print(f"Table number {num} is already empty.")
    # With the table number and assignment validated, clear all items except the capacity from the corresponding table number key in the tables dictionary.
    else:
      # Combine the current table number in a list with its 'linked_tables' to clear all
      tables_to_clear = [num] + tables[num]['linked_tables']
      # Iterate through tables to clear
      for t in tables_to_clear:
        # store the capacity value in a variable
        capacity = tables[t]['capacity']
        # clear the dict
        tables[t].clear()
        # reassign the capacity value
        tables[t]['capacity'] = capacity
        tables[t]['status'] = 'available'
        # Print different messages for the first table in the list vs the linked tables
        if t == num:  
          print(f'Table number {num} has been cleared.')
        else:
          print(f'Linked table {t} has been cleared.')
  save_data()

load_data()
print(tables)
print(reservations)
print(reservation_lookup)
print(menu)
