import pandas as pd

from stories import config
from stories.health_oda.get_oda import (
    get_total_bilateral_oda,
    get_bilateral_health_oda,
    get_imputed_multilateral_health_oda,
)
from stories.health_oda.trends import group_by_grouper


def filter_g7_countries(df: pd.DataFrame) -> pd.DataFrame:
    """keep only the G7 countries."""
    g7_donors = [
        4,  # France
        5,  # Germany
        6,  # Italy
        12,  # United Kingdom
        301,  # Canada
        302,  # United States
        701,  # Japan
    ]

    return df.loc[lambda d: d.donor_code.isin(g7_donors)].reset_index(drop=True)


def g7_health_share_trend(
    start_year: int = 2012,
    end_year: int = 2022,
    prices: str = "constant",
    base_year: int = 2022,
) -> pd.DataFrame:

    # Define the grouper
    grouper = ["year"]

    # Get the data for all sectors
    all_sectors_bilateral = get_total_bilateral_oda(
        start_year=start_year, end_year=end_year, prices=prices, base_year=base_year
    )

    all_sectors_multilateral = get_imputed_multilateral_health_oda(
        start_year=start_year - 2, end_year=end_year, prices=prices, base_year=base_year
    ).astype({"value": float})

    all_sectors = (
        pd.concat([all_sectors_bilateral, all_sectors_multilateral], ignore_index=True)
        .assign(value=lambda d: d.value.fillna(0))
        .pipe(filter_g7_countries)
        .pipe(group_by_grouper, grouper=grouper)
    )

    # Get the data for health
    health_bilateral = get_bilateral_health_oda(
        start_year=start_year, end_year=end_year, prices=prices, base_year=base_year
    )

    health_multilateral = get_imputed_multilateral_health_oda(
        start_year=start_year, end_year=end_year, prices=prices, base_year=base_year
    ).astype({"value": float})

    health = (
        pd.concat([health_bilateral, health_multilateral], ignore_index=True)
        .pipe(filter_g7_countries)
        .pipe(group_by_grouper, grouper=grouper)
    )

    # Merge the data
    data = pd.merge(all_sectors, health, on=grouper, suffixes=("_total", "_health"))

    # Calculate the share
    data["share"] = round(100 * data["value_health"] / data["value_total"], 2)
    data["value_health"] = data["value_health"].map("{:,.0f}".format)
    data["value_total"] = data["value_total"].map("{:,.0f}".format)

    return data


if __name__ == "__main__":
    health_share = g7_health_share_trend(2012, 2022)
    health_share.rename(
        columns={
            "value_total": "Total ODA",
            "value_health": "Health ODA",
            "share": "Health Share",
        }
    ).to_csv(config.Paths.health_oda / "g7_health_share_trend.csv", index=False)
