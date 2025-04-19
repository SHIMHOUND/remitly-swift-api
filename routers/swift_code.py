from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
import sqlalchemy.exc

from db import get_db
from models.swift_code import SwiftCode
from schemas.swift_code import (
    SwiftCodeResponse,
    SwiftCodeCreate,
    CountrySwiftCodesResponse,
    SwiftCodeBase,
    SwiftCodeBranch,
    MessageResponse
)

router = APIRouter(prefix="/v1/swift-codes", tags=["swift-codes"])


@router.get("/{swift_code}", response_model=SwiftCodeResponse)
def get_swift_code(swift_code: str, db: Session = Depends(get_db)):
    """
    Retrieve details of a single SWIFT code whether for a headquarters or branches.
    """
    swift_code = swift_code.upper()
    db_swift_code = db.query(SwiftCode).options(selectinload(SwiftCode.branches)).filter(
        SwiftCode.swiftCode == swift_code
    ).first()

    if not db_swift_code:
        raise HTTPException(status_code=404, detail=f"SWIFT code {swift_code} not found")

    branches = None
    if db_swift_code.isHeadquarter:
        branches_query = db.query(SwiftCode).filter(
            SwiftCode.headquarterCode == swift_code
        ).all()
        branches = [
            SwiftCodeBranch.model_validate(branch, from_attributes=True) for branch in branches_query
        ]

    return SwiftCodeResponse(
        address=db_swift_code.address,
        bankName=db_swift_code.bankName,
        countryISO2=db_swift_code.countryISO2,
        countryName=db_swift_code.countryName,
        isHeadquarter=db_swift_code.isHeadquarter,
        swiftCode=db_swift_code.swiftCode,
        branches=branches
    )


@router.get("/country/{country_iso2code}", response_model=CountrySwiftCodesResponse)
def get_country_swift_codes(country_iso2code: str, db: Session = Depends(get_db)):
    country_iso2code = country_iso2code.upper()

    country_swift_codes = db.query(SwiftCode).filter(
        SwiftCode.countryISO2 == country_iso2code
    ).all()

    if not country_swift_codes:
        raise HTTPException(status_code=404, detail=f"No SWIFT codes found for country {country_iso2code}")

    country_name = country_swift_codes[0].countryName

    swift_codes_list = [
        SwiftCodeBase(
            address=code.address,
            bankName=code.bankName,
            countryISO2=code.countryISO2,
            isHeadquarter=code.isHeadquarter,
            swiftCode=code.swiftCode
        ) for code in country_swift_codes
    ]

    return CountrySwiftCodesResponse(
        countryISO2=country_iso2code,
        countryName=country_name,
        swiftCodes=swift_codes_list
    )


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_swift_code(swift_code: SwiftCodeCreate, db: Session = Depends(get_db)):
    swift_code_dict = swift_code.model_dump()
    swift_code_dict["countryISO2"] = swift_code_dict["countryISO2"].upper()
    swift_code_dict["countryName"] = swift_code_dict["countryName"].upper()
    swift_code_dict["swiftCode"] = swift_code_dict["swiftCode"].upper()

    db_swift_code = db.query(SwiftCode).filter(
        SwiftCode.swiftCode == swift_code_dict["swiftCode"]
    ).first()

    if db_swift_code:
        raise HTTPException(status_code=400, detail=f"SWIFT code {swift_code_dict['swiftCode']} already exists")

    new_swift_code = SwiftCode(**swift_code_dict)

    if not swift_code_dict["isHeadquarter"]:
        potential_hq_code = swift_code_dict["swiftCode"][:8] + "XXX"
        headquarters = db.query(SwiftCode).filter(SwiftCode.swiftCode == potential_hq_code).first()
        if headquarters:
            new_swift_code.headquarterCode = potential_hq_code

    try:
        db.add(new_swift_code)
        db.commit()
        db.refresh(new_swift_code)
        return {"message": f"SWIFT code {swift_code_dict['swiftCode']} created successfully"}
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{swift_code}", response_model=MessageResponse)
def delete_swift_code(swift_code: str, db: Session = Depends(get_db)):
    swift_code = swift_code.upper()
    db_swift_code = db.query(SwiftCode).filter(SwiftCode.swiftCode == swift_code).first()

    if not db_swift_code:
        raise HTTPException(status_code=404, detail=f"SWIFT code {swift_code} not found")

    if db_swift_code.isHeadquarter:
        branches = db.query(SwiftCode).filter(SwiftCode.headquarterCode == swift_code).all()
        if branches:
            for branch in branches:
                branch.headquarterCode = None
            db.commit()

    db.delete(db_swift_code)
    db.commit()

    return {"message": f"SWIFT code {swift_code} deleted successfully"}
