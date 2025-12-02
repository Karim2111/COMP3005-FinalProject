from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Time,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Member(Base):
    __tablename__ = "member"

    member_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    date_of_birth = Column(String)
    gender = Column(String)
    fitness_goals = Column(String)

    # relationships
    bookings = relationship("Booking", back_populates="member")
    health_metrics = relationship("HealthMetric", back_populates="member")


class Booking(Base):
    __tablename__ = "booking"

    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("member.member_id"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("class_schedule.schedule_id"), nullable=False)


    member = relationship("Member", back_populates="bookings")
    schedule = relationship("ClassSchedule", back_populates="bookings")


class HealthMetric(Base):
    __tablename__ = "health_metric"

    metric_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("member.member_id"), nullable=False)
    weight = Column(String)
    height = Column(String)
    bodyfat = Column(String)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    member = relationship("Member", back_populates="health_metrics")


class FitnessClass(Base):
    __tablename__ = "fitness_class"

    class_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    duration = Column(Integer, nullable=False)  

    schedules = relationship("ClassSchedule", back_populates="fitness_class")


class Trainer(Base):
    __tablename__ = "trainer"

    trainer_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    specialization = Column(String)
    password = Column(String, nullable=False)

    schedules = relationship("ClassSchedule", back_populates="trainer")
    availabilities = relationship("TrainerAvailability", back_populates="trainer")


class TrainerAvailability(Base):
    __tablename__ = "trainer_availability"

    availability_id = Column(Integer, primary_key=True, autoincrement=True)
    trainer_id = Column(Integer, ForeignKey("trainer.trainer_id"), nullable=False)
    day_of_week = Column(String, nullable=False)  
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    trainer = relationship("Trainer", back_populates="availabilities")


class ClassSchedule(Base):
    __tablename__ = "class_schedule"

    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("fitness_class.class_id"), nullable=False)
    room_id = Column(Integer, ForeignKey("room.room_id"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("trainer.trainer_id"), nullable=False)
    day_of_week = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    fitness_class = relationship("FitnessClass", back_populates="schedules")
    room = relationship("Room", back_populates="schedules")
    trainer = relationship("Trainer", back_populates="schedules")
    bookings = relationship("Booking", back_populates="schedule")


class Room(Base):
    __tablename__ = "room"

    room_id = Column(Integer, primary_key=True, autoincrement=True)
    room_name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)

    schedules = relationship("ClassSchedule", back_populates="room")


class Admin(Base):
    __tablename__ = "admin"

    admin_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
