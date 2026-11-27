import uuid
import random

from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import select, func

from src.database.connection import SessionLocal
from src.database.models import (
    Guest,
    RoomType,
    Room,
    Reservation,
    ServiceRequest,
)


ROOM_TYPES = [
    ("Standard", 60, 2, 40, ["Wi-Fi", "AC", "TV"]),
    ("Deluxe", 100, 2, 30, ["Wi-Fi", "AC", "TV", "Mini Bar"]),
    ("Ocean View", 150, 3, 20, ["Wi-Fi", "AC", "Ocean View", "Balcony"]),
    ("Family Suite", 200, 4, 8, ["Wi-Fi", "AC", "Living Area", "Kitchen"]),
    ("Presidential Suite", 350, 4, 2, ["Wi-Fi", "AC", "Jacuzzi", "Ocean View"]),
]


GUEST_NAMES = [
    "Kavindu Perera",
    "Nethmi Jayasinghe",
    "Tharindu Fernando",
    "Sahan Bandara",
    "Harini Rajendran",
    "Arjun Sivakumar",
    "Mohamed Rizwan",
    "Ayesha Farook",
    "Kasun Silva",
    "Sanduni Wijesinghe",
    "Isuru Herath",
    "Dilini Gunawardena",
    "Chathura Senanayake",
    "Amaya De Silva",
    "Dinuka Rathnayake",
    "Sachini Dissanayake",
    "Pasindu Wickramasinghe",
    "Hiruni Abeysekara",
    "Ravindu Madushanka",
    "Shenali Rodrigo",
    "Nipun Karunaratne",
    "Thilini Samarasinghe",
    "Ashan Jayawardena",
    "Kavindya Ekanayake",
    "Lahiru Weerasinghe",
    "Piumi Hettiarachchi",
    "Malith Gamage",
    "Ishara Kumari",
    "Supun Ranasinghe",
    "Anjali Pathirana",
    "Karthik Yogarajah",
    "Priya Tharmalingam",
    "Suresh Balasubramaniam",
    "Janani Krishnan",
    "Naveen Selvarajah",
    "Divya Nadarajah",
    "Vijay Shanmugam",
    "Anusha Ramanathan",
    "Dinesh Kanagaratnam",
    "Meena Sivarajah",
    "Ahmed Nazeer",
    "Fathima Zahra",
    "Abdul Rahman",
    "Amina Hassan",
    "Mohamed Imran",
    "Zainab Ali",
    "Rizwan Hameed",
    "Safiya Ismail",
    "Azhar Saleem",
    "Maryam Rauf",
]


SERVICE_EXAMPLES = [
    ("room_service", "Send a Sri Lankan rice and curry lunch."),
    ("room_service", "Order string hoppers and coconut sambol."),
    ("room_service", "Send two cups of Ceylon tea."),
    ("room_service", "Order vegetable kottu for dinner."),
    ("transport", "Arrange a taxi to Bandaranaike International Airport."),
    ("transport", "Arrange transport to Colombo Fort."),
    ("housekeeping", "Clean the room before we return from Negombo Beach."),
    ("housekeeping", "Please change the bed sheets."),
    ("amenities", "Send two additional towels."),
    ("amenities", "Provide an extra bottle of drinking water."),
    ("maintenance", "The air conditioner is not working."),
    ("maintenance", "The television remote is not working."),
    ("room_service", "Send a traditional Sri Lankan breakfast."),
    ("room_service", "Send two fresh king coconut drinks."),
    ("transport", "Arrange a taxi to Negombo town."),
    ("housekeeping", "Please clean the bathroom."),
    ("amenities", "Provide an additional pillow."),
    ("maintenance", "The Wi-Fi connection is unstable."),
    ("other", "Request a late checkout."),
    ("other", "Request information about a Muthurajawela boat tour."),
]

def generate_phone_number():

    prefix = random.choice([
        "70", "71", "72", "74",
        "75", "76", "77", "78"
    ])

    number = random.randint(1000000, 9999999)

    return f"+94{prefix}{number}"

def seed_room_types(db):

    room_types = []

    for name, price, capacity, quantity, amenities in ROOM_TYPES:

        room_type = db.scalar(
            select(RoomType).where(RoomType.name == name)
        )

        if room_type is None:

            room_type = RoomType(
                name=name,
                description=f"{name} accommodation at Azure Bay Resort.",
                price_per_night=Decimal(str(price)),
                max_guests=capacity,
                amenities=amenities,
            )

            db.add(room_type)
            db.flush()

        room_types.append((room_type, quantity))

    print("Room types ready:", len(room_types))

    return room_types


def seed_rooms(db, room_types):

    rooms = []

    for floor, (room_type, quantity) in enumerate(room_types, start=1):

        for number in range(1, quantity + 1):

            room_number = f"{floor}{number:02d}"

            room = db.scalar(
                select(Room).where(Room.room_number == room_number)
            )

            if room is None:

                room = Room(
                    room_number=room_number,
                    room_type_id=room_type.id,
                    floor=floor,
                    status="active",
                )

                db.add(room)
                db.flush()

            rooms.append((room, room_type))

    print("Rooms ready:", len(rooms))

    return rooms


def seed_guests(db):

    guests = []

    for name in GUEST_NAMES:

        email = name.lower().replace(" ", ".") + "@example.com"

        guest = db.scalar(
            select(Guest).where(Guest.email == email)
        )

        if guest is None:

            guest = Guest(
                full_name=name,
                email=email,
                phone=generate_phone_number(),
            )

            db.add(guest)
            db.flush()

        elif guest.phone is None or guest.phone.startswith("+9400"):

            guest.phone = generate_phone_number()

        guests.append(guest)

    print("Guests ready:", len(guests))

    return guests


def seed_reservations(db, guests, rooms):

    reservations = []

    today = datetime.now(ZoneInfo("Asia/Colombo")).date()

    for i in range(30):

        reference = f"SP-DEMO-{i + 1:03d}"

        reservation = db.scalar(
            select(Reservation).where(
                Reservation.booking_reference == reference
            )
        )

        if reservation is None:

            # Spread reservations across the hotel.
            room, room_type = rooms[i * 3]

            if i < 10:

                status = "checked_in"
                check_in = today - timedelta(days=1)
                check_out = today + timedelta(days=2)

            elif i < 25:

                status = "confirmed"
                check_in = today + timedelta(days=i - 8)
                check_out = check_in + timedelta(days=3)

            else:

                status = "cancelled"
                check_in = today + timedelta(days=5)
                check_out = check_in + timedelta(days=2)

            nights = (check_out - check_in).days

            reservation = Reservation(
                booking_reference=reference,
                guest_id=guests[i].id,
                room_id=room.id,
                check_in=check_in,
                check_out=check_out,
                num_guests=2,
                price_per_night=room_type.price_per_night,
                total_price=room_type.price_per_night * nights,
                status=status,
            )

            db.add(reservation)
            db.flush()

        reservations.append(reservation)

    print("Reservations ready:", len(reservations))

    return reservations


def seed_service_requests(db, reservations):

    for i, (service_type, description) in enumerate(SERVICE_EXAMPLES):

        request_id = uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"staypilot-demo-service-{i + 1}"
        )

        existing = db.get(ServiceRequest, request_id)

        if existing is not None:
            continue

        request = ServiceRequest(
            id=request_id,
            reservation_id=reservations[i % 10].id,
            service_type=service_type,
            description=description,
            status=["pending", "in_progress", "completed"][i % 3],
        )

        db.add(request)

    print("Service requests ready:", len(SERVICE_EXAMPLES))


def main():

    with SessionLocal() as db:

        try:

            room_types = seed_room_types(db)
            rooms = seed_rooms(db, room_types)
            guests = seed_guests(db)

            reservations = seed_reservations(
                db, guests, rooms
            )

            seed_service_requests(db, reservations)

            db.commit()

            print("\nDatabase seeding completed successfully!")

            print("\nDatabase summary")
            print("-" * 35)

            for model in [
                RoomType,
                Room,
                Guest,
                Reservation,
                ServiceRequest,
            ]:

                count = db.scalar(
                    select(func.count()).select_from(model)
                )

                print(f"{model.__tablename__}: {count}")

        except Exception:

            db.rollback()
            raise


if __name__ == "__main__":
    main()
