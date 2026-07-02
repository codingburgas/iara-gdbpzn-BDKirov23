from app import create_app, db
from app.models.user import User
from app.models.team import Team, FireTruck, TeamMember, Shift
from app.models.incident import IncidentType, HazardousMaterial
from app.models.chat import ChatTemplate
from app.models.resource import Resource
from datetime import time

app = create_app()

with app.app_context():
    db.create_all()

    if User.query.first():
        print("Database already seeded.")
        exit(0)

    admin = User(
        email="admin@gdpbzn.bg",
        first_name="Admin",
        last_name="System",
        rank="Commissioner",
        role="admin",
    )
    admin.set_password("admin123")
    db.session.add(admin)

    dispatcher = User(
        email="dispatcher@gdpbzn.bg",
        first_name="Ivan",
        last_name="Dispatcherov",
        rank="Inspector",
        role="dispatcher",
    )
    dispatcher.set_password("disp123")
    db.session.add(dispatcher)

    commander = User(
        email="commander@gdpbzn.bg",
        first_name="Georgi",
        last_name="Komandirov",
        rank="Chief Inspector",
        role="commander",
    )
    commander.set_password("com123")
    db.session.add(commander)

    ff1 = User(
        email="firefighter1@gdpbzn.bg",
        first_name="Petar",
        last_name="Petrov",
        phone="0888123456",
        rank="Senior Firefighter",
        role="firefighter",
    )
    ff1.set_password("ff123")
    db.session.add(ff1)

    ff2 = User(
        email="firefighter2@gdpbzn.bg",
        first_name="Dimitar",
        last_name="Dimitrov",
        phone="0888123457",
        rank="Firefighter",
        role="firefighter",
    )
    ff2.set_password("ff123")
    db.session.add(ff2)

    ff3 = User(
        email="firefighter3@gdpbzn.bg",
        first_name="Nikolay",
        last_name="Nikolov",
        phone="0888123458",
        rank="Firefighter",
        role="firefighter",
    )
    ff3.set_password("ff123")
    db.session.add(ff3)

    addl_users = [
        ("firefighter4@gdpbzn.bg", "Hristo", "Hristov", "0888123459", "Senior Firefighter", "firefighter"),
        ("firefighter5@gdpbzn.bg", "Mariya", "Ivanova", "0888123460", "Firefighter", "firefighter"),
        ("firefighter6@gdpbzn.bg", "Vasil", "Vasilev", "0888123461", "Firefighter", "firefighter"),
        ("firefighter7@gdpbzn.bg", "Todor", "Todorov", "0888123462", "Senior Firefighter", "firefighter"),
        ("firefighter8@gdpbzn.bg", "Elena", "Petrova", "0888123463", "Firefighter Paramedic", "firefighter"),
        ("firefighter9@gdpbzn.bg", "Stoyan", "Stoyanov", "0888123464", "Firefighter", "firefighter"),
        ("firefighter10@gdpbzn.bg", "Krasimir", "Krasimirov", "0888123465", "Senior Firefighter", "firefighter"),
        ("firefighter11@gdpbzn.bg", "Daniel", "Danov", "0888123466", "Firefighter", "firefighter"),
        ("firefighter12@gdpbzn.bg", "Petq", "Petrova", "0888123467", "Firefighter Paramedic", "firefighter"),
        ("firefighter13@gdpbzn.bg", "Rumen", "Rumenov", "0888123468", "Firefighter", "firefighter"),
        ("firefighter14@gdpbzn.bg", "Svetla", "Svetlinova", "0888123469", "Firefighter", "firefighter"),
        ("firefighter15@gdpbzn.bg", "Valeri", "Valeriev", "0888123470", "Senior Firefighter", "firefighter"),
    ]
    for email, fn, ln, phone, rank, role in addl_users:
        u = User(email=email, first_name=fn, last_name=ln, phone=phone, rank=rank, role=role)
        u.set_password("ff123")
        db.session.add(u)

    truck1 = FireTruck(
        registration_number="PB-1234",
        model="Mercedes Atego",
        type="fire_engine",
        capacity=6,
        gps_device_id="GPS-001",
    )
    db.session.add(truck1)

    truck2 = FireTruck(
        registration_number="PB-5678",
        model="MAN TGM",
        type="water_tanker",
        capacity=3,
        gps_device_id="GPS-002",
        photo_url="https://img.freepik.com/free-photo/fire-truck-city-street_107791-1991.jpg",
        year_manufactured=2019, mileage_km=45200, water_tank_l=10000, foam_tank_l=500,
    )
    db.session.add(truck2)

    truck3 = FireTruck(
        registration_number="PB-9012",
        model="Mercedes Arocs",
        type="turntable_ladder",
        capacity=3,
        gps_device_id="GPS-003",
        photo_url="https://i.imgur.com/6qEMmUK.jpg",
        year_manufactured=2021, mileage_km=18900, water_tank_l=500, foam_tank_l=200,
    )
    truck4 = FireTruck(
        registration_number="PB-3456",
        model="Iveco Magirus",
        type="aerial_platform",
        capacity=4,
        gps_device_id="GPS-004",
        photo_url="https://i.imgur.com/QvFzdYn.jpg",
        year_manufactured=2020, mileage_km=31200, water_tank_l=400, foam_tank_l=200,
    )
    truck5 = FireTruck(
        registration_number="PB-7890",
        model="Scania P410",
        type="rescue_vehicle",
        capacity=6,
        gps_device_id="GPS-005",
        photo_url="https://i.imgur.com/6RFkHSk.jpg",
        year_manufactured=2022, mileage_km=8900, water_tank_l=200, foam_tank_l=100,
    )
    truck6 = FireTruck(
        registration_number="PB-1111",
        model="Ford Ranger",
        type="command_vehicle",
        capacity=5,
        gps_device_id="GPS-006",
        photo_url="https://i.imgur.com/w7EFCdC.jpg",
        year_manufactured=2023, mileage_km=5200, water_tank_l=0, foam_tank_l=0,
    )
    db.session.add_all([truck3, truck4, truck5, truck6])

    team1 = Team(name="Alpha Team", fire_truck_id=1, station="Sofia Central")
    db.session.add(team1)

    team2 = Team(name="Bravo Team", fire_truck_id=2, station="Sofia Central")
    db.session.add(team2)

    team3 = Team(name="Charlie Team", fire_truck_id=3, station="Sofia South")
    team4 = Team(name="Delta Team", fire_truck_id=4, station="Sofia North")
    team5 = Team(name="Echo Team", fire_truck_id=5, station="Sofia East")
    db.session.add_all([team3, team4, team5])

    shift_morning = Shift(
        name="Morning Shift",
        start_time=time(6, 0),
        end_time=time(14, 0),
    )
    db.session.add(shift_morning)

    shift_afternoon = Shift(
        name="Afternoon Shift",
        start_time=time(14, 0),
        end_time=time(22, 0),
    )
    db.session.add(shift_afternoon)

    shift_night = Shift(
        name="Night Shift",
        start_time=time(22, 0),
        end_time=time(6, 0),
    )
    db.session.add(shift_night)

    db.session.flush()

    tm1 = TeamMember(user_id=3, team_id=1, is_team_leader=True, is_on_shift=True)
    tm2 = TeamMember(user_id=4, team_id=1, is_on_shift=True)
    tm3 = TeamMember(user_id=2, team_id=2, is_team_leader=True, is_on_shift=True)
    tm4 = TeamMember(user_id=5, team_id=2, is_on_shift=True)
    tm5 = TeamMember(user_id=6, team_id=1, is_on_shift=True)
    tm6 = TeamMember(user_id=7, team_id=2, is_on_shift=True)
    tm7 = TeamMember(user_id=8, team_id=3, is_team_leader=True, is_on_shift=True)
    tm8 = TeamMember(user_id=9, team_id=3, is_on_shift=True)
    tm9 = TeamMember(user_id=10, team_id=3, is_on_shift=True)
    tm10 = TeamMember(user_id=11, team_id=4, is_team_leader=True, is_on_shift=True)
    tm11 = TeamMember(user_id=12, team_id=4, is_on_shift=True)
    tm12 = TeamMember(user_id=13, team_id=4, is_on_shift=True)
    tm13 = TeamMember(user_id=14, team_id=5, is_team_leader=True, is_on_shift=True)
    tm14 = TeamMember(user_id=15, team_id=5, is_on_shift=True)
    tm15 = TeamMember(user_id=16, team_id=5, is_on_shift=True)
    tm16 = TeamMember(user_id=17, team_id=1, is_on_shift=False)
    tm17 = TeamMember(user_id=18, team_id=2, is_on_shift=False)
    db.session.add_all([tm1, tm2, tm3, tm4, tm5, tm6, tm7, tm8, tm9, tm10, tm11, tm12, tm13, tm14, tm15, tm16, tm17])

    types = [
        ("Building Fire", "FIRE-BLDG", "fire", "Structure fire in buildings"),
        ("Forest Fire", "FIRE-FOREST", "fire", "Forest and wildland fires"),
        ("Vehicle Fire", "FIRE-VEH", "fire", "Vehicle fires"),
        ("Traffic Accident", "RESCUE-TRAFFIC", "rescue", "Traffic accidents with trapped persons"),
        ("Technical Rescue", "RESCUE-TECH", "rescue", "Technical rescues"),
        ("Medical Emergency", "MEDICAL", "medical", "Medical emergencies"),
        ("HazMat Spill", "HAZMAT", "hazmat", "Hazardous material spills"),
        ("Flood", "NATURAL-FLOOD", "natural", "Flooding incidents"),
        ("Earthquake", "NATURAL-EQ", "natural", "Earthquake response"),
        ("False Alarm", "OTHER-FALSE", "other", "False alarms"),
    ]
    for name, code, cat, desc in types:
        db.session.add(IncidentType(name=name, code=code, category=cat, description=desc))

    materials = [
        ("Chlorine", "UN1017", "2.3", "Toxic gas", "Use SCBA. Evacuate downwind. Water spray to disperse."),
        ("Ammonia", "UN1005", "2.3", "Toxic gas", "Use SCBA. Avoid contact with liquid."),
        ("Gasoline", "UN1203", "3", "Flammable liquid", "Use foam. No water on burning liquid."),
        ("Propane", "UN1978", "2.1", "Flammable gas", "Evacuate. Stop leak if safe. Cool containers with water."),
        ("Sulfuric Acid", "UN1830", "8", "Corrosive liquid", "Use acid-resistant PPE. Neutralize with lime/soda ash."),
    ]
    for name, un, hclass, desc, instr in materials:
        db.session.add(HazardousMaterial(
            name=name, un_number=un, hazard_class=hclass,
            description=desc, handling_instructions=instr,
        ))

    templates = [
        ("arrival_notification", "Team arrived on scene."),
        ("arrival_notification", "En route to location. ETA 10 minutes."),
        ("status_update", "Fire is contained. Continuing with cooling operations."),
        ("status_update", "Requesting backup. Situation escalating."),
        ("resource_request", "Requesting additional water tanker."),
        ("resource_request", "Need more foam concentrate."),
        ("emergency", "MAYDAY - Firefighter down at my location!"),
        ("emergency", "Need immediate medical assistance."),
        ("coordination", "Setting up command post at the north entrance."),
        ("coordination", "Establishing water supply from hydrant at corner."),
        ("general", "Copy that."),
        ("general", "Standing by for further instructions."),
    ]
    for cat, text in templates:
        db.session.add(ChatTemplate(category=cat, message_text=text))

    if not Resource.query.first():
        resources = [
            ("Вода", "water", 50000, "L", "Централен резервоар - София"),
            ("Вода", "water", 30000, "L", "Резервоар Пловдив"),
            ("Вода", "water", 20000, "L", "Резервоар Варна"),
            ("Дизелово гориво", "fuel", 5000, "L", "Горивна база София"),
            ("Бензин", "fuel", 2000, "L", "Горивна база София"),
            ("Пяна AFFF 3%", "foam", 5000, "L", "Склад София"),
            ("Пяна AFFF 6%", "foam", 3000, "L", "Склад Пловдив"),
            ("Суха пяна", "foam", 2000, "kg", "Склад Варна"),
            ("Пожарен маркуч 52mm", "equipment", 50, "бр", "Склад София"),
            ("Пожарен маркуч 75mm", "equipment", 30, "бр", "Склад Пловдив"),
            ("Стрък 52mm", "equipment", 20, "бр", "Склад Варна"),
            ("Стрък 75mm", "equipment", 15, "бр", "Склад София"),
            ("Въздушно-дихателен апарат", "equipment", 25, "бр", "Склад София"),
            ("Дихателна маска", "equipment", 50, "бр", "Логистичен център"),
            ("Защитен костюм", "equipment", 40, "бр", "Логистичен център"),
            ("Каска", "equipment", 60, "бр", "Логистичен център"),
            ("Ръкавици", "equipment", 200, "чифта", "Логистичен център"),
            ("Аптечка", "medical", 30, "бр", "Медицински склад"),
            ("Носилка", "medical", 15, "бр", "Медицински склад"),
            ("Дефибрилатор", "medical", 5, "бр", "Медицински склад"),
            ("Питейна вода", "food", 1000, "бутилки", "Склад София"),
            ("Сухи хранителни пакети", "food", 500, "бр", "Склад София"),
        ]
        for name, rtype, qty, unit, loc in resources:
            db.session.add(Resource(name=name, resource_type=rtype, quantity_available=qty, unit=unit, storage_location=loc, is_consumable=(rtype not in ("vehicle",))))

    db.session.commit()
    print("Database seeded successfully!")
    print("Admin: admin@gdpbzn.bg / admin123")
    print("Dispatcher: dispatcher@gdpbzn.bg / disp123")
    print("Commander: commander@gdpbzn.bg / com123")
    print("Firefighters: firefighter1-3@gdpbzn.bg / ff123")
