import sqlite3

# Initialize the database and create the seats table only if it doesn't exist
def initialize_seats():
    conn = sqlite3.connect('train_seats.db')
    c = conn.cursor()
    
    # Create the seats table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS seats
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 seat_number INTEGER NOT NULL,
                 status TEXT NOT NULL CHECK(status IN ('available', 'booked')))''')
    
    # Populate the seats table only if there are no seats yet
    seat_count = c.execute("SELECT COUNT(*) FROM seats").fetchone()[0]
    if seat_count == 0:
        for i in range(1, 81):  # 80 seats total
            c.execute("INSERT INTO seats (seat_number, status) VALUES (?, 'available')", (i,))
    
    conn.commit()
    conn.close()

# Find available seats based on the number of seats requested
def find_available_seats(num_seats):
    conn = sqlite3.connect('train_seats.db')
    c = conn.cursor()

    available_seats = []

    # Prioritize booking in the same row if possible
    for row in range(1, 12):  # 11 rows in total (10 rows of 7 seats, 1 row of 3 seats)
        if row < 11:  # First 10 rows with 7 seats each
            seats_in_row = c.execute("SELECT seat_number FROM seats WHERE seat_number BETWEEN ? AND ? AND status='available'",
                                     (row * 7 - 6, row * 7)).fetchall()
        else:  # Last row with 3 seats
            seats_in_row = c.execute("SELECT seat_number FROM seats WHERE seat_number BETWEEN 78 AND 80 AND status='available'").fetchall()

        available_seats.extend([seat[0] for seat in seats_in_row])
        if len(available_seats) >= num_seats:
            break

    # If not enough seats are found in rows, book adjacent available seats
    if len(available_seats) < num_seats:
        remaining_seats = c.execute("SELECT seat_number FROM seats WHERE status='available'").fetchall()
        available_seats.extend([seat[0] for seat in remaining_seats])

    conn.close()
    return available_seats[:num_seats]  # Return only the number of seats requested

# Book the specified seats and update their status in the database
def book_seats(seat_numbers):
    conn = sqlite3.connect('train_seats.db')
    c = conn.cursor()
    
    for seat_number in seat_numbers:
        c.execute("UPDATE seats SET status='booked' WHERE seat_number=?", (seat_number,))
    
    conn.commit()
    conn.close()

# Display the current status of all seats
def display_seats():
    conn = sqlite3.connect('train_seats.db')
    c = conn.cursor()
    
    seats = c.execute("SELECT seat_number, status FROM seats ORDER BY seat_number").fetchall()
    for i, seat in enumerate(seats):
        seat_display = f"{seat[0]}: {'🟢' if seat[1] == 'available' else '🔴'}"
        
        if (i + 1) % 7 == 0 or i == 79:  # New line after every 7 seats or the last row of 3 seats
            print(seat_display)
        else:
            print(seat_display, end=" ")
    
    conn.close()

# Function to check if any seats are available
def available_seats_count():
    conn = sqlite3.connect('train_seats.db')
    c = conn.cursor()
    available_count = c.execute("SELECT COUNT(*) FROM seats WHERE status='available'").fetchone()[0]
    conn.close()
    return available_count

# Main function to handle multiple bookings
def book_tickets():
    initialize_seats()  # Initialize the seats if not already done

    while True:
        available_seats_remaining = available_seats_count()
        if available_seats_remaining == 0:
            print("The coach is fully booked! No more seats available.")
            break

        print(f"Available seats: {available_seats_remaining}")
        num_seats = int(input(f"Enter the number of seats to book (up to 7 seats): "))

        if num_seats > 7:
            print("You can only book a maximum of 7 seats at a time.")
        elif num_seats > available_seats_remaining:
            print(f"Only {available_seats_remaining} seats are available. Please try again.")
        else:
            available_seats = find_available_seats(num_seats)
            book_seats(available_seats)
            print(f"Seats booked: {available_seats}")
            display_seats()
        
        more_tickets = input("Do you want to book more tickets? (yes/no): ").lower()
        if more_tickets != "yes":
            print("Thank you for using the booking system!")
            break

# Example usage
book_tickets()
