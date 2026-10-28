import pandas as pd
from pathlib import Path

# ==========================================================
# WEEKS 4-5: DATA CLEANING AND PREPARATION
# ==========================================================
# Purpose:
# 1. Convert date columns to datetime format.
# 2. Convert key numeric columns to numeric types.
# 3. Flag invalid numeric values.
# 4. Check date consistency.
# 5. Check geographic data quality.
# 6. Report missing values and data types.
# 7. Save cleaned datasets and quality reports.
#
# Invalid records are flagged, not automatically deleted.
# Missing values are reported rather than filled with guesses.
# ==========================================================

# ----------------------------------------------------------
# 1. Load the Week 2-3 enriched datasets
# ----------------------------------------------------------

sold_file = "CRMLS_Week2_3_Sold_With_Mortgage_Rates.csv"
listings_file = "CRMLS_Week2_3_Listings_With_Mortgage_Rates.csv"

sold = pd.read_csv(sold_file)
listings = pd.read_csv(listings_file)

print("=" * 60)
print("WEEKS 4-5 DATA CLEANING")
print("=" * 60)

print("\nINITIAL DATASET SIZES")
print("Sold rows:", len(sold))
print("Sold columns:", len(sold.columns))
print("Listings rows:", len(listings))
print("Listings columns:", len(listings.columns))


# ----------------------------------------------------------
# 2. Define fields to clean
# ----------------------------------------------------------

date_columns = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate"
]

numeric_columns = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
    "Latitude",
    "Longitude"
]

# Only add columns here after confirming they are unnecessary.
# Keep this list empty until redundant columns are identified.
columns_to_drop = []


# ----------------------------------------------------------
# 3. Helper function for cleaning each dataset
# ----------------------------------------------------------

def clean_dataset(df, dataset_name):

    df = df.copy()

    print("\n" + "=" * 60)
    print(f"CLEANING: {dataset_name}")
    print("=" * 60)

    rows_before = len(df)
    columns_before = len(df.columns)

    print("Rows before cleaning:", rows_before)
    print("Columns before cleaning:", columns_before)

    # ------------------------------------------------------
    # 4. Convert date columns to datetime
    # ------------------------------------------------------

    print("\nDATE CONVERSION")

    for col in date_columns:
        if col in df.columns:
            # Invalid date strings become NaT (missing dates).
            df[col] = pd.to_datetime(df[col], errors="coerce")

            print(f"{col}: converted to datetime")

        else:
            print(f"{col}: column not present in this dataset")

    # ------------------------------------------------------
    # 5. Convert numeric fields to numeric types
    # ------------------------------------------------------

    print("\nNUMERIC TYPE CONVERSION")

    for col in numeric_columns:
        if col in df.columns:
            # Values that cannot be converted become NaN.
            df[col] = pd.to_numeric(df[col], errors="coerce")

            print(f"{col}: converted to numeric")

    # ------------------------------------------------------
    # 6. Flag invalid numeric values
    # ------------------------------------------------------

    print("\nINVALID NUMERIC VALUE FLAGS")

    if "ClosePrice" in df.columns:
        df["invalid_closeprice_flag"] = df["ClosePrice"] <= 0

    if "LivingArea" in df.columns:
        df["invalid_livingarea_flag"] = df["LivingArea"] <= 0

    if "DaysOnMarket" in df.columns:
        df["invalid_days_on_market_flag"] = df["DaysOnMarket"] < 0

    if "BedroomsTotal" in df.columns:
        df["invalid_bedrooms_flag"] = df["BedroomsTotal"] < 0

    if "BathroomsTotalInteger" in df.columns:
        df["invalid_bathrooms_flag"] = (
            df["BathroomsTotalInteger"] < 0
        )

    numeric_flag_columns = [
        "invalid_closeprice_flag",
        "invalid_livingarea_flag",
        "invalid_days_on_market_flag",
        "invalid_bedrooms_flag",
        "invalid_bathrooms_flag"
    ]

    for col in numeric_flag_columns:
        if col in df.columns:
            print(f"{col}: {int(df[col].sum())} flagged records")

    # ------------------------------------------------------
    # 7. Check date consistency
    # ------------------------------------------------------

    print("\nDATE CONSISTENCY CHECKS")

    required_date_columns = [
        "ListingContractDate",
        "PurchaseContractDate",
        "CloseDate"
    ]

    if all(col in df.columns for col in required_date_columns):

        listing_date = df["ListingContractDate"]
        purchase_date = df["PurchaseContractDate"]
        close_date = df["CloseDate"]

        # Listing date occurs after the closing date.
        df["listing_after_close_flag"] = (
            listing_date.notna()
            & close_date.notna()
            & (listing_date > close_date)
        )

        # Purchase contract date occurs after closing.
        df["purchase_after_close_flag"] = (
            purchase_date.notna()
            & close_date.notna()
            & (purchase_date > close_date)
        )

        # Flag violations of the expected date order:
        # Listing date <= Purchase contract date <= Close date.
        listing_after_purchase = (
            listing_date.notna()
            & purchase_date.notna()
            & (listing_date > purchase_date)
        )

        purchase_after_close = (
            purchase_date.notna()
            & close_date.notna()
            & (purchase_date > close_date)
        )

        df["negative_timeline_flag"] = (
                df["listing_after_close_flag"]
                | listing_after_purchase
                | purchase_after_close
        )

        print(
            "listing_after_close_flag:",
            int(df["listing_after_close_flag"].sum())
        )

        print(
            "purchase_after_close_flag:",
            int(df["purchase_after_close_flag"].sum())
        )

        print(
            "negative_timeline_flag:",
            int(df["negative_timeline_flag"].sum())
        )

    else:
        print(
            "Date consistency checks skipped: "
            "one or more required date columns are absent."
        )

    # ------------------------------------------------------
    # 8. Check geographic data quality
    # ------------------------------------------------------

    print("\nGEOGRAPHIC DATA CHECKS")

    # Find the coordinate columns using common field names.
    # Use the standard Latitude/Longitude fields when available.
    latitude_candidates = ["Latitude", "latitude", "lat", "latfilled"]
    longitude_candidates = [
        "Longitude", "longitude", "lon", "long", "lonfilled"
    ]

    latitude_col = next(
        (col for col in latitude_candidates if col in df.columns),
        None
    )

    longitude_col = next(
        (col for col in longitude_candidates if col in df.columns),
        None
    )

    if latitude_col and longitude_col:

        # Convert coordinates to numeric values.
        df[latitude_col] = pd.to_numeric(
            df[latitude_col], errors="coerce"
        )

        df[longitude_col] = pd.to_numeric(
            df[longitude_col], errors="coerce"
        )

        latitude = df[latitude_col]
        longitude = df[longitude_col]

        # Flag missing coordinates.
        df["missing_coordinates_flag"] = (
            latitude.isna() | longitude.isna()
        )

        # Zero coordinates can be placeholders for missing data.
        df["zero_coordinates_flag"] = (
            (latitude == 0) | (longitude == 0)
        )

        # California longitudes should be negative.
        df["positive_longitude_flag"] = longitude > 0

        # Flag impossible coordinate values.
        impossible_coordinates = (
            latitude.notna()
            & ~latitude.between(-90, 90)
        ) | (
            longitude.notna()
            & ~longitude.between(-180, 180)
        )

        # Approximate California bounding box.
        # This is a screening check, not a precise state boundary.
        outside_california = (
            latitude.notna()
            & longitude.notna()
            & ~(
                latitude.between(32.5, 42.1)
                & longitude.between(-124.5, -114.1)
            )
        )

        df["out_of_state_or_implausible_coords_flag"] = (
            impossible_coordinates | outside_california
        )

        print("Latitude column used:", latitude_col)
        print("Longitude column used:", longitude_col)

        print(
            "Missing coordinates:",
            int(df["missing_coordinates_flag"].sum())
        )

        print(
            "Zero coordinates:",
            int(df["zero_coordinates_flag"].sum())
        )

        print(
            "Positive longitude:",
            int(df["positive_longitude_flag"].sum())
        )

        print(
            "Out-of-state or implausible coordinates:",
            int(
                df[
                    "out_of_state_or_implausible_coords_flag"
                ].sum()
            )
        )

    else:
        print(
            "Geographic checks skipped: latitude and/or "
            "longitude columns were not found."
        )
        print("Available columns:", df.columns.tolist())

    # ------------------------------------------------------
    # 9. Remove only explicitly approved columns
    # ------------------------------------------------------

    existing_drop_columns = [
        col for col in columns_to_drop if col in df.columns
    ]

    if existing_drop_columns:
        df = df.drop(columns=existing_drop_columns)
        print("\nColumns removed:", existing_drop_columns)
    else:
        print("\nNo columns removed; none were specified.")

    # ------------------------------------------------------
    # 10. Report missing values
    # ------------------------------------------------------

    print("\nTOP 15 COLUMNS BY MISSING VALUE COUNT")

    missing_report = pd.DataFrame({
        "column": df.columns,
        "missing_count": df.isna().sum().values,
        "missing_percent": (
            df.isna().mean().values * 100
        )
    })

    missing_report = missing_report.sort_values(
        "missing_percent", ascending=False
    )

    print(missing_report.head(15).to_string(index=False))

    # ------------------------------------------------------
    # 11. Confirm final data types and row counts
    # ------------------------------------------------------

    rows_after = len(df)
    columns_after = len(df.columns)

    print("\nFINAL DATASET SIZES")
    print("Rows before cleaning:", rows_before)
    print("Rows after cleaning:", rows_after)
    print("Columns before cleaning:", columns_before)
    print("Columns after cleaning:", columns_after)

    print("\nFINAL DATE AND NUMERIC DATA TYPES")

    for col in date_columns + numeric_columns:
        if col in df.columns:
            print(f"{col}: {df[col].dtype}")

    # Save a missing-value report for this dataset.
    missing_report.to_csv(
        f"{dataset_name.lower()}_week4_5_missing_report.csv",
        index=False
    )

    return df


# ----------------------------------------------------------
# 12. Clean sold and listings datasets
# ----------------------------------------------------------

sold_clean = clean_dataset(sold, "Sold")
listings_clean = clean_dataset(listings, "Listings")


# ----------------------------------------------------------
# 13. Save cleaned datasets
# ----------------------------------------------------------

sold_output = "CRMLS_Week4_5_Sold_Cleaned.csv"
listings_output = "CRMLS_Week4_5_Listings_Cleaned.csv"

sold_clean.to_csv(sold_output, index=False)
listings_clean.to_csv(listings_output, index=False)

print("\n" + "=" * 60)
print("WEEKS 4-5 CLEANING COMPLETE")
print("=" * 60)

print("Saved:", sold_output)
print("Saved:", listings_output)
print("Saved: sold_week4_5_missing_report.csv")
print("Saved: listings_week4_5_missing_report.csv")