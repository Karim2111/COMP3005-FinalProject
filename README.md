# COMP3005-FinalProject: Karim Rifai (101300239)

This repository is for the final project of the COMP3005 course. 

Video demonstration link: [Demo Video](https://drive.google.com/file/d/18-3ATBZVYYx6SHYwwUgcKTD2SGUxe26r/view?usp=sharing)

PDF link: [Project Documentation](KarimRifai-101300239-FinalProject.pdf)


## Project Structure
- `db_manager.py`: Manages database connections and operations.
- `models.py`: Defines the database schema using SQLAlchemy ORM.
- `app.py`: The main application logic and user interface.
- `requirements.txt`: Lists the required Python packages.

## Minimum Requirements By Group Size (1)

| Requirement | Details |
|---|---|
| Entities | `Member`, `Trainer`, `Room`, `Admin`, `FitnessClass`, `ClassSchedule`, `Booking`, `HealthMetric`, `TrainerAvailability` |
| Relationships | Member-Booking, Member-HealthMetric, Trainer-ClassSchedule, Trainer-TrainerAvailability, FitnessClass-ClassSchedule, Room-ClassSchedule, ClassSchedule-Booking |
| Application Operations | `Member`: register, login, view dashboard, update profile, update personal info, add health metrics, manage booking; `Trainer`: register, login, view schedule, search member, manage availability; `Admin`: login, room management, class management, schedule management |
| Mandatory roles | `Member`, `Trainer`, `Admin` |
| View + Trigger + Index | View: member_dashboard_view; Trigger: enforce_capacity (check_class_capacity); Index: idx_member_email, idx_booking_member, idx_booking_schedule |


## Setup Instructions
1. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Configure the database connection in `db_manager.py`.
    ```python
    # Format: postgresql://user:password@host/dbname
    DATABASE_URL = "postgresql://postgres:yourpassword@host/dbname"
    ```
3. Run the application:
   ```bash
   python app.py
   ```

## Required Content for All Projects

### Normalization:

All Tables are already in 3NF

Normalization Proof:
1. 2NF Compliance:
- All 9 tables use single-column primary keys (member_id, trainer_id, room_id, admin_id, class_id, schedule_id, booking_id, metric_id, availability_id).
- All tables use a primary key therefore no table has a composite primary key, partial dependencies 
cannot exist

2. 3NF Compliance:
- No non-key attribute depends on another non-key attribute in any table therefor there are no transitive dependencies so it is already in 3NF
Some examples:
- Member table: email does not determine first_name, first_name does not determine fitness_goals. All attributes independently describe the member.
- HealthMetric table: weight does not determine height, height does not determine bodyfat. Each is an independent measurement of the same metric entry.
- ClassSchedule table: day_of_week does not determine start_time (multiple schedules can exist on same day at different times). Time attributes independently describe when the schedule occurs.



### ER Model:
![ER Model Image](ermodel.png)




### ER to Relational Mapping:
![ER to Relational Mapping Image](relational.png)

### Assumptions and Mapping Tables:
| Requirements | Assumptions/Notes | Representation in ER Model and Relational Schema
|---|---|---|
| Members has unique ID and their basic info and login are stored | member_id is used as the primary key for easier joins and indexing | Entity member (PK: member_id, attributes: first_name, last_name, email, password)|
| The system records member health metrics over time without overwriting previous entries | Each measurement is connected to one member by member_id and has a time stamp | entity health_metric (PK: metric_id, FK: member_id, attributes: weight, height, bodyfat, recorded_at) |
| Trainers define their availability so classes can only be booked in free time slots | Each availability slot is connected to one trainer | Relationship “trainer Offers trainer_availability” (1:N); entity trainer_availability (PK: availability_id, FK: trainer_id, attributes: day_of_week, start_time, end_time)|
| Members can book classes that are scheduled at specific times | Each booking is connected to one member and class | Relationships “member Makes booking” and “class_schedule Receives booking” (both 1:N); entity booking (PK: booking_id, FKs: member_id, schedule_id, attribute: status)|
| Fitness classes are defined once and then scheduled in rooms with trainer and times | Class like yoga can happen multiple times | Entity FitnessClass (PK: class_id, attributes: name, description, duration); Relationship "FitnessClass Has ClassSchedule" (1:N)|
| Rooms have limited capacity and must be managed to avoid overbooking | Each room has capacity that is enforced by trigger | Entity Room (PK: room_id, attributes: room_name, capacity)|
| Admins manage the system | Admin accounts are separate from members and trainers | Entity Admin (PK: admin_id, attributes: username, password)|





### Database Definition:     
- `models.py`: Contains the SQLAlchemy ORM definitions for the database schema.
- Includes `Member`, `Trainer`, `Room`, `Admin`, `FitnessClass`, `ClassSchedule`, `Booking`, `HealthMetric`, and `TrainerAvailability` tables with appropriate relationships and constraints.
- **View**: `member_dashboard_view` - Aggregates member information with health metrics and booking counts for optimized dashboard queries.
- **Trigger**: `enforce_capacity` - Executes the `check_class_capacity()` function before inserting bookings to prevent overbooking rooms beyond capacity.
- **Indexes**: 
  - `idx_member_email` - Fast member login lookups by email
  - `idx_booking_member` - Optimizes member booking queries
  - `idx_booking_schedule` - Speeds up class schedule lookups

### Functionality Demonstration:
- `Member` functionality: `member_register()`, `member_login()`, `member_view_dashboard()`, `member_update_profile()`, `member_manage_booking()`
    - `member_register()`: Creates a new member account and stores it in the database.
    - `member_login()`: Authenticates a member and allows access to member-specific features.
    - `member_view_dashboard()`: Displays a personalized dashboard with fitness goals, health metrics, and total bookings using the optimized `member_dashboard_view`.
    - `member_update_profile()`: Allows members to update their fitness goals, health metrics (weight, height, body fat), and personal information (name, email, password, date of birth, gender).
    - `member_manage_booking()`: Enables members to book, view, and cancel class bookings. The booking system enforces room capacity limits via database trigger.

- `Trainer` functionality: `trainer_register()`, `trainer_login()`, `trainer_view_schedule()`, `trainer_search_member()`, `trainer_manage_availability()`
    - `trainer_register()`: Creates a new trainer account with specialization and stores it in the database.
    - `trainer_login()`: Authenticates a trainer and allows access to trainer-specific features.
    - `trainer_view_schedule()`: Displays the trainer's assigned class schedules with room and time details.
    - `trainer_search_member()`: Allows trainers to search for members by first or last name and view their profile including fitness goals and health metrics.
    - `trainer_manage_availability()`: Enables trainers to add, view, update, and remove their availability by day of week and time range.

- `Admin` functionality: `admin_login()`, `admin_room_management()`, `admin_class_management()`, `admin_schedule_management()`
    - `admin_login()`: Authenticates an admin and allows access to admin-specific features.
    - `admin_room_management()`: Manages rooms - view all rooms, add new rooms with capacity, and remove existing rooms.
    - `admin_class_management()`: Oversees fitness classes - view all classes, add new classes with description and duration, and remove classes.
    - `admin_schedule_management()`: Complete scheduling system that matches available trainers, rooms, and classes based on time constraints and displays only compatible options for scheduling.

### Code Structure:
- `db_manager.py`: Database connection and operations.
- `models.py`: Database schema definitions.
- `app.py`: The main application logic.

### Interface & User Flow:

- Command-line interface for user interactions.
- Member, Trainer, and Admin roles with distinct menus and options.
```bash
Member Menu:

#First Level Menu
1. Register
2. Login
#Second Level Menu
1. View Dashboard
2. Update Profile
   - Update Fitness Goals
   - Update Health Metrics (Weight, Height, Body Fat)
   - Update Personal Information
3. Manage Booking
   - View/Cancel Bookings
   - Book Available Classes
4. Logout
 ```

```bash
Trainer Menu:

#First Level Menu
1. Register
2. Login
#Second Level Menu
1. View Schedule
2. Search Member
3. Manage Availability
   - View/Update Availability
   - Add Availability
   - Remove Availability
4. Logout
```

```bash
Admin Menu:

#First Level Menu
1. Login
#Second Level Menu
1. Room Management
   - View Rooms
   - Add Room
   - Remove Room
2. Class Management
   - View Classes
   - Add Class
   - Remove Class
3. Schedule Management
   - View Schedules
   - Add Schedule (with smart filtering of available trainers, rooms, and classes)
   - Remove Schedule
4. Logout
```
