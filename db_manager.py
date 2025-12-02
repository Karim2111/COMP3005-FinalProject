# db_manager.py
from sqlalchemy import and_, create_engine, or_ , text
from sqlalchemy.orm import sessionmaker
from models import Base, Member, Trainer, Room, FitnessClass, ClassSchedule, Booking, HealthMetric, TrainerAvailability, Admin
from datetime import datetime

# DB Connection String
# Format: postgresql://user:password@host/dbname
DATABASE_URL = "postgresql://postgres:admin@localhost/final"

class DBManager:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        print("Database Connected")

    def create_view(self):
        session = self.get_session()
        session.execute(text("""
            CREATE OR REPLACE VIEW member_dashboard_view AS
            SELECT 
                m.member_id,
                m.first_name,
                m.last_name,
                m.fitness_goals,
                hm.weight,
                hm.height,
                hm.bodyfat,
                hm.recorded_at,
                COUNT(b.booking_id) as total_bookings
            FROM member m
            LEFT JOIN health_metric hm ON m.member_id = hm.member_id
            LEFT JOIN booking b ON m.member_id = b.member_id
            GROUP BY m.member_id, hm.metric_id
        """))
        session.commit()
        session.close()

    def create_trigger(self):
        session = self.get_session()
        session.execute(text("""
            CREATE OR REPLACE FUNCTION check_class_capacity()
            RETURNS TRIGGER AS $$
            DECLARE
                current_bookings INT;
                max_capacity INT;
            BEGIN
                SELECT COUNT(*), r.capacity
                INTO current_bookings, max_capacity
                FROM booking b
                JOIN class_schedule cs ON b.schedule_id = cs.schedule_id
                JOIN room r ON cs.room_id = r.room_id
                WHERE b.schedule_id = NEW.schedule_id
                GROUP BY r.capacity;
                
                IF current_bookings >= max_capacity THEN
                    RAISE EXCEPTION 'Class is at full capacity';
                END IF;
                
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            
            CREATE TRIGGER enforce_capacity
            BEFORE INSERT ON booking
            FOR EACH ROW
            EXECUTE FUNCTION check_class_capacity();
        """))
        session.commit()
        session.close()

    def create_index(self):
        session = self.get_session()
        # Index on email for fast member login lookups
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_member_email 
            ON member(email);
        """))
        
        # Index on member_id for faster bookings queries
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_booking_member 
            ON booking(member_id);
        """))
        
        # Index on schedule_id for faster class lookups
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_booking_schedule 
            ON booking(schedule_id);
        """))
        session.commit()
        session.close()



    def initialize_db(self):
        Base.metadata.create_all(self.engine)
        print("Database initialized (tables created).")

        self.create_view()
        self.create_trigger()
        self.create_index()

        with self.Session() as session:
            if session.query(Member).count() == 0:
                self.insert_sample_data()
                
                print("Sample data inserted")
            else:
                print("Sample data already exists, skipping insertion.")
    
    def reset_db(self):
        # Drop views and triggers before dropping tables
        session = self.get_session()
        try:
        
            session.execute(text("DROP VIEW IF EXISTS member_dashboard_view CASCADE"))
            session.execute(text("DROP TRIGGER IF EXISTS enforce_capacity ON booking"))
            session.execute(text("DROP FUNCTION IF EXISTS check_class_capacity() CASCADE"))
            session.commit()
        except Exception as e:
            print(f"Error dropping views/triggers: {e}")
            session.rollback()
        finally:
            session.close()
        
        # Now drop all tables
        Base.metadata.drop_all(self.engine)
        print("Database reset (tables dropped).")
        self.initialize_db()


    def get_session(self):
        return self.Session()
    
    def close(self):
        self.engine.dispose()
        print("Database connection closed")


    def insert_sample_data(self):
        session = self.get_session()
        try:
            # Members
            member1 = Member(first_name="Jack", last_name="Wimp", email="jack@gmail.com", password="123", date_of_birth="1990-01-15", gender="Male", fitness_goals="Lose weight")
            member2 = Member(first_name="Ryan", last_name="Perry", email="ryan@gmail.com", password="123", date_of_birth="1985-06-22", gender="Male", fitness_goals="Build muscle")
            member3 = Member(first_name="Ming", last_name="Vo", email="ming@gmail.com", password="123", date_of_birth="1992-03-10", gender="Female", fitness_goals="Improve endurance")
            
            # Trainers
            trainer1 = Trainer(first_name="Grant", last_name="Tar", email="grant@gmail.com", password="123", specialization="Yoga")
            trainer2 = Trainer(first_name="Karim", last_name="Rifai", email="karim@gmail.com", password="123", specialization="Strength Training")
            
            
            # Admin
            admin = Admin(username="admin", password="123")
            
            # Rooms
            room1 = Room(room_name="Room A", capacity=20)
            room2 = Room(room_name="Room B", capacity=15)
            room3 = Room(room_name="Room C", capacity=10)
            room4 = Room(room_name="Studio 1", capacity=25)
            
            # Classes
            class1 = FitnessClass(name="Yoga", description="A relaxing yoga class", duration=60)
            class2 = FitnessClass(name="Strength", description="Build your strength", duration=45)
            class3 = FitnessClass(name="Cardio", description="High intensity cardio workout", duration=30)
            class4 = FitnessClass(name="Pilates", description="Core strengthening pilates", duration=50)
            class5 = FitnessClass(name="HIIT", description="High Intensity Interval Training", duration=40)
            
            # Add to session
            session.add_all([member1, member2, member3, trainer1, trainer2, admin, 
                           room1, room2, room3, room4, class1, class2, class3, class4, class5])
            session.flush()  # Flush to assign IDs
            
            # Health Metrics
            health_metric1 = HealthMetric(member_id=member1.member_id, weight="100", height="180", bodyfat="25")
            health_metric2 = HealthMetric(member_id=member2.member_id, weight="80", height="175", bodyfat="15")
            health_metric3 = HealthMetric(member_id=member3.member_id, weight="70", height="170", bodyfat="10")
            

            # Trainer Availabilities
            availability1 = TrainerAvailability(
                trainer_id=trainer1.trainer_id,
                day_of_week="Monday",
                start_time=datetime.strptime("09:00", "%H:%M").time(),
                end_time=datetime.strptime("11:00", "%H:%M").time()
            )
            availability2 = TrainerAvailability(
                trainer_id=trainer2.trainer_id,
                day_of_week="Wednesday",
                start_time=datetime.strptime("14:00", "%H:%M").time(),
                end_time=datetime.strptime("16:00", "%H:%M").time()
            )

            availability4 = TrainerAvailability(
                trainer_id=trainer1.trainer_id,
                day_of_week="Friday",
                start_time=datetime.strptime("15:00", "%H:%M").time(),
                end_time=datetime.strptime("17:00", "%H:%M").time()
            )
            availability5 = TrainerAvailability(
                trainer_id=trainer2.trainer_id,
                day_of_week="Thursday",
                start_time=datetime.strptime("08:00", "%H:%M").time(),
                end_time=datetime.strptime("10:00", "%H:%M").time()
            )

            # Class Schedules - Multiple schedules for different days and times
            schedule1 = ClassSchedule(
                class_id=class1.class_id,
                room_id=room1.room_id,
                trainer_id=trainer1.trainer_id,
                day_of_week="Monday",
                start_time=datetime.strptime("09:00", "%H:%M").time(),
                end_time=datetime.strptime("10:00", "%H:%M").time(),
            )
            schedule2 = ClassSchedule(
                class_id=class2.class_id,
                room_id=room2.room_id,
                trainer_id=trainer2.trainer_id,
                day_of_week="Wednesday",
                start_time=datetime.strptime("14:00", "%H:%M").time(),
                end_time=datetime.strptime("14:45", "%H:%M").time(),
            )

            schedule4 = ClassSchedule(
                class_id=class4.class_id,
                room_id=room4.room_id,
                trainer_id=trainer1.trainer_id,
                day_of_week="Friday",
                start_time=datetime.strptime("15:00", "%H:%M").time(),
                end_time=datetime.strptime("15:50", "%H:%M").time(),
            )

            session.add_all([health_metric1, health_metric2, health_metric3,
                           availability1, availability2, availability4, availability5,
                           schedule1, schedule2, schedule4])
            session.flush()

            # Bookings - Some members have booked classes
            booking1 = Booking(member_id=member1.member_id, schedule_id=schedule1.schedule_id)
            booking2 = Booking(member_id=member2.member_id, schedule_id=schedule1.schedule_id)
            booking3 = Booking(member_id=member3.member_id, schedule_id=schedule2.schedule_id)
            

            # Delete availabilities that are now used by schedules
            session.delete(availability1)
            session.delete(availability2)

            session.delete(availability4)
            
            session.add_all([booking1, booking2, booking3])

            session.commit()
      
            
        except Exception as e:
            session.rollback()
            print(f"Error inserting sample data: {e}")
        finally:
            session.close()







# MEMBER OPERATIONS ------------------------------------------------------------------------------------
    def register_member(self, first, last, email, password, date_of_birth, gender, goal):
        session = self.get_session()
        try:
            new_member = Member(
                first_name=first, 
                last_name=last, 
                email=email, 
                password=password,
                date_of_birth=date_of_birth,
                gender=gender,
                fitness_goals=goal
            )
            session.add(new_member)
            session.commit()
            return new_member.member_id
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close()

    def member_login(self, email, password):
        session = self.get_session()
        try:
            # This query benefits from idx_member_email index for fast email lookup
            member = session.query(Member).filter_by(email=email, password=password).first()
            if member:
                return member.member_id
            return None
        except Exception as e:
            return str(e)
        finally:
            session.close()

    def get_member_profile(self, member_id):
        session = self.get_session()
        # Use the member_dashboard_view for optimized query
        result = session.execute(text("""
            SELECT member_id, first_name, last_name, fitness_goals, 
                   weight, height, bodyfat, recorded_at, total_bookings
            FROM member_dashboard_view
            WHERE member_id = :member_id
            ORDER BY recorded_at DESC
            LIMIT 1
        """), {"member_id": member_id}).fetchone()
        
        member = session.query(Member).filter_by(member_id=member_id).first()
        session.close()
        
        if result and member:
            # Create a simple object to hold health metrics for compatibility
            class HealthMetricData:
                def __init__(self, weight, height, bodyfat, recorded_at):
                    self.weight = weight
                    self.height = height
                    self.bodyfat = bodyfat
                    self.recorded_at = recorded_at
            
            health_metric = HealthMetricData(result[4], result[5], result[6], result[7]) if result[4] else None
            return (result[0], result[1], result[2], member.email, member.password, result[3], health_metric, result[8])
        return None
    
    def update_fitness_goals(self, member_id, new_goals):
        session = self.get_session()
        try:
            member = session.query(Member).filter_by(member_id=member_id).first()
            if member:
                member.fitness_goals = new_goals
                session.commit()
                return True
            return "Member not found"
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close()
    
    def update_personal_info(self, member_id, field, new_value):
        session = self.get_session()
        try:
            member = session.query(Member).filter_by(member_id=member_id).first()
            if member:
                if field == 'first_name':
                    member.first_name = new_value
                elif field == 'last_name':
                    member.last_name = new_value
                elif field == 'email':
                    member.email = new_value
                elif field == 'password':
                    member.password = new_value
                elif field == 'date_of_birth':
                    member.date_of_birth = new_value
                elif field == 'gender':
                    member.gender = new_value
                else:
                    return "Invalid field"
                
                session.commit()
                return True
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close()


    
    def add_health_metrics(self, member_id, new_metrics):
        session = self.get_session()
        try:
            metric = HealthMetric(
                member_id=member_id,
                weight=new_metrics.get('weight'),
                height=new_metrics.get('height'),
                bodyfat=new_metrics.get('bodyfat')
            )
            session.add(metric)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close()

    def get_member_bookings(self, member_id):
        session = self.get_session()
        # This query benefits from idx_booking_member index for fast member lookups
        results = session.query(Booking).join(ClassSchedule).join(FitnessClass).filter(Booking.member_id == member_id).all()
        
        data = []
        for b in results:
            data.append((b.booking_id,b.schedule.fitness_class.name, b.schedule.start_time, b.schedule.end_time))
        session.close()
        return data
    
    def cancel_booking(self, booking_id, member_id):
        session = self.get_session()
        try:
            booking = session.query(Booking).filter_by(booking_id=booking_id, member_id=member_id).first()
            if booking:
                session.delete(booking)
                session.commit()
                return True
            return "Booking not found"
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close()

    def book_class(self, member_id, schedule_id):
        session = self.get_session()
        try:
            # The trigger 'enforce_capacity' will automatically check room capacity
            # before allowing this booking to be inserted
            new_booking = Booking(member_id=member_id, schedule_id=schedule_id)
            session.add(new_booking)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            # The trigger will raise an exception if class is full
            return str(e)
        finally:
            session.close()

    def get_available_classes(self):
        session = self.get_session()
        schedules = session.query(ClassSchedule).join(FitnessClass).join(Room).all()
        
        data = []
        for entry in schedules:
            # Get current booking count for this schedule
            booking_count = session.query(Booking).filter_by(schedule_id=entry.schedule_id).count()
            capacity = entry.room.capacity
            available_spots = capacity - booking_count
            
            data.append((
                entry.schedule_id, 
                entry.fitness_class.name, 
                entry.room.room_name, 
                entry.start_time, 
                entry.end_time,
                f"{booking_count}/{capacity}",
                available_spots
            ))
        session.close()
        return data

    # TRAINER OPERATIONS ------------------------------------------------------------------------------------

    def register_trainer(self, first, last, email, password, specialization):
        session = self.get_session()
        try:
            new_trainer = Trainer(
                first_name=first, 
                last_name=last, 
                email=email, 
                password=password,
                specialization=specialization
            )
            session.add(new_trainer)
            session.commit()
            return new_trainer.trainer_id
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close()


    def trainer_login(self, email, password):
        session = self.get_session()
        try:
            trainer = session.query(Trainer).filter_by(email=email, password=password).first()
            if trainer:
                return trainer.trainer_id
            return "Invalid credentials"
        except Exception as e:
            return str(e)
        finally:
            session.close()
        

    def get_trainer_schedule(self, trainer_id):
        session = self.get_session()
        schedules = session.query(ClassSchedule).join(FitnessClass).join(Room).filter(ClassSchedule.trainer_id == trainer_id).all()
        
        data = []
        for s in schedules:
            data.append((s.fitness_class.name, s.room.room_name, s.start_time, s.end_time))
        session.close()
        return data
    
    def get_trainer_availability(self, trainer_id):
        session = self.get_session()
        availabilities = session.query(TrainerAvailability).filter(TrainerAvailability.trainer_id == trainer_id).all()
        
        data = []
        for a in availabilities:
            data.append((a.availability_id, a.day_of_week, a.start_time, a.end_time))
        session.close()
        return data
    def update_trainer_availability(self, availability_id, day_of_week, start_time, end_time):
        session = self.get_session()
        try:
            availability = session.query(TrainerAvailability).filter_by(availability_id=availability_id).first()
            if availability:
                availability.day_of_week = day_of_week
                availability.start_time = start_time
                availability.end_time = end_time
                session.commit()
                return True
            return "Availability not found"
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close() 
    def remove_trainer_availability(self, availability_id, trainer_id):
        session = self.get_session()
        try:
            availability = session.query(TrainerAvailability).filter_by(availability_id=availability_id, trainer_id=trainer_id).first()
            if availability:
                session.delete(availability)
                session.commit()
                return True
            return "Availability not found"
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close()
    def add_trainer_availability(self, trainer_id, day_of_week, start_time, end_time):
        session = self.get_session()
        try:
            availability = TrainerAvailability(
                trainer_id=trainer_id,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            )
            session.add(availability)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close()
    

    def search_member_by_name(self, firstname, lastname):
        session = self.get_session()
        member = session.query(Member).filter(
            or_(Member.first_name.ilike(f"%{firstname}%"), Member.last_name.ilike(f"%{lastname}%"))
        ).first()
        health_metric = session.query(HealthMetric).filter_by(member_id=member.member_id).order_by(HealthMetric.metric_id.desc()).first()
                
        if member:
            return (member.member_id, member.first_name, member.last_name, member.email, member.password, member.fitness_goals, health_metric)
        return None
      

    # ADMIN OPERATIONS ------------------------------------------------------------------------------------
    def admin_login(self, username, password):
        session = self.get_session()
        try:
            admin = session.query(Admin).filter_by(username=username, password=password).first()
            if admin:
                return True
            return False
        except Exception as e:
            return str(e)  
        finally:
            session.close()

    def add_class(self, name, description, duration):
        session = self.get_session()
        try:
            new_class = FitnessClass(
                name=name,
                description=description,
                duration=duration
            )
            session.add(new_class)
            session.commit()
            return new_class.class_id
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close()
    def remove_class(self, class_id):
        session = self.get_session()
        try:
            fitness_class = session.query(FitnessClass).filter_by(class_id=class_id).first()
            if fitness_class:
                session.delete(fitness_class)
                session.commit()
                return True
            return "Class not found"
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close()
    def get_all_classes(self):
        session = self.get_session()
        classes = session.query(FitnessClass).all()
        
        data = []
        for c in classes:
            data.append((c.class_id, c.name, c.description, c.duration))
        session.close()
        return data

    def get_all_rooms(self):
        session = self.get_session()
        rooms = session.query(Room).all()
        
        data = []
        for r in rooms:
            data.append((r.room_id, r.room_name, r.capacity))
        session.close()
        return data
    def add_room(self, room_name, capacity):
        session = self.get_session()
        try:
            new_room = Room(
                room_name=room_name,
                capacity=capacity
            )
            session.add(new_room)
            session.commit()
            return new_room.room_id
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close()

    def remove_room(self, room_id):
        session = self.get_session()
        try:
            room = session.query(Room).filter_by(room_id=room_id).first()
            if room:
                session.delete(room)
                session.commit()
                return True
            return "Room not found"
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close()

    def get_all_schedules(self):
        session = self.get_session()
        schedules = session.query(ClassSchedule).join(FitnessClass).join(Room).join(Trainer).all()
        
        data = []
        for s in schedules:
            data.append((s.schedule_id, s.fitness_class.name, s.room.room_name, f"{s.trainer.first_name} {s.trainer.last_name}", s.start_time, s.end_time))
        session.close()
        return data
    
    def remove_schedule(self, schedule_id):
        session = self.get_session()
        try:
            schedule = session.query(ClassSchedule).filter_by(schedule_id=schedule_id).first()
            if schedule:
                session.delete(schedule)
                # delete associated bookings
                bookings = session.query(Booking).filter_by(schedule_id=schedule_id).all()
                for booking in bookings:
                    session.delete(booking)
                session.commit()
                return True
            return "Schedule not found"
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close()
    
    def add_schedule(self, class_id, room_id, trainer_id, day_of_week, start_time, end_time):
        session = self.get_session()
        try:
            new_schedule = ClassSchedule(
                class_id=class_id,
                room_id=room_id,
                trainer_id=trainer_id,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            )
            session.add(new_schedule)
            # get trainer availability and delete
            availability = session.query(TrainerAvailability).filter(
                TrainerAvailability.trainer_id==trainer_id,
                TrainerAvailability.day_of_week==day_of_week,
                TrainerAvailability.start_time <= start_time,
                TrainerAvailability.end_time >= end_time
            ).first()
            if availability:
                session.delete(availability)
    
            session.commit()
            return new_schedule.schedule_id
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close()

    def get_available_trainers(self, day_of_week, start_time, end_time):
        session = self.get_session()
        # query trainers who are available during the given time
        # trainer availability should match day_of_week and be within start_time and end_time
        try:
            available_trainers = session.query(Trainer).join(TrainerAvailability).filter(
                TrainerAvailability.day_of_week == day_of_week,
                TrainerAvailability.start_time <= start_time,
                TrainerAvailability.end_time >= end_time
            ).all()
            data = []
            for t in available_trainers:
                data.append((t.trainer_id, t.first_name, t.last_name, t.specialization))
            session.close()
            return data
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close()


       
    def get_available_rooms(self, start_time, end_time):
        session = self.get_session()
        try:
            # query rooms that are not booked during the given time
            booked_room_ids = session.query(ClassSchedule.room_id).filter(
                or_(
                    ClassSchedule.start_time.between(start_time, end_time),
                    ClassSchedule.end_time.between(start_time, end_time),
                    and_(ClassSchedule.start_time <= start_time, ClassSchedule.end_time >= end_time)
                )
            ).scalar_subquery()
            available_rooms = session.query(Room).filter(~Room.room_id.in_(booked_room_ids)).all()
            data = []
            for r in available_rooms:
                data.append((r.room_id, r.room_name, r.capacity))
            session.close()
            return data
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close()

    def get_classes_by_duration(self, start_time, end_time):
        session = self.get_session()
        try:
            if isinstance(start_time, datetime):
                start_time = start_time.time()
            if isinstance(end_time, datetime):
                end_time = end_time.time()

            start_dt = datetime.combine(datetime.today(), start_time)
            end_dt = datetime.combine(datetime.today(), end_time)
            duration_minutes = (end_dt - start_dt).seconds / 60
            
            # query class that have a duration fitting within start_time and end_time
            classes = session.query(FitnessClass).filter(
                FitnessClass.duration <= duration_minutes
            ).all()
            data = []
            for c in classes:
                data.append((c.class_id, c.name, c.description, c.duration))
            session.close()
            return data
        except Exception as e:
            session.rollback()
            return str(e)
        finally:
            session.close()

    
    
        