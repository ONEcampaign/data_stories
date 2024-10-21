import pandas as pd
from pydeflate import deflate

from stories.eu27_targets.growth import get_constant_deflators


def to_constant(
    df: pd.DataFrame,
    base_year: int = 2025,
    source_currency: str = "EUI",
    source_column: str = "total_oda_official_definition",
    target_column: str = "total_oda_official_definition",
) -> pd.DataFrame:
    if base_year > 2023:
        deflators = get_constant_deflators(base=base_year).assign(
            year=lambda d: d.year.dt.year
        )
        deflate_year = 2023
    else:
        deflate_year = base_year

    df = deflate(
        df=df,
        base_year=deflate_year,
        deflator_source="oecd_dac",
        deflator_method="dac_deflator",
        exchange_source="oecd_dac",
        source_currency="USA" if source_currency == "USD" else source_currency,
        target_currency="EUI",
        id_column="donor_code",
        id_type="DAC",
        date_column="year",
        source_column=source_column,
        target_column=target_column,
    )

    if "gni" in df.columns:

        df = deflate(
            df=df,
            base_year=deflate_year,
            deflator_source="oecd_dac",
            deflator_method="dac_deflator",
            exchange_source="oecd_dac",
            source_currency="USA" if source_currency == "USD" else source_currency,
            target_currency="EUI",
            id_column="donor_code",
            id_type="DAC",
            date_column="year",
            source_column="gni",
            target_column="gni",
        )

    if base_year > 2023:
        df = df.merge(
            deflators,
            left_on=["year", "donor_code"],
            right_on=["year", "dac_code"],
            how="left",
        )

        df[target_column] = df[target_column] / df["value"]

    if "gni" in df.columns:
        df = df.assign(gni=lambda d: d.gni / d.value)

    return df.assign(prices="constant", base_year=base_year)
