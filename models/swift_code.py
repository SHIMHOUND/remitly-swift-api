from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

try:
    from db import Base
except ImportError:
    print("Failed to import base from db. Please, check the import path.")
    raise

class SwiftCode(Base):
    __tablename__ = "swift_codes"

    swiftCode = Column(String, primary_key=True)
    bankName = Column(String, nullable=False)
    address = Column(String, nullable=True)
    countryISO2 = Column(String, nullable=False)
    countryName = Column(String, nullable=False)
    isHeadquarter = Column(Boolean, default=False)
    headquarterCode = Column(String, ForeignKey("swift_codes.swiftCode"), nullable=True)

    branches = relationship("SwiftCode",
                           foreign_keys=[headquarterCode],
                           backref="headquarters",
                           remote_side=[swiftCode])