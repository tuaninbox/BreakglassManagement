from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from core.db import Base 

class BreakglassRequest(Base):
    __tablename__ = "breakglass_requests"

    id = Column(Integer, primary_key=True, index=True)

    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)

    reason = Column(String, nullable=False)
    status = Column(String, default="pending")  
    # pending → waiting for approver  
    # approved → approver approved  
    # rejected → approver rejected  
    # expired → optional later  

    otp_verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)

    # Relationships
    requester = relationship("User", foreign_keys=[requester_id])
    approver = relationship("User", foreign_keys=[approver_id])
