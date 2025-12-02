from db_manager import DBManager
from datetime import datetime
import sys
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Member Section -------------------------------------------------------------------
def member_page(db):
    print("1. Register")
    print("2. Login")
    choice = input("Select Option: ")
    if choice == '1':
        member_register(db)
    elif choice == '2':
        email = input("Member Email: ")
        password = input("Password: ")
        id = db.member_login(email, password)
        if id:
            print ("LOGIN SUCCESSFUL")
            while True:
                clear_screen()
                print("\n--- Member Menu ---")
                print("1. Update Profile")
                print("2. View Personalized Dashboard")
                print("3. Book/Upadate/Cancel Personal Training Session")
                print("4. Logout")
                sub_choice = input("Select Option: ")
                if sub_choice == '1':
                    clear_screen()
                    member_update_profile(db, id)
                    input("\nPress Enter to continue...")
                elif sub_choice == '2':
                    clear_screen()
                    member_view_dashboard(db, id)
                    input("\nPress Enter to continue...")
                elif sub_choice == '3':
                    clear_screen()
                    member_manage_booking(db, id)
                    input("\nPress Enter to continue...")
                elif sub_choice == '4':
                    break
        else:
            print("Login Failed.")

def member_register(db):
    print("\n--- Register Member ---")
    f_name = input("First Name: ")
    l_name = input("Last Name: ")
    email = input("Email: ")
    pw = input("Password: ")
    dob = input("Date of Birth (YYYY-MM-DD): ")
    gender = input("Gender (Male/Female/Other): ")
    goal = input("Fitness Goal: ")
    
    result = db.register_member(f_name, l_name, email, pw, dob, gender, goal)
    if isinstance(result, int):
        print(f"Success! Your Member ID is {result}")
    else:
        print(f"Registration Failed: {result}")


def member_update_profile(db, id):
    print("1. Update Fitness Goals")
    print("2. Update Health Metrics")
    print("3. Update Personal Information")
    choice = input("Select Option: ")
    if choice == '1':
        new_goals = input("Enter new fitness goals: ")
        success = db.update_fitness_goals(id, new_goals)
        if success:
            print("Fitness goals updated successfully.")
        else:
            print("Update failed.")
    elif choice == '2':
        print ("Enter new health metrics:")
        new_metrics = {}
        weight = input("Enter weight: ")
        height = input("Enter height: ")
        bodyfat = input("Enter body fat percentage: ")
        new_metrics['weight'] = weight
        new_metrics['height'] = height
        new_metrics['bodyfat'] = bodyfat

        success = db.add_health_metrics(id, new_metrics)
        if success:
            print("Health metrics updated successfully.")
        else:
            print("Update failed.")
    elif choice == '3':
        print("1. First Name")
        print("2. Last Name")
        print("3. Email")
        print("4. Password")
        print("5. Date of Birth")
        print("6. Gender")
        print("7. Back")
        sub_choice = input("Select Option: ")
        if sub_choice == '1':
            new_first = input("Enter new first name: ")
            success = db.update_personal_info(id,'first_name', new_first)
        elif sub_choice == '2':
            new_last = input("Enter new last name: ")
            success = db.update_personal_info(id,'last_name', new_last)
        elif sub_choice == '3':
            new_email = input("Enter new email: ")
            success = db.update_personal_info(id,'email', new_email)
        elif sub_choice == '4':
            new_password = input("Enter new password: ")
            success = db.update_personal_info(id,'password', new_password)
        elif sub_choice == '5':
            new_dob = input("Enter new date of birth (YYYY-MM-DD): ")
            success = db.update_personal_info(id,'date_of_birth', new_dob)
        elif sub_choice == '6':
            new_gender = input("Enter new gender (Male/Female/Other): ")
            success = db.update_personal_info(id,'gender', new_gender)
        elif sub_choice == '7':
            return
        
def member_view_dashboard(db, id):
    print ("=== Personalized Dashboard ===")
    profile = db.get_member_profile(id)
    if profile:
        health_metrics = profile[6]
        total_bookings = profile[7] if len(profile) > 7 else 0
        print(f"Name: {profile[1]} {profile[2]}")
        print(f"Fitness Goals: {profile[5]}")
        print(f"Total Bookings: {total_bookings}")
        if health_metrics:
            print(f"Recent Health Metrics: Weight - {health_metrics.weight}lbs, Height - {health_metrics.height}cm, Body Fat - {health_metrics.bodyfat}%")
    else:
        print("Profile not found.")

def member_manage_booking(db, id):
    print ("1. View/Manage Bookings")
    print ("2. View/Book Available Classes")
    print ("3. Back")
    choice = input("Select Option: ")
    if choice == '1':
        bookings = db.get_member_bookings(id)
        if bookings:
            print("=== Your Bookings ===")
            for b in bookings:
                print(f"Booking ID: {b[0]}, Class: {b[1]}, Start_Time: {b[2]}, End_Time: {b[3]}")
            print ("1. Cancel Booking")
            print ("2. Back")
            sub_choice = input("Select Option: ")
            if sub_choice == '1':
                booking_id = input("Enter Booking ID to cancel: ")
                success = db.cancel_booking(booking_id, id)
                if success:
                    print("Booking cancelled successfully.")
                else:
                    print("Cancellation failed.")
            elif sub_choice == '2':
                return
        else:
            print("No bookings found.")
    elif choice == '2':
        schedule = db.get_available_classes()
        print("=== Available Classes ===")
        for entry in schedule:
            # Handle both old format (5 items) and new format (7 items)
            if len(entry) >= 7:
                print(f"Schedule ID: {entry[0]}, Class: {entry[1]}, Room: {entry[2]}, Start Time: {entry[3]}, End Time: {entry[4]}, Bookings: {entry[5]}, Available Spots: {entry[6]}")
            else:
                print(f"Schedule ID: {entry[0]}, Class: {entry[1]}, Room: {entry[2]}, Start Time: {entry[3]}, End Time: {entry[4]}")
        print ("1. Book a Class")
        print ("2. Back")
        sub_choice = input("Select Option: ")
        if sub_choice == '1':
            schedule_id = input("Enter Schedule ID to book: ")
            success = db.book_class(id, schedule_id)
            if success:
                print("Class booked successfully.")
            else:
                print(f"Booking failed: {success}")
        elif sub_choice == '2':
            return
    elif choice == '3':
        return
    

    

# Trainer Section -------------------------------------------------------------------

def trainer_page(db):
    print("1. Register")
    print("2. Login")
    choice = input("Select Option: ")
    if choice == '1':
        trainer_register(db)
    elif choice == '2':
        email = input("Trainer Email: ")
        password = input("Password: ")
        id = db.trainer_login(email, password)
        if id:
            print ("LOGIN SUCCESSFUL")
            while True:
                clear_screen()
                print("\n--- Trainer Menu ---")
                print("1. View Schedule")
                print("2. Search Member Profiles")
                print("3. Manage Availability")
                print("4. Logout")
                sub_choice = input("Select Option: ")
                if sub_choice == '1':
                    clear_screen()
                    trainer_view_schedule(db, id)
                    input("\nPress Enter to continue...")
                elif sub_choice == '2':
                    clear_screen()
                    trainer_search_member(db, id)
                    input("\nPress Enter to continue...")
                elif sub_choice == '3':
                    clear_screen()
                    trainer_manage_availability(db, id)
                    input("\nPress Enter to continue...")
                elif sub_choice == '4':
                    break
        else:
            print("Login Failed.")

def trainer_register(db):
    print("\n--- Register Trainer ---")
    f_name = input("First Name: ")
    l_name = input("Last Name: ")
    email = input("Email: ")
    pw = input("Password: ")
    specialization = input("Specialization: ")
    
    
    result = db.register_trainer(f_name, l_name,email,pw,specialization)
    if isinstance(result, int):
        print(f"Success! Your Trainer ID is {result}")
    else:
        print(f"Registration Failed: {result}")
    
def trainer_view_schedule(db, id):
    print("=== Your Schedule ===")
    schedule = db.get_trainer_schedule(id)
    for entry in schedule:
        print(f"Class: {entry[0]}, Room: {entry[1]}, Start Time: {entry[2]}, End Time: {entry[3]}")
    
def trainer_search_member(db, id):
    firstname = input("Enter member first name to search: ")
    lastname = input("Enter member last name to search: ")
    results = db.search_member_by_name(firstname, lastname)
    if results:
        print("=== Member Profile ===")
        health_metrics = results[6]
        print(f"Name: {results[1]} {results[2]}")
        print(f"Fitness Goals: {results[5]}")
        if health_metrics:
            print(f"Recent Health Metrics: Weight - {health_metrics.weight}lbs, Height - {health_metrics.height}cm, Body Fat - {health_metrics.bodyfat}%")
    else:
        print("No members found.")

def trainer_manage_availability(db, id):
    print("1. View/ Manage Availability")
    print("2. Add Availability")
    print("3. Remove Availability")
    print("4. Back")
    choice = input("Select Option: ")
    if choice == '1':
        availabilities = db.get_trainer_availability(id)
        print("=== Your Availabilities ===")
        for a in availabilities:
            print(f"Availability_id: {a[0]}, Day: {a[1]}, Start Time: {a[2]}, End Time: {a[3]}")
        print(" 1. update Availability")
        print(" 2. Back")
        sub_choice = input("Select Option: ")
        if sub_choice == '1':
            availability_id = input("Enter Availability ID to update: ")
            day_of_week = input("Enter new day of week: ")
            start_time = input("Enter new start time (HH:MM:SS): ")
            end_time = input("Enter new end time (HH:MM:SS): ")
            success = db.update_trainer_availability(availability_id, day_of_week, start_time, end_time)
            if success:
                print("Availability updated successfully.")
            else:
                print("Update failed.")
        elif sub_choice == '2':
            return
    elif choice == '2':
        day_of_week = input("Enter day of week: ")
        start_time = input("Enter start time (HH:MM:SS): ")
        end_time = input("Enter end time (HH:MM:SS): ")
        success = db.add_trainer_availability(id, day_of_week, start_time, end_time)
        if success:
            print("Availability added successfully.")
        else:
            print("Addition failed.")
    elif choice == '3':
        availabilities = db.get_trainer_availability(id)
        print("=== Your Availabilities ===")
        for a in availabilities:
            print(f"Availability_id: {a[0]}, Day: {a[1]}, Start Time: {a[2]}, End Time: {a[3]}")
        availability_id = input("Enter Availability ID to remove: ")
        success = db.remove_trainer_availability(availability_id, id)
        if success:
            print("Availability removed successfully.")
        else:
            print("Removal failed.")
    elif choice == '4':
        return


# Admin Section ---------------------------------------------------------------------

def admin_page(db):
    Username = input("Admin Username: ")
    Password = input("Admin Password: ")
    if db.admin_login(Username, Password):
        while True:
            clear_screen()
            print("\n--- Admin Menu ---")
            print("1. Room Management")
            print("2. Class Management")
            print("3. Schedule Management")
            print("4. Logout")
            sub_choice = input("Select Option: ")
            if sub_choice == '1':
                clear_screen()
                admin_room_management(db)
                input("\nPress Enter to continue...")
            elif sub_choice == '2':
                clear_screen()
                admin_class_management(db)
                input("\nPress Enter to continue...")
            elif sub_choice == '3':
                clear_screen()
                admin_schedule_management(db)
                input("\nPress Enter to continue...")
            elif sub_choice == '4':
                break
    else:
        print("Login Failed.")

def admin_room_management(db):
    print("1. View Rooms")
    print("2. Add Room")
    print("3. Remove Room")
    print("4. Back")
    choice = input("Select Option: ")
    if choice == '1':
        rooms = db.get_all_rooms()
        print("=== Rooms ===")
        for r in rooms:
            print(f"Room ID: {r[0]}, Name: {r[1]}, Capacity: {r[2]}")
    elif choice == '2':
        room_name = input("Enter room name: ")
        capacity = input("Enter room capacity: ")
        success = db.add_room(room_name, capacity)
        if success:
            print("Room added successfully.")
        else:
            print("Addition failed.")
    elif choice == '3':
        room_id = input("Enter room ID to remove: ")
        success = db.remove_room(room_id)
        if success:
            print("Room removed successfully.")
        else:
            print("Removal failed.")
    elif choice == '4':
        return

def admin_class_management(db):
    print("1. View Classes")
    print("2. Add Class")
    print("3. Remove Class")
    print("4. Back")
    choice = input("Select Option: ")
    if choice == '1':
        classes = db.get_all_classes()
        print("=== Classes ===")
        for c in classes:
            print(f"Class ID: {c[0]}, Name: {c[1]}, Description: {c[2]}, Duration: {c[3]} mins")
    elif choice == '2':
        class_name = input("Enter class name: ")
        description = input("Enter class description: ")
        duration = input("Enter class duration (in minutes): ")
        success = db.add_class(class_name, description, duration)
        if success:
            print("Class added successfully.")
        else:
            print("Addition failed.")
    elif choice == '3':
        class_id = input("Enter class ID to remove: ")
        success = db.remove_class(class_id)
        if success:
            print("Class removed successfully.")
        else:
            print("Removal failed.")
    elif choice == '4':
        return


def admin_schedule_management(db):
    print("1. View Schedules")
    print("2. Remove Schedule")
    print("3. Add Schedule")
    print("4. Back")
    choice = input("Select Option: ")
    if choice == '1':
        schedules = db.get_all_schedules()
        print("=== Schedules ===")
        for s in schedules:
            print(f"Schedule ID: {s[0]}, Class: {s[1]}, Room: {s[2]}, Trainer: {s[3]}, Start Time: {s[4]}, End Time: {s[5]}")
    elif choice == '2':
        schedule_id = input("Enter schedule ID to remove: ")
        success = db.remove_schedule(schedule_id)
        if success:
            print("Schedule removed successfully.")
        else:
            print("Removal failed.")
    elif choice == '3':
        admin_add_schedule(db)


    elif choice == '4':
        return


def admin_add_schedule(db):
        # get dates
        start_time = input("Enter start time (HH:MM:SS): ")
        end_time = input("Enter end time (HH:MM:SS): ")
        day_of_week = input("Enter day of week (Monday): ")

        try:
            start_dt = datetime.strptime(start_time.strip(), "%H:%M:%S").time()
            end_dt = datetime.strptime(end_time.strip(), "%H:%M:%S").time()
        except Exception:
            print("Invalid time format. Please use HH:MM:SS")
            return

        # display available classes within duration
        classes = db.get_classes_by_duration(start_dt, end_dt)
        print("=== Classes ===")
        if isinstance(classes, str):
            print(f"Error fetching classes: {classes}")
        elif classes:
            for c in classes:
                print(f"Class ID: {c[0]}, Name: {c[1]}, Description: {c[2]}, Duration: {c[3]} mins")
        else:
            print("No classes available for the provided duration.")
            return

        # display available rooms 
        rooms = db.get_available_rooms(start_dt, end_dt)
        print("=== Rooms ===")
        if isinstance(rooms, str):
            print(f"Error fetching rooms: {rooms}")
        elif rooms:
            for r in rooms:
                print(f"Room ID: {r[0]}, Name: {r[1]}, Capacity: {r[2]}")
        else:
            print("No rooms available for the provided time range.")
            return

        # display available trainers 
        trainers = db.get_available_trainers(day_of_week, start_dt, end_dt)
        print("=== Trainers ===")
        if isinstance(trainers, str):
            print(f"Error fetching trainers: {trainers}")
        elif trainers:
            for t in trainers:
                print(f"Trainer ID: {t[0]}, Name: {t[1]} {t[2]}, Specialization: {t[3]}")
        else:
            print("No trainers available for the provided day/time range.")
            return

        class_id = input("Enter class ID to schedule: ")
        room_id = input("Enter room ID to schedule: ")
        trainer_id = input("Enter trainer ID to schedule: ")
        success = db.add_schedule(class_id, room_id, trainer_id,day_of_week, start_dt, end_dt)
        if success:
            print("Schedule added successfully.")
        else:
            print("Addition failed.")
        


if __name__ == "__main__":
    db = DBManager()

    while True:
        clear_screen()
        print("\n--- FITNESS CLUB SYSTEM ---")
        print("1. Member Page")
        print("2. Trainer Page")
        print("3. Admin Page")
        print("4. Reset Database")
        print("5. Exit")

        choice = input("Select Option: ")
        if choice == '1':
            clear_screen()
            member_page(db)
        elif choice == '2':
            clear_screen()
            trainer_page(db)
        elif choice == '3':
            clear_screen()
            admin_page(db)
        elif choice == '4':
            clear_screen()
            db.reset_db()
            input("\nPress Enter to continue...")
        elif choice == '5':
            print("Exiting...")
            db.close()
            sys.exit(0)