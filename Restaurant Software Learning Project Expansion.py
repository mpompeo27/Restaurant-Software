from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP

import json, os

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'restaurant_data.json')

tables = {}

reservations = {}

reservation_lookup = {}

menu = {}

# Create function to load data from our json file
def load_data():
  # Validate the path for the database file
  if os.path.exists(DB_FILE):
    try:
      # Open the database file and load the data from the json
      with open(DB_FILE, 'r') as db:
        data = json.load(db)
      # Restore global state
      tables.update({int(k): v for k, v in data['tables'].items()}) # repopulate tables dict
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
    elif name == 'name':
      # Confirm name is a string.
      if not isinstance(value, str):
        raise TypeError(f"Invalid name {value}. Must be a string.")
      # Confirm string is not empty.
      if not value:
        raise ValueError(f"Invalid name. Name must not be blank.")
    elif name == 'vip_status':
      # Confirm vip_status is a boolean.
      if not isinstance(value, bool):
        raise TypeError(f"Invalid VIP status {value}. Must be True or False.")
    elif name == 'reserve_status':
      # Confirm reservation status is a boolean.
      if not isinstance(value, bool):
        raise TypeError(f"Invalid reservation status {value}. Must be True or False.")
    elif name == 'time':
      # Validate time entered as a string formatted correctly as 24 hr time and date HH:MM mm-dd-yyyy.
      try:
        datetime.strptime(value, '%H:%M %m-%d-%Y')
      except ValueError:
        raise ValueError("Seating time must be formatted as HH:MM mm-dd-yyyy (e.g. '14:30 03-20-2026').")
    elif name == 'party_size':
      # Confirm party_size is an integer.
      if not isinstance(value, int):
        raise TypeError(f"Invalid party size '\{value}'\. Must be a positive integer.")      
      if value <= 0:
        raise ValueError(f"Invalid party size {value}. Must be a positive integer.")
    elif name == 'tip':
      # Confirm tip is a number, and that it's between 0 and 100.
      if not isinstance(value, (int, float)):
        raise TypeError(f"\'{value}\' is not a valid tip percent. Must be a number between 0 and 100.")
      if 0 <= value <= 100:
        raise ValueError(f"\'{value}\' is not a valid tip percent. Must be a number between 0 and 100.")
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

# Define a function to assign tables that will take in a table number, the guest name, the size of the party, whether they have VIP status, if they have a reservation, and the time of their seating. If unspecified, VIP status and reservation will default to false and seating time will default to None before being set inside the function to the current time in UTC-6.
def assign_table(table_number, name, party_size, vip_status=False, reserve_status=False, time=None): 
  # Set the actual default value for time to the current time.
  if time is None:
    time = datetime.now(timezone(timedelta(hours=-6))).strftime('%H:%M %m-%d-%Y')
  # Call the validate_params function to run standard checks.
  validate_params(table_number=table_number, name=name, party_size=party_size, vip_status=vip_status, reserve_status=reserve_status, time=time)
  # Check if table is already occupied.
  if 'name' in tables[table_number]:
    raise ValueError(f"Table {table_number} is currently occupied.") 
  # Check that the size of the party fits the given table.
  if party_size > tables[table_number]['capacity']:
    raise ValueError(f"Party size {party_size} is too large for table {table_number}. Seating capacity is only {tables[table_number]['capacity']}.")
  # If table is being assigned without a reservation, check the seating time against existing reservations to make sure there is no conflict with an upcoming reservation within 1 hour for which the table needs to remain open. This check is not needed if the table is being assigned from a reservation because the reservation system already checks to ensure reservations for a given table are sufficiently spaced out.
  if reserve_status == False:
    time_obj = datetime.strptime(time, '%H:%M %m-%d-%Y')
    for r in reservations[table_number]:
      existing_time = datetime.strptime(reservation_lookup[r]['time'], '%H:%M %m-%d-%Y')
      if timedelta(0) < (existing_time - time_obj) < timedelta(hours=1):
        raise ValueError(f"Table {table_number} has an upcoming reservation at {reservation_lookup[r]['time']} and cannot be seated. Table must remain open for the reservation.")
  # If validation checks are passed, add info to the tables dictionary to assig the table.
  tables[table_number]['name'] = name
  tables[table_number]['vip_status'] = vip_status
  tables[table_number]['reservation'] = reserve_status
  tables[table_number]['seating_time'] = time
  tables[table_number]['num_diners'] = party_size
  new_order = Order()
  tables[table_number]['order'] = {'ord_number': new_order.order_number}
  tables[table_number]['total'] = None
  save_data()

# Function to assign food and drink items to the order for a specific table, taking in the table number and the ordered items with **kwargs used to allow for variable keyword arguments for food and drinks separately. Items must be provided in a list format.
def add_order_items(table_number, **order_items):
  # Validate table number.
  validate_params(table_number=table_number)
  # Validate order items provided in list form.
  if not all(isinstance(v, list) for v in order_items.values()):
    raise ValueError("All order items must be provided in separate lists for food and drinks.")
  # Check if there is food in the order and if yes assign the 'food' parameter to a variable called 'foods'.
  if 'food' in order_items:
    foods = order_items.get('food')
    # Check that all items in the foods list are strings. Return ValueError if not.
    if not all(isinstance(item, str) for item in foods):
      raise ValueError("All food items must be strings.")
    # Check that all items in foods are on the menu. Return LookupError if not. 
    if not all(item in menu['foods'] for item in foods):
      raise LookupError("One or more food items are not on the menu.")
    # If all items in foods are properly entered as strings and on the menu, proceed to add to the order.
    # Validate if order already has food items and append to the list if yes.
    if 'food_items' in tables[table_number]['order']:
      for f in foods:
        tables[table_number]['order']['food_items'].append(f)
    # Otherwise create the 'food_items' key for this order and set it equal to the list of foods.
    else:
      tables[table_number]['order']['food_items'] = foods
  # Repeat the same for drinks.
  if 'drinks' in order_items: 
    drinks = order_items.get('drinks')
    if not all(isinstance(item, str) for item in drinks):
      raise ValueError("All drinks must be strings.")
    if not all(item in menu['drinks'] for item in drinks):
      raise LookupError("One or more drinks are not on the menu.")
    if 'drinks' in tables[table_number]['order']:
      for d in drinks:
        tables[table_number]['order']['drinks'].append(d)
    else:
      tables[table_number]['order']['drinks'] = drinks
  save_data()
      
# Function to remove food and drink items from a table's order in the case of mistakes, taking in the table number and the items to remove with **kwargs used to allow for variable keyword arguments for food and drinks separately. Items must be provided in a list format.
def remove_order_items(table_number, **removed_items):
  # Validate table number.
  validate_params(table_number=table_number)
  # Validate order items provided in list form.
  if not all(isinstance(v, list) for v in removed_items.values()):
    raise ValueError("All items to remove must be provided in separate lists for food and drinks.")  
  # Check if there is food in the removed items. If yes, assign the 'food' argument to a variable called 'remove_foods'.
  if 'food' in removed_items:
    remove_foods = removed_items.get('food')
    # Check that all items in the removed foods list are strings. Return ValueError if not, otherwise remove foods from the order in the tables dictionary.
    if not all(isinstance(item, str) for item in remove_foods):
      raise ValueError("All food items must be strings.")
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
      raise ValueError("All drinks must be strings.")   
    else:
      for drink in remove_drinks:
        if drink not in tables[table_number]['order']['drinks']:
          print(f"Cannot remove drink {drink} because it is not in the order.")
        else:
          tables[table_number]['order']['drinks'].remove(drink)
  save_data()

# Function that will take in the table number and an operation - either 'add' or 'print' - to iterate through items in the table's order and either sum the prices to get the total or print them all with formatting for the bill.
def iterate_items(table_number, op):
  if op == 'add':
    # Initialize total to 0.
    total = Decimal(0)
    # Check if the table's order has food, and if yes, iterate through the food_items and add each one's price to the total.
    if 'food_items' in tables[table_number]['order']:
      for food in tables[table_number]['order']['food_items']:
        item_price = menu['foods'][food]
        total += Decimal(item_price)      
    # Repeat for drinks.
    if 'drinks' in tables[table_number]['order']:
      for drink in tables[table_number]['order']['drinks']:
        item_price = menu['drinks'][drink]
        total += Decimal(item_price)
    return total
  elif op == 'print':
    if 'food_items' in tables[table_number]['order']:
      for food in tables[table_number]['order']['food_items']:
        item_price = menu['foods'][food]
        print(f"{food:<25} ${item_price:.2f}")
    # Repeat for drinks.
    if 'drinks' in tables[table_number]['order']:
      for drink in tables[table_number]['order']['drinks']:
        item_price = menu['drinks'][drink]
        print(f"{drink:<25} ${item_price:.2f}")

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

# Function to print the table's bill including tip with no split payment, taking in the table number and tip % with a default tip of 20%.
def print_bill(table_number, tip=None):
  # Validate the table number and tip amount.
  validate_params(table_number=table_number, tip=tip)
  # Print the order number at the top of the bill.
  print(f"Order Number: {tables[table_number]['order']['ord_number']}\n")
  iterate_items(table_number, 'print')
  total = calc_total(table_number).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
  tip_pct = Decimal(str(tip))/100
  total_tip = (total * tip_pct).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
  total_bill = (total + total_tip).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
  # Print messages for the order total, tip, and total bill.
  print(f"\n{'Order:':<25} ${total}")
  print(f"{f'Tip {tip}%:':<25} ${total_tip}")
  print(f"{'Total:':<25} ${total_bill}\n")
  return total_bill

# Function to calculate the price per person for splitting a bill. Takes in the table number as argument and optional number of people splitting the bill with default value None. Actual default value will be set inside the function to the number of diners because it requires referencing the table_number parameter.
def print_split_bill(table_number, tip=20.0, split=None):
  # Set the actual default value for split to the number of diners for the table and otherwise validate the value.
  if split is None:
    split = tables[table_number]['num_diners']
  # Validate the value of the split parameter if not defaulted.
  if not isinstance(split, int):
    raise TypeError(f"Number of people splitting the bill must be a positive integer.")
  if split <= 0:
    raise ValueError(f"Number of people splitting the bill must be a positive integer.")
  # Call print_bill to validate the table_number and tip parameters, print everything up to the total bill with tip, and returning the total_bill amount for use in calculating the split per person.
  total_bill = print_bill(table_number, tip)
  split_price = (total_bill / split).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
  print(f"{f'Per person:':<25} ${split_price}.")

# Create Reservation class for generating unique reservation IDs using a class variable reservation_count to ensure the counter is not modified elsewhere in the code outside the class constructor.
class Reservation:
  # Create the class variable for reservation count.  
  reservation_count = 0

  # Create a class constructor to increment the reservation count and create a unique string for the reservation ID. 
  def __init__(self):
    Reservation.reservation_count += 1
    self.ID = 'rsv-' + str(Reservation.reservation_count).zfill(5)

# Function to add a reservation to the reservations queue. It will take in the table number, the time of the reservation, the customer name, and their VIP status and create a Reservation class object to generate a reservation ID. If not specified, VIP status will default to False. The reservation ID will be added to the reservations dictionary in a list for the designated table, and the reservation info details will be added to the reservation_lookup dictionary under the reservation number. A message will print confirming the reservation was made successfully.
def add_reservation(table_number, time, name, party_size, vip_status=False):
  # Call the validate_params function to run standard checks.
  validate_params(table_number=table_number, time=time, name=name, party_size=party_size, vip_status=vip_status)
  # Check that the size of the party fits the given table.
  if party_size > tables[table_number]['capacity']:
    raise ValueError(f"Party size {party_size} is too large for table {table_number}. Seating capacity is only {tables[table_number]['capacity']}.")
  # Check that the requested reservation time isn't too close to an existing reservation for the same table so customers with reservations are not waiting for the table to become available when they arrive.
  requested_time = datetime.strptime(time, '%H:%M %m-%d-%Y')
  for r in reservations[table_number]:
    existing_time = datetime.strptime(reservation_lookup[r]['time'], '%H:%M %m-%d-%Y')
    if abs(requested_time - existing_time) < timedelta(hours=1):
      raise ValueError(f"Table {table_number} already has a reservation at {reservation_lookup[r]['time']}, which is less than 1 hour from {time}.")
  # Create the reservation class object to generate the reservation ID.
  reserve_obj = Reservation()
  # Call the reservation's info dictionary attribute
  reservation_ID = reserve_obj.ID
  reservation_info = {'name': name, 'time': time, 'num_diners': party_size, 'vip_status': vip_status, 'table': table_number}
  reservations[table_number].append(reservation_ID)
  reservation_lookup[reservation_ID] = reservation_info
  print(f"Table {table_number} has been reserved for {name} at {time} with reservation number {reserve_obj.ID}. Their VIP status is {vip_status}.")
  save_data()

# Function to find a customer's reservation ID from their name and reservation time.
def find_reservation(name, time):
  # Call the validate_params function to run standard checks.
  validate_params(name=name, time=time)
  # Iterate through each reservation in the lookup dictionary and match by name and time.
  for rsv in reservation_lookup:
    if reservation_lookup[rsv]['name'] == name and reservation_lookup[rsv]['time'] == time:
      print(f"The reservation number is {rsv}.")
      return rsv
  print(f"No reservation found for {name} at {time}.")

# Function to assign tables from reservation IDs when customers arrive at the restaurant. Use **kwargs to take in any number of reservation IDs at once.)
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
      name = reservation_lookup[rsv_ID]['name']
      vip_status = reservation_lookup[rsv_ID]['vip_status']
      time = reservation_lookup[rsv_ID]['time']
      table_number = reservation_lookup[rsv_ID]['table']
      party_size = reservation_lookup[rsv_ID]['num_diners']
      assign_table(table_number, name, party_size, vip_status, True, time)
      # Remove the reservation ID from the reservations and reservation_lookup dictionaries now that the guests have arrived and been assigned to the table.
      reservations[table_number].remove(rsv_ID)
      del reservation_lookup[rsv_ID]
  save_data()

# Function to remove tables' guests when they leave the restaurant. Uses *args to accept a variable amount of table numbers to remove at once.
def unassign_tables(*table_numbers):
  # Validate that all table number arguments are integer numbers.
  if not all(isinstance(num, int) for num in table_numbers):
    raise TypeError("All table numbers must be integers.")
  # Iterate through the table numbers. 
  for num in table_numbers:
    # Validate the table number exists. If not print a message and continue.
    if num not in tables:
      print(f"There is no table number {num}!")
    # Validate the table has an assignment that can be removed. If not, print a message and continue.
    elif 'name' not in tables[num]:
      print(f"Table number {num} is already empty.")
    # With the table number and assignment validated, remove each item from the corresponding table number key in the tables dictionary.
    else:
      tables[num].pop('name')
      tables[num].pop('vip_status')
      tables[num].pop('reservation')
      tables[num].pop('seating_time')
      tables[num].pop('num_diners')
      tables[num].pop('order')
      tables[num].pop('total')
      print(f"Table number {num} has been cleared.")
  save_data()

load_data()
print(tables)
print(reservations)
print(reservation_lookup)
print(menu)

#assign_table(1, 'Jiho', 2)
#add_order_items(1, food=['Pancakes'], drinks=['Orange Juice', 'Apple Juice'])
#print(str(tables) + '\n')

#assign_table(3, 'Jim', 4, True)
#add_order_items(3, food=['Spaghetti', 'Salad'], drinks=['White Wine'])
#print(str(tables) + '\n')

#assign_table(7, 'Mary', 7, True)
#add_order_items(7, food=['Salad', 'Pork Chops'])
#print(str(tables) + '\n')

#print_bill(3)
#print_split_bill(3, split=2)
#print(str(tables) + '\n')

#remove_order_items(1, drinks=['Apple Juice'])
#print(str(tables) + '\n')

#unassign_tables(3, 12, 2)
#print(str(tables) + '\n')

#add_reservation(4, '17:00 03-25-2026', "Mark", 4)
#add_reservation(6, '17:00 03-25-2026', "Davis", 5)
#add_reservation(2, '15:30 03-23-2026', "Roger", 2, True)
#print(str(reservations) + '\n')

#rsv1 = find_reservation('Mark', '17:00 03-25-2026')
#print(rsv1)
#rsv2 = find_reservation('Davis', '15:30 03-25-2026')
#reserve_list = [rsv1, rsv2]

#assign_table_from_reservation(*reserve_list)
#print(tables)
#print(str(reservations) + '\n')
