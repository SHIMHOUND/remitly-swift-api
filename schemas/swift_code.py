from typing import List, Optional
from pydantic import BaseModel

class SwiftCodeBase(BaseModel):
    address: str
    bankName: str
    countryISO2: str
    isHeadquarter: bool
    swiftCode: str

class SwiftCodeBranch(SwiftCodeBase):
    pass

    class ConfigDict:
        from_attributes = True

class SwiftCodeHeadquarter(SwiftCodeBase):
    countryName: str
    branches: List[SwiftCodeBranch] = []

    class Config:
        orm_mode = True

class SwiftCodeResponse(BaseModel):
    address: str
    bankName: str
    countryISO2: str
    countryName: str
    isHeadquarter: bool
    swiftCode: str
    branches: Optional[List[SwiftCodeBranch]] = None

    model_config = {
        "from_attributes": True
    }

class SwiftCodeCreate(BaseModel):
    address: str
    bankName: str
    countryISO2: str
    countryName: str
    isHeadquarter: bool
    swiftCode: str

class CountrySwiftCodesResponse(BaseModel):
    countryISO2: str
    countryName: str
    swiftCodes: List[SwiftCodeBase]

    class Config:
        orm_mode = True

class MessageResponse(BaseModel):
    message: str