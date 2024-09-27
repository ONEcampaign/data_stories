from typing import Optional

import pandas as pd
from oda_data import ODAData, set_data_path


from stories import config
from stories.health_oda.common import filter_health_sectors

set_data_path(config.Paths.raw_data)


GROUPER = [
    "year",
    "indicator",
    "donor_code",
    "recipient_code",
    "purpose_code",
    "keywords",
    "prices",
]


def _get_health_oda_indicator(
    indicator: str,
    start_year: int = 2000,
    end_year: int = 2023,
    prices: str = "current",
    base_year: Optional[int] = None,
) -> pd.DataFrame:

    # Create an ODAData object
    oda = ODAData(
        years=range(start_year, end_year + 1), prices=prices, base_year=base_year
    )

    # Load the indicator
    oda.load_indicator(indicator)

    # Get the data, filtered by health sectors
    df = oda.get_data().pipe(filter_health_sectors)

    # Group the data
    grouper = [c for c in GROUPER if c in df.columns]
    df = df.groupby(grouper, dropna=False, observed=True)["value"].sum().reset_index()

    return df


def get_bilateral_health_oda(
    start_year: int = 2000,
    end_year: int = 2023,
    prices: str = "current",
    base_year: Optional[int] = None,
) -> pd.DataFrame:

    return _get_health_oda_indicator(
        indicator="crs_bilateral_flow_disbursement_gross",
        start_year=start_year,
        end_year=end_year,
        prices=prices,
        base_year=base_year,
    )


def get_total_bilateral_oda(
    start_year: int = 2000,
    end_year: int = 2023,
    prices: str = "current",
    base_year: Optional[int] = None,
) -> pd.DataFrame:
    """Gross disbursements of bilateral ODA."""
    # Create an ODAData object
    oda = ODAData(
        years=range(start_year, end_year + 1), prices=prices, base_year=base_year
    )

    # Load the indicator
    oda.load_indicator("crs_bilateral_flow_disbursement_gross")

    # Get the data, filtered by health sectors
    df = oda.get_data()

    # Group the data
    grouper = [c for c in GROUPER if c in df.columns]
    df = df.groupby(grouper, dropna=False, observed=True)["value"].sum().reset_index()

    return df


def get_imputed_multilateral_health_oda(
    start_year: int = 2000,
    end_year: int = 2023,
    prices: str = "current",
    base_year: Optional[int] = None,
) -> pd.DataFrame:
    return _get_health_oda_indicator(
        indicator="imputed_multi_flow_disbursement_gross",
        start_year=start_year,
        end_year=end_year,
        prices=prices,
        base_year=base_year,
    )


if __name__ == "__main__":
    df = get_imputed_multilateral_health_oda(2018, 2023)
