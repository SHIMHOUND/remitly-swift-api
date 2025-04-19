import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db import Base, get_db
from models.swift_code import SwiftCode

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the dependency to use our test database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Add test data
    db = TestingSessionLocal()

    # Create a test headquarters
    hq = SwiftCode(
        swiftCode="TESTBANKXXX",
        bankName="TEST BANK",
        address="123 Test St, Test City",
        countryISO2="US",
        countryName="UNITED STATES",
        isHeadquarter=True
    )

    # Create a test branch
    branch = SwiftCode(
        swiftCode="TESTBANK123",
        bankName="TEST BANK BRANCH",
        address="456 Branch St, Test City",
        countryISO2="US",
        countryName="UNITED STATES",
        isHeadquarter=False,
        headquarterCode="TESTBANKXXX"
    )

    db.add(hq)
    db.add(branch)
    db.commit()
    db.close()

    yield

    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)


def test_get_swift_code_headquarters():
    response = client.get("/v1/swift-codes/TESTBANKXXX")
    assert response.status_code == 200
    data = response.json()
    assert data["swiftCode"] == "TESTBANKXXX"
    assert data["isHeadquarter"] == True
    assert "branches" in data
    assert len(data["branches"]) == 1
    assert data["branches"][0]["swiftCode"] == "TESTBANK123"


def test_get_swift_code_branch():
    response = client.get("/v1/swift-codes/TESTBANK123")
    assert response.status_code == 200
    data = response.json()
    assert data["swiftCode"] == "TESTBANK123"
    assert data["isHeadquarter"] == False
    assert data["branches"] is None


def test_get_country_swift_codes():
    response = client.get("/v1/swift-codes/country/US")
    assert response.status_code == 200
    data = response.json()
    assert data["countryISO2"] == "US"
    assert data["countryName"] == "UNITED STATES"
    assert len(data["swiftCodes"]) == 2


def test_create_swift_code():
    new_code = {
        "swiftCode": "NEWBANKXXX",
        "bankName": "NEW TEST BANK",
        "address": "789 New St, New City",
        "countryISO2": "CA",
        "countryName": "Canada",
        "isHeadquarter": True
    }

    response = client.post("/v1/swift-codes", json=new_code)
    assert response.status_code == 201
    assert response.json()["message"] == "SWIFT code NEWBANKXXX created successfully"

    # Verify the new code exists
    check_response = client.get("/v1/swift-codes/NEWBANKXXX")
    assert check_response.status_code == 200
    assert check_response.json()["swiftCode"] == "NEWBANKXXX"
    assert check_response.json()["countryISO2"] == "CA"
    assert check_response.json()["countryName"] == "CANADA"  # Should be uppercase


def test_delete_swift_code():
    response = client.delete("/v1/swift-codes/TESTBANK123")
    assert response.status_code == 200
    assert response.json()["message"] == "SWIFT code TESTBANK123 deleted successfully"

    # Verify it's gone
    check_response = client.get("/v1/swift-codes/TESTBANK123")
    assert check_response.status_code == 404