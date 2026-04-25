from db import SessionLocal, Service

def add_service(name, description, price, price_type):
    session = SessionLocal()
    service = Service(
        name=name,
        description=description,
        price=price,
        price_type=price_type
    )
    session.add(service)
    session.commit()
    session.close()

def update_service(service_id, name, description, price, price_type):
    session = SessionLocal()
    service = session.query(Service).filter(Service.id == service_id).first()

    if service:
        service.name = name
        service.description = description
        service.price = price
        service.price_type = price_type
        session.commit()

    session.close()

def get_services():
    session = SessionLocal()
    services = session.query(Service).all()
    session.close()
    return services