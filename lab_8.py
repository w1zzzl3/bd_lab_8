from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, func
from sqlalchemy.orm import declarative_base, Session, relationship
from sqlalchemy.exc import IntegrityError

engine = create_engine('sqlite:///db.db', echo=False)
Base = declarative_base()

class Bugs(Base):
    __tablename__ = 'bugs'

    BugId = Column(Integer, primary_key=True)
    BugName = Column(Integer)
    BugDescription = Column(String)

class Reports(Base):
    __tablename__ = 'reports'

    ReportId = Column(Integer, primary_key=True)
    BugId = Column(Integer, ForeignKey('bugs.BugId'))
    FileName = Column(String)
    Date = Column(String)

    bugs = relationship("Bugs")

Base.metadata.create_all(engine)

def create_session():
    return Session(engine)

def close_session(session):
    session.close()

def create_bug(session, bugName, bugDescription):
    new_bug = Bugs(BugName=bugName, BugDescription=bugDescription)
    session.add(new_bug)
    try:
        session.commit()
    except IntegrityError as e:
        print(f"Error: {e}")
        session.rollback()

def create_report(session, bugId, fileName, date):
    new_report = Reports(BugId=bugId, FileName=fileName, Date=date)
    session.add(new_report)
    session.commit()

def get_all_bugs(session):
    return session.query(Bugs).all()

def get_all_reports(session):
    return session.query(Reports).all()

def update_bugs(session, BugId, BugDescription):
    bugs_to_update = session.query(Bugs).filter_by(BugId=BugId).first()
    if bugs_to_update:
        bugs_to_update.BugDescription = BugDescription
        session.commit()

def delete_bugs(session, BugId):
    bugs_to_delete = session.query(Bugs).filter_by(BugId=BugId).first()
    if bugs_to_delete:
        session.delete(bugs_to_delete)
        session.commit()

def get_report_details(session):
    return session.query(Reports.ReportId, Reports.BugId, Bugs.BugDescription, Reports.FileName, Reports.Date).\
        join(Bugs, Bugs.BugId == Reports.BugId).all()

def get_report_details_filtered(session, BugId=None):
    query = session.query(Reports.ReportId, Reports.BugId, Bugs.BugDescription, Reports.FileName, Reports.Date).\
        join(Bugs, Bugs.BugId == Reports.BugId)
        
    if BugId is not None:
        query = query.filter(Reports.BugId == BugId)
        return query.all()
    else:
        return 1

def report_count_per_bug(session, BugId=None):
    query = session.query(func.count(Reports.BugId).label('bug_count')).\
        join(Bugs, Bugs.BugId == Reports.BugId)

    if BugId is not None:
        query = query.filter(Reports.BugId == BugId)
        return query.all()
    else:
        return 1


session = create_session()

bugs_to_add = [[403, "Something happened"]]
for item in bugs_to_add:
    create_bug(session, item[0], item[1])

reports_to_add = [[403, "py.py", "20.09.2077"]]
for item in reports_to_add:
    create_report(session, item[0], item[1], item[2])

all_bugs = get_all_bugs(session)
print("Всі баги:")
for bug in all_bugs:
    print(bug.BugId, bug.BugName, bug.BugDescription)

all_reports = get_all_reports(session)
print("Всі звіти:")
for report in all_reports:
    print(report.ReportId, report.BugId, report.FileName, report.Date)

certain_bug_reports = get_report_details_filtered(session, 1)
print("Всі звіти з багом 404: ")
for report in certain_bug_reports:
    print(report.ReportId, report.BugId, report.FileName, report.Date)

certain_bug_reports_count = report_count_per_bug(session, 404)
print("\nКількість звітів по кожному багові:")
print(certain_bug_reports_count)

close_session(session)