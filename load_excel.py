import pandas as pd
from sqlalchemy.orm import Session
from models.swift_code import SwiftCode, Base
from db import engine


def load_swift_codes(file_path: str, db: Session):
    Base.metadata.create_all(bind=engine)

    print(f"Reading Excel file: {file_path}")
    df = pd.read_excel(file_path)

    print("Original Excel columns:", df.columns.tolist())

    # Clean column names - convert to lowercase and replace spaces with underscores
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    print("Cleaned Excel columns:", df.columns.tolist())

    # Determine column name mappings
    # This maps from how columns appear in the Excel (after cleaning) to our model fields
    column_mapping = {}

    # Required fields for our model
    required_fields = ['swiftCode', 'bankName', 'countryISO2', 'countryName']

    # Try to identify column names based on common variations
    possible_mappings = {
        'swiftCode': ['swift_code', 'swift', 'bic', 'swift_bic', 'code'],
        'bankName': ['bank_name', 'bank', 'institution_name', 'financial_institution', 'name'],
        'countryISO2': ['country_iso2_code', 'country_code', 'iso2', 'iso_code', 'country_iso'],
        'countryName': ['country_name', 'country', 'nation']
    }

    for model_field, possible_names in possible_mappings.items():
        for col_name in possible_names:
            if col_name in df.columns:
                column_mapping[col_name] = model_field
                print(f"Mapped '{col_name}' to '{model_field}'")
                break

    # Check if we have all required fields
    missing_fields = [field for field in required_fields if field not in column_mapping.values()]
    if missing_fields:
        print(f"ERROR: Could not find mappings for required fields: {missing_fields}")
        print("Please update your Excel file to include these columns or update the mapping in load_excel.py")
        return

    # Rename columns based on mapping
    df = df.rename(columns=column_mapping)
    print("Final DataFrame columns:", df.columns.tolist())

    # Make sure required columns exist
    for field in required_fields:
        if field not in df.columns:
            print(f"ERROR: Required field '{field}' not found in DataFrame")
            return

    # Make sure country codes and names are uppercase
    df['countryISO2'] = df['countryISO2'].str.upper()
    df['countryName'] = df['countryName'].str.upper()

    # Add address column if it doesn't exist
    if 'address' not in df.columns:
        print("Address column not found, adding empty addresses")
        df['address'] = ''

    # Identify headquarters vs branches
    df['isHeadquarter'] = df['swiftCode'].str.endswith('XXX')

    # Map branches to their headquarters
    df['headquarterCode'] = None

    # Process each non-headquarter code
    for idx, row in df[~df['isHeadquarter']].iterrows():
        swift_code = row['swiftCode']
        potential_hq_code = swift_code[:8] + "XXX"

        # Check if this headquarters exists in our data
        if potential_hq_code in df[df['isHeadquarter']]['swiftCode'].values:
            df.at[idx, 'headquarterCode'] = potential_hq_code

    # Insert all records into the database
    records_added = 0
    for _, row in df.iterrows():
        try:
            swift_code = SwiftCode(
                swiftCode=row['swiftCode'],
                bankName=row['bankName'],
                address=row['address'],
                countryISO2=row['countryISO2'],
                countryName=row['countryName'],
                isHeadquarter=row['isHeadquarter'],
                headquarterCode=row.get('headquarterCode')
            )

            # Check if record already exists
            existing = db.query(SwiftCode).filter(SwiftCode.swiftCode == swift_code.swiftCode).first()
            if not existing:
                db.add(swift_code)
                records_added += 1
        except Exception as e:
            print(f"Error processing row: {row}")
            print(f"Exception: {e}")

    db.commit()
    print(f"Data import completed successfully! Added {records_added} new records.")


if __name__ == "__main__":
    from db import SessionLocal

    db = SessionLocal()
    try:
        load_swift_codes("Interns_2025_SWIFT_CODES.xlsx", db)
    finally:
        db.close()
