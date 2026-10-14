
import pandas as pd
import glob
import os

# Folder containing the original monthly CSV files
data_folder = "csv"

# Find the original monthly sold and listings files
sold_files = sorted(
    glob.glob(os.path.join(data_folder, "*Sold*.csv"))
)

listing_files = sorted(
    glob.glob(os.path.join(data_folder, "*Listing*.csv"))
)

# Check that monthly files were found
if not sold_files:
    raise FileNotFoundError(
        "No monthly sold files found. Check the csv folder and filenames."
    )

if not listing_files:
    raise FileNotFoundError(
        "No monthly listings files found. Check the csv folder and filenames."
    )

# --------------------------------------------------
# 1. Combine all monthly SOLD files
# --------------------------------------------------

sold_monthly = []

for file in sold_files:
    df = pd.read_csv(file)
    print(f"Sold file: {os.path.basename(file)} | Rows: {len(df)}")
    sold_monthly.append(df)

# Total rows across individual monthly files
sold_rows_before_concat = sum(len(df) for df in sold_monthly)

# Combine the monthly sold files
sold_all = pd.concat(sold_monthly, ignore_index=True)

print("\nSOLD DATA")
print("Monthly files found:", len(sold_files))
print("Rows across monthly files:", sold_rows_before_concat)
print("Rows after concatenation:", len(sold_all))

# Save the combined sold dataset BEFORE filtering
sold_all.to_csv(
    "CRMLS_Combined_Sold_All_Property_Types_202401_202608.csv",
    index=False
)

# Check property types before filtering
print("\nSold property type counts:")
print(sold_all["PropertyType"].value_counts(dropna=False))

print("\nSold property type percentages:")
print(
    sold_all["PropertyType"]
    .value_counts(normalize=True, dropna=False)
    .mul(100)
)

# Filter sold records to Residential
sold_residential = sold_all[
    sold_all["PropertyType"] == "Residential"
].copy()

print("\nSold rows before Residential filter:", len(sold_all))
print("Sold rows after Residential filter:", len(sold_residential))

# Save the Residential-only sold dataset
sold_residential.to_csv(
    "CRMLS_Combined_Residential_Sold_202401_202608.csv",
    index=False
)


# --------------------------------------------------
# 2. Combine all monthly LISTINGS files
# --------------------------------------------------

listing_monthly = []

for file in listing_files:
    df = pd.read_csv(file)
    print(f"Listings file: {os.path.basename(file)} | Rows: {len(df)}")
    listing_monthly.append(df)

# Total rows across individual monthly files
listing_rows_before_concat = sum(len(df) for df in listing_monthly)

# Combine the monthly listings files
listings_all = pd.concat(listing_monthly, ignore_index=True)

print("\nLISTINGS DATA")
print("Monthly files found:", len(listing_files))
print("Rows across monthly files:", listing_rows_before_concat)
print("Rows after concatenation:", len(listings_all))

# Save the combined listings dataset BEFORE filtering
listings_all.to_csv(
    "CRMLS_Combined_Listings_All_Property_Types_202401_202608.csv",
    index=False
)

# Check property types before filtering
print("\nListings property type counts:")
print(listings_all["PropertyType"].value_counts(dropna=False))

print("\nListings property type percentages:")
print(
    listings_all["PropertyType"]
    .value_counts(normalize=True, dropna=False)
    .mul(100)
)

# Filter listing records to Residential
listings_residential = listings_all[
    listings_all["PropertyType"] == "Residential"
].copy()

print("\nListings rows before Residential filter:", len(listings_all))
print("Listings rows after Residential filter:", len(listings_residential))

# Save the Residential-only listings dataset
listings_residential.to_csv(
    "CRMLS_Combined_Residential_Listings_202401_202608.csv",
    index=False
)

print("\nWeek 1 aggregation complete.")
print("Both all-property-type and Residential-only datasets were saved.")









