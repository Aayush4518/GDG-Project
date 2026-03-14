from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
import uuid
from .base import Base


class Tourist(Base):
    __tablename__ = "tourists"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    kyc_hash = Column(String, nullable=False)
    emergency_contact = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    trip_end_date = Column(DateTime(timezone=True), nullable=False)


class IDLedger(Base):
    __tablename__ = "id_ledger"
    
    id = Column(Integer, primary_key=True, index=True)
    tourist_id = Column(UUID(as_uuid=True), ForeignKey("tourists.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    data = Column(JSON, nullable=False)
    previous_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False, unique=True)


class LocationLog(Base):
    __tablename__ = "location_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    tourist_id = Column(UUID(as_uuid=True), ForeignKey("tourists.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


class HighRiskZone(Base):
    __tablename__ = "high_risk_zones"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    geometry = Column(Geometry('POLYGON'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# NOTE: TouristItinerary is reserved for a future planned-route persistence feature.
# In-memory route storage is currently handled by route_monitor_service.py.
# Uncomment and run Alembic migration when implementing DB-backed route storage.
#
# class TouristItinerary(Base):
#     __tablename__ = "tourist_itineraries"
#     id = Column(Integer, primary_key=True, index=True)
#     tourist_id = Column(UUID(as_uuid=True), ForeignKey("tourists.id"), nullable=False, index=True)
#     sequence_order = Column(Integer, nullable=False)
#     location = Column(Geometry('POINT'), nullable=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
