from app import create_app, db
from app.models.user import User
from app.models.team import Team, TeamMember
from datetime import time

app = create_app()

with app.app_context():
    existing = User.query.filter(User.email.like("firefighter%@gdpbzn.bg")).count()
    if existing > 5:
        print(f"Already have {existing} firefighters. Skipping.")
        exit(0)

    addl = [
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

    user_ids = []
    for email, fn, ln, phone, rank, role in addl:
        if User.query.filter_by(email=email).first():
            print(f"  {email} already exists")
            continue
        u = User(email=email, first_name=fn, last_name=ln, phone=phone, rank=rank, role=role)
        u.set_password("ff123")
        db.session.add(u)
        db.session.flush()
        user_ids.append(u.id)
        print(f"  + {fn} {ln} ({email})")

    team3 = Team.query.filter_by(name="Charlie Team").first()
    team4 = Team.query.filter_by(name="Delta Team").first()
    team5 = Team.query.filter_by(name="Echo Team").first()
    team1 = Team.query.filter_by(name="Alpha Team").first()
    team2 = Team.query.filter_by(name="Bravo Team").first()

    if not team3:
        team3 = Team(name="Charlie Team", fire_truck_id=1, station="Sofia South")
        team4 = Team(name="Delta Team", fire_truck_id=2, station="Sofia North")
        team5 = Team(name="Echo Team", fire_truck_id=1, station="Sofia East")
        db.session.add_all([team3, team4, team5])
        db.session.flush()
        print("  + Added teams: Charlie, Delta, Echo")

    memberships = [
        (6, team1.id if team1 else 1, False), (7, team2.id if team2 else 2, False),
        (8, team3.id, True), (9, team3.id, False), (10, team3.id, False),
        (11, team4.id, True), (12, team4.id, False), (13, team4.id, False),
        (14, team5.id, True), (15, team5.id, False), (16, team5.id, False),
        (17, team1.id if team1 else 1, False), (18, team2.id if team2 else 2, False),
    ]

    for uid, tid, is_leader in memberships:
        if not TeamMember.query.filter_by(user_id=uid, team_id=tid).first():
            tm = TeamMember(user_id=uid, team_id=tid, is_team_leader=is_leader, is_on_shift=True)
            db.session.add(tm)

    db.session.commit()
    total = User.query.filter(User.role == "firefighter").count()
    print(f"\nDone! Total firefighters: {total}")
    print("All passwords: ff123")
