import pandas as pd
import numpy as np

# Load datasets BEFORE the Residential filter
sold = pd.read_csv(
    "CRMLS_Combined_Sold_All_Property_Types_202401_202608.csv"
)

listings = pd.read_csv(
    "CRMLS_Combined_Listings_All_Property_Types_202401_202608.csv"
)

# --------------------------------------------------
# 1. Understand the dataset
# --------------------------------------------------

print("SOLD DATASET")
print("Number of rows:", len(sold))
print("Number of columns:", len(sold.columns))

print("\nColumn names:")
print(sold.columns.tolist())

print("\nFirst five rows:")
print(sold.head())

print("\nData types:")
print(sold.dtypes)


# --------------------------------------------------
# 2. Check property types
# --------------------------------------------------

print("\nUnique Property Types:")
print(sold["PropertyType"].unique())

print("\nProperty Type Counts:")
print(sold["PropertyType"].value_counts(dropna=False))


# --------------------------------------------------
# 3. Filter to Residential
# --------------------------------------------------

rows_before_filter = len(sold)

sold = sold[sold["PropertyType"] == "Residential"].copy()

rows_after_filter = len(sold)

print("\nRows before Residential filter:", rows_before_filter)
print("Rows after Residential filter:", rows_after_filter)

# --------------------------------------------------
# 3A. Check and filter listings to Residential
# --------------------------------------------------

print("\nListings property types before filtering:")
print(listings["PropertyType"].value_counts(dropna=False))

listing_rows_before_filter = len(listings)

listings = listings[
    listings["PropertyType"] == "Residential"
].copy()

listing_rows_after_filter = len(listings)

print("\nListings rows before Residential filter:",
      listing_rows_before_filter)
print("Listings rows after Residential filter:",
      listing_rows_after_filter)

# --------------------------------------------------
# 4. Missing value analysis
# --------------------------------------------------

null_summary = pd.DataFrame({
    "null_count": sold.isnull().sum(),
    "null_percent": (sold.isnull().sum() / len(sold)) * 100
})

null_summary["over_90_percent_missing"] = (
    null_summary["null_percent"] > 90
)

print("\nMissing Value Summary:")
print(null_summary)


# Save the missing value report
null_summary.to_csv("week2_3_missing_value_report.csv")


# --------------------------------------------------
# 5. Identify columns with more than 90% missing
# --------------------------------------------------

high_missing = null_summary[
    null_summary["over_90_percent_missing"]
]

print("\nColumns with more than 90% missing:")
print(high_missing)


# --------------------------------------------------
# 6. Numeric distribution summary
# --------------------------------------------------

numeric_fields = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket"
]

distribution_summary = sold[numeric_fields].describe(
    percentiles=[0.01, 0.25, 0.50, 0.75, 0.99]
).T

distribution_summary["median"] = sold[numeric_fields].median()

print("\nNumeric Distribution Summary:")
print(distribution_summary)


# Save numeric distribution summary
distribution_summary.to_csv(
    "week2_3_numeric_distribution_summary.csv"
)


# --------------------------------------------------
# 7. Save the filtered dataset
# --------------------------------------------------

sold.to_csv(
    "CRMLS_Week2_3_Residential_Sold.csv",
    index=False
)

print("\nEDA and validation complete.")


# --------------------------------------------------
# Check date fields for mortgage enrichment
# --------------------------------------------------

print("\nDate columns:")
print("CloseDate:", "CloseDate" in sold.columns)
print("ListingContractDate:", "ListingContractDate" in listings.columns)


# --------------------------------------------------
# Fetch mortgage rate data from FRED
# --------------------------------------------------

url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"

mortgage = pd.read_csv(
    url,
    parse_dates=["observation_date"]
)

mortgage.columns = ["date", "rate_30yr_fixed"]

print("\nMortgage data:")
print(mortgage.head())


# --------------------------------------------------
# Calculate monthly mortgage rate averages
# --------------------------------------------------

mortgage["year_month"] = mortgage["date"].dt.to_period("M")

mortgage_monthly = (
    mortgage
    .groupby("year_month")["rate_30yr_fixed"]
    .mean()
    .reset_index()
)

print("\nMonthly mortgage rates:")
print(mortgage_monthly.head())

# --------------------------------------------------
# Create year-month key for sold data
# --------------------------------------------------

sold["year_month"] = pd.to_datetime(
    sold["CloseDate"]
).dt.to_period("M")

print("\nSold year-month:")
print(sold[["CloseDate", "year_month"]].head())



# --------------------------------------------------
# Create year-month key for listings data
# --------------------------------------------------

listings["year_month"] = pd.to_datetime(
    listings["ListingContractDate"]
).dt.to_period("M")

print("\nListings year-month:")
print(listings[["ListingContractDate", "year_month"]].head())



# --------------------------------------------------
# Merge mortgage rates onto sold data
# --------------------------------------------------

sold_with_rates = sold.merge(
    mortgage_monthly,
    on="year_month",
    how="left"
)

print("\nSold data with mortgage rates:")
print(
    sold_with_rates[
        ["CloseDate", "year_month", "ClosePrice", "rate_30yr_fixed"]
    ].head()
)


# --------------------------------------------------
# Merge mortgage rates onto listings data
# --------------------------------------------------

listings_with_rates = listings.merge(
    mortgage_monthly,
    on="year_month",
    how="left"
)

print("\nListings data with mortgage rates:")
print(
    listings_with_rates[
        ["ListingContractDate", "year_month", "rate_30yr_fixed"]
    ].head()
)

# --------------------------------------------------
# Validate mortgage rate merge
# --------------------------------------------------

sold_missing_rates = sold_with_rates[
    "rate_30yr_fixed"
].isnull().sum()

listing_missing_rates = listings_with_rates[
    "rate_30yr_fixed"
].isnull().sum()

print("\nMissing mortgage rates after merge:")
print("Sold:", sold_missing_rates)
print("Listings:", listing_missing_rates)

# --------------------------------------------------
# Save enriched datasets
# --------------------------------------------------

sold_with_rates.to_csv(
    "CRMLS_Week2_3_Sold_With_Mortgage_Rates.csv",
    index=False
)

listings_with_rates.to_csv(
    "CRMLS_Week2_3_Listings_With_Mortgage_Rates.csv",
    index=False
)

print("\nMortgage rate enrichment complete.")
















