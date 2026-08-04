from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from core.db import Base

class BreakglassAccount(Base):
    __tablename__ = "breakglass_accounts"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    username = Column(String, nullable=False)
    vault_path = Column(String, nullable=False)
    vault_key = Column(String, nullable=False)
    is_enabled = Column(Boolean, default=True)

    device = relationship("Device", backref="breakglass_accounts")
