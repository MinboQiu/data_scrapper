from sqlalchemy import create_engine, Column, ForeignKey  # Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Integer, String, Date, Float)  # SmallInteger, DateTime, Boolean, Text, LargeBinary


DeclarativeBase = declarative_base()


def db_connect(connect_string):
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    # return create_engine(get_project_settings().get("CONNECTION_STRING"), nullable=True)
    return create_engine(connect_string, nullable=True)


def create_table(engine):
    DeclarativeBase.metadata.create_all(engine)


class Record(DeclarativeBase):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True)
    name = Column('name', String(255), nullable=True)
    regulationNo = Column('regulationNo', String(255), nullable=True)
    landSource = Column('landSource', String(255), nullable=True)
    tenureOfUse = Column('tenureOfUse', Integer(), nullable=True)
    industry = Column('industry', String(255), nullable=True)
    landLevel = Column('landLevel', String(255), nullable=True)
    price = Column('price', Float(), nullable=True)
    owner = Column('owner', String(255), nullable=True)
    plotRatioUpperLimit = Column('plotRatioUpperLimit', Float(), nullable=True)
    plotRatioDownLimit = Column('plotRatioDownLimit', Float(), nullable=True)
    dateOfDeliveryAgreed = Column('dateOfDeliveryAgreed', Date(), nullable=True)
    dateOfConstructionAgreed = Column('dateOfConstructionAgreed', Date(), nullable=True)
    dateOfConstructionActual = Column('dateOfConstructionActual', Date(), nullable=True)
    dateOfCompletionAgreed = Column('dateOfCompletionAgreed', Date(), nullable=True)
    dateOfCompletionActual = Column('dateOfCompletionActual', Date(), nullable=True)
    approvedBy = Column('approvedBy', String(255), nullable=True)
    dateOfSigning = Column('dateOfSigning', Date(), nullable=True)
    district = Column('district', String(255), nullable=True)
    location = Column('location', String(255), nullable=True)
    area = Column('area', String(255), nullable=True)
    usage = Column('usage', String(255), nullable=True)
    wayOfSupply = Column('wayOfSupply', String(255), nullable=True)
    url = Column('url', String(255), nullable=True)


class Payment(DeclarativeBase):
    __tablename__ = "payments"

    id = Column(Integer(), primary_key=True)
    date = Column('date', Date(), nullable=True)
    amount = Column('amount', Float(), nullable=True)
    comment = Column('comment', String(255), nullable=True)
    record_id = Column(Integer, ForeignKey('records.id'), nullable=True)
    record = relationship("Record", back_populates="payments")


Record.payments = relationship("Payment", order_by=Payment.date, back_populates="record")
