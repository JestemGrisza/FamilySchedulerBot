from sqlalchemy import Column, Integer, VARCHAR, BLOB, DateTime, Boolean
from sqlalchemy import create_engine
from sqlalchemy import or_, and_
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import exists

import datetime

engine = create_engine('sqlite:///fml_schd.db', echo=False)

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    tid = Column(Integer, index=True)
    name = Column(VARCHAR(255))
    firstname = Column(VARCHAR(255))
    lastname = Column(VARCHAR(255))
    phone_number = Column(VARCHAR(255))
    admin = Column(Boolean)
    ro = Column(Boolean)

    tasks = relationship('Task', backref='user', lazy='dynamic')

    def __repr__(self):
        return f"<User {self.name=}, tid {self.tid=}>"


class Req(Base):
    __tablename__ = 'req'

    id = Column(Integer, primary_key=True)
    tid = Column(Integer)
    name = Column(VARCHAR(255))
    firstname = Column(VARCHAR(255))
    lastname = Column(VARCHAR(255))
    phone_number = Column(VARCHAR(255))

    def __repr__(self):
        return f"<Req {self.name=}, tid {self.tid=}>"


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    task_name = Column(VARCHAR(255))

    # create_date = Column(DateTime(timezone=True), default=func.now())
    create_date = Column(DateTime, default=datetime.datetime.now)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    notify_at = Column(DateTime)

    user_id = Column(Integer, ForeignKey('users.tid'))

    def __repr__(self):
        return f"<Task {self.task_name=}>, User {self.user_id=}"


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def add_req(tid, name, firstname, lastname):
    rec = Req(tid=tid, name=name, firstname=firstname, lastname=lastname)
    session.add(rec)
    session.commit()


def add_user(tid, name, firstname, lastname, admin=False, ro=False):
    rec = User(tid=tid, name=name, firstname=firstname, lastname=lastname, admin=admin, ro=ro)
    session.add(rec)
    session.commit()


def req_to_user_move(tid):
    req = session.query(Req).filter(Req.tid == tid).first()
    # print(req)
    rec = User(tid=req.tid, name=req.name, firstname=req.firstname, lastname=req.lastname)
    session.add(rec)
    session.delete(req)
    session.commit()


def get_root_user_tid():
    return session.query(User).filter(User.admin == 1).first().tid


def add_task(task_name, user_id, start_date='', end_date='', notify_at=''):
    rec = Task(task_name=task_name, user_id=user_id, start_date=start_date, end_date=end_date, notify_at=notify_at)
    session.add(rec)
    session.commit()


def get_task(tid, date):
    return session.query(Task).filter(and_(Task.user_id == tid, func.DATE(Task.start_date) == date)).all()


def show_users():
    users = session.query(User).all()
    return users


def show_req():
    req = session.query(Req).all()
    return req


def user_exist(tid):
    return session.query(exists().where(User.tid == tid)).scalar()


def req_exist(tid):
    return session.query(exists().where(Req.tid == tid)).scalar()


def user_table():
    return session.query(User).count()


def req_table():
    return session.query(Req).count()


if __name__ == '__main__':
    pass
    print(req_exist(502886232))
    # req_to_user_move(502886232)
    # add_user(54321,'vasia', admin=True)
    # print(get_root_user_tid())
    # print(req_table())
    # print(session.query(User).count())
    # pass
    # add_task('test #1', 1)
    # add_user(12345,'grisha')
    # add_req(54321,'vasia')
    # print(show_users())
    # for i in show_users():
    #     print(i.id, i.tid, i.name)

    # print(user_exist(426072814))
