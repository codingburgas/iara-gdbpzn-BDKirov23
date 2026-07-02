from app import create_app, db
from app.models.team import FireTruck, Team

app = create_app()

with app.app_context():
    existing = FireTruck.query.count()
    if existing > 2:
        print(f"Already have {existing} trucks. Skipping.")
        exit(0)

    import sqlalchemy as sa
    insp = sa.inspect(db.engine)
    columns = [c["name"] for c in insp.get_columns("fire_trucks")]
    kwargs = {}
    if "photo_url" in columns:
        kwargs["photo_url"] = "https://i.imgur.com/6qEMmUK.jpg"

    trucks = [
        FireTruck(
            registration_number="PB-9012",
            model="Mercedes Arocs",
            type="turntable_ladder",
            capacity=3,
            gps_device_id="GPS-003",
            photo_url="https://i.imgur.com/6qEMmUK.jpg" if "photo_url" in columns else None,
            year_manufactured=2021, mileage_km=18900, water_tank_l=500, foam_tank_l=200,
        ),
        FireTruck(
            registration_number="PB-3456",
            model="Iveco Magirus",
            type="aerial_platform",
            capacity=4,
            gps_device_id="GPS-004",
            photo_url="https://i.imgur.com/QvFzdYn.jpg" if "photo_url" in columns else None,
            year_manufactured=2020, mileage_km=31200, water_tank_l=400, foam_tank_l=200,
        ),
        FireTruck(
            registration_number="PB-7890",
            model="Scania P410",
            type="rescue_vehicle",
            capacity=6,
            gps_device_id="GPS-005",
            photo_url="https://i.imgur.com/6RFkHSk.jpg" if "photo_url" in columns else None,
            year_manufactured=2022, mileage_km=8900, water_tank_l=200, foam_tank_l=100,
        ),
        FireTruck(
            registration_number="PB-1111",
            model="Ford Ranger",
            type="command_vehicle",
            capacity=5,
            gps_device_id="GPS-006",
            photo_url="https://i.imgur.com/w7EFCdC.jpg" if "photo_url" in columns else None,
            year_manufactured=2023, mileage_km=5200, water_tank_l=0, foam_tank_l=0,
        ),
    ]
    db.session.add_all(trucks)
    db.session.flush()

    teams = Team.query.all()
    truck_ids = [t.id for t in FireTruck.query.all()]
    for i, team in enumerate(teams):
        if i < len(truck_ids):
            team.fire_truck_id = truck_ids[i]
            print(f"  Assigned truck {truck_ids[i]} to {team.name}")

    db.session.commit()
    print(f"\nDone! Total trucks: {FireTruck.query.count()}")
