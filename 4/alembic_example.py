
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    age = Column(Integer)

    posts = relationship('Post', back_populates='author', cascade='all, delete-orphan')


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    author = relationship('User', back_populates='posts')

engine = create_engine('postgresql://postgres:pwd@localhost:5432/test')
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from contextlib import contextmanager
@contextmanager
def get_session():
    session = session_local()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(f'Error: {e}')
        raise
    finally:
        session.close()

def create_user(
        age: int,
        name: str,
        email: str,
):
    new_user = User(
        name=name,
        email=email,
        age=age,
    )
    with get_session() as session:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        print(f'Created user: {new_user.id}')


def create_post(
        title: str,
        content: str,
        user_id: int,
):
    new_post = Post(
        title=title,
        content=content,
        user_id=user_id,
    )
    with get_session() as session:
        session.add(new_post)
        session.commit()
        session.refresh(new_post)
        print(f'Created post: {new_post.id} for user {user_id}')


from sqlalchemy import select, Table, MetaData, Column, String
metadata = MetaData()
users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key = True),
    Column('name', String),
    Column('email', String),
    Column('age', Integer),
)

def get_user(user_id: int):
    select_query = select(users).where(users.c.id == user_id)
    result_list = []

    with engine.connect() as connection:
        result = connection.execute(select_query)
        result_list_raw = result.mappings().fetchall()
        for row in result_list_raw:
            result_list.append(dict(row))

        print(f'found {len(result_list)} rows: {result_list[0]}')

    return result_list[0]

if __name__ == '__main__':
    create_user(25, 'asdasdasdasd Doe', 'john.doe@example.com')
    create_post('Title1', 'Content', 1)
    create_post('Title2', 'Content', 1)
    create_post('Title3', 'Content', 1)
    get_user(1)