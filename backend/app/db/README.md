# Model Development: Development Notes and developer rationales

*This is written, assuming the fact that the reader is not aware of the tech stacks use cases, and the writer is arguing on why they are using the stacks that has been used. Hence, the rationale on the writers part.*


**SQLAlchemy** is a python based object relationship mapper, which maps python classes to a databases tables. whereas **Alembic** is a migration tool that tracks changes in SQLAlchemy models and generates versioned scripts to update actual database schema. it checks current DB state vs SQLAlchemy and generates a new script for reflecting the changes in the app/db/models.

## How it works?

- `Base = declarative_base()` in `base.py`: This tells SQLAlchemy we're creating ORM models.
- Models subclass `Base`, which is used by Alembic to understand the DB schema.
- `engine = create_engine(...)` in `session.py`: This sets up the connection to the DB.
- `SessionLocal = sessionmaker(bind=engine)` creates actual sessions to talk to the DB.
- When we `alembic upgrade head`, Alembic runs the generated migration script, which uses raw SQL under the hood.

## Best Practices When Writing Models


| Best Practice                       | Reason                              |
| ----------------------------------- | ----------------------------------- |
| shared base in `base.py`            | Centralizes Base & metadata         |
| `index=True` for lookup fields      | Speeds up queries                   |
| avoid circular imports              | Split model relationships carefully |
| use `__tablename__`                 | Explicit is better than implicit    |
| separate models from schemas        | Keeps domain logic clean            |
| nullable=False` where required      | Enforces data constraints           |


**Circular Imports** happen often in SQLAlchemy due to bidirectional relationships using `ForeignKey` and `relationship()` in separate model files.

### Bad Example

```bash
# user.py
class User(Base):
    songs = relationship("Song", back_populates="artist")

# song.py
class Song(Base):
    artist_id = Column(Integer, ForeignKey("user.id"))
    artist = relationship("User", back_populates="songs")

```

This one has circular import and dependency on one another, a better way of doing it and avoiding circular import that i have used and implemented is:

- String based Reference:
    ```bash
    artist = relationship("User", back_populates="songs")  # NOT relationship(User)

    ```
    We don’t need to import the actual class (e.g. from user import User), 


- group models andput them into same files instead of multiple files. SQLAlchemy stores the model names as strings, Later, after all models are loaded, it matches those strings to actual classes


## My Decision and rationale

I would use one file per data model, because as its a bigger database with multiple tables, separation of code by models would be helpful in the long run for maintaining the code, Hence to remove the issue of circular imports, I would be adhering to two different methods, one is using strings in writing relationships instead of actually importing the class with which the current code has a relationship. Next up, is instead of importing a class at the begining, i would load it only inside a function when needed. That is do function locale import.  

Example:

```bash
# Not to be done ->
from app.db.models.playlist import Playlist



# To be done ->
def get_user_playlists(user_id: int):
    from app.db.models.playlist import Playlist
    return db.query(Playlist).filter(Playlist.user_id == user_id).all()

```

Conventions I used :

- using __tablename__ explicitly, even though SQL Alchemy can infer it 
- using __repr__() or __str__() for Debugging.

    ```bash
    def __repr__(self):
    return f"<User id={self.id} username={self.username}>"

    ```
- defined __table_args__ for Constraints & Indexes
- soft dleetion for audit log
- audit fields (Timestamps) like `created_at` and `deleted_at`
- using Relationships Carefully, always defining backrefs or back_populates if needed\
- kinda avoided loading everything by default (lazy="select" is safe) and being clear when to use uselist=False for one-to-one
- avoided Importing DB Session in Models
- Used UUIDs if security is needed, don't want to expose (e.g. user IDs). eg:

```bash
import uuid
from sqlalchemy.dialects.postgresql import UUID
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

```
- not storing raw strings when it should be restricted instead used Python enum.Enum:
```bash
class UserRole(str, enum.Enum):
    superadmin = "superadmin"
    singer = "singer"
    listener = "listener"

role = Column(Enum(UserRole), nullable=False)

```
- prefixing foreign keys consistently, such as instead of just user_id, using created_by_user_id, owner_user_id, etc.
- seeding for roles, plans, doing it safely so that it inserts default values with `INSERT ... ON CONFLICT DO NOTHING`

### To be Seeded

| Table                                                     | Why?                                                                            |
| --------------------------------------------------------- | ------------------------------------------------------------------------------- |
| **Genre**                                                 | Needed to classify songs. Static values that don’t change often.                |
| **SubscriptionPlan**                                      | Plans must exist so users can subscribe.                                        |
| **User**                                                  | For admin/superadmin login. Needed for app management and seed tracking.        |
| **SystemConfig**                                          | App-wide feature toggles or settings. May control limits, features, or toggles. |
| **Localization**                                          | For multi-language UI text keys required to support localization.               |
| **PaymentMethod** _(If model not enum)_ [Future Plan]     | Needed to support different payment types                                       |
