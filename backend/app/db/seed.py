from datetime import date

from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.domain import Employee, Intervention, Role, TravelExpense, User


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        demo_users = [
            ("Administrateur CAIDELEC", "admin@caidelec.local", "admin123", Role.ADMIN),
            ("Reception CAIDELEC", "reception@caidelec.local", "reception123", Role.RECEPTION),
            ("Comptabilite CAIDELEC", "comptable@caidelec.local", "comptable123", Role.COMPTABLE),
            ("Manager CAIDELEC", "manager@caidelec.local", "manager123", Role.MANAGER),
        ]
        for full_name, email, password, role in demo_users:
            if not db.query(User).filter(User.email == email).first():
                db.add(
                    User(
                        full_name=full_name,
                        email=email,
                        password_hash=hash_password(password),
                        role=role,
                    )
                )

        if not db.query(Employee).first():
            employees = [
                Employee(full_name="Youssef Amrani", function="Technicien electricite", phone="0600000001"),
                Employee(full_name="Salma Bennani", function="Technicienne maintenance", phone="0600000002"),
                Employee(full_name="Hamza El Idrissi", function="Chef d'equipe", phone="0600000003"),
            ]
            db.add_all(employees)
            db.flush()

            intervention = Intervention(
                intervention_date=date.today(),
                client="Residence Al Amal",
                site="Casablanca - Ain Sebaa",
                mission="Diagnostic et remise en service tableau electrique",
                employee_id=employees[0].id,
                notes="Intervention prioritaire demandee par la reception.",
            )
            db.add(intervention)
            db.flush()
            db.add(
                TravelExpense(
                    intervention_id=intervention.id,
                    distance_km=32,
                    transport_amount=80,
                    meal_amount=40,
                    other_amount=0,
                )
            )

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
