from kaihelper.domain.core.database import Base, engine
from kaihelper.domain.models.user import User

def init_db():
    Base.metadata.create_all(bind=engine)
    
if __name__ == "__main__":
    init_db()
