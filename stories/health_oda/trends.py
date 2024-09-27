import pandas as pd

from stories import config
from stories.health_oda.common import (
    filter_low_income_countries,
    filter_african_countries,
)
from stories.health_oda.get_oda import get_bilateral_health_oda, get_total_bilateral_oda


def low_income_and_africa_trend(
    start_year: int = 1990,
    end_year: int = 2023,
    prices: str = "constant",
    base_year: int = 2022,
):
    # Get bilateral health data
    full_data = get_bilateral_health_oda(
        start_year=start_year, end_year=end_year, prices=prices, base_year=base_year
    )

    # Filter countries
    low_income = filter_low_income_countries(full_data).assign(
        recipient_group="Low income"
    )
    africa = filter_african_countries(full_data).assign(recipient_group="Africa")

    df = pd.concat([low_income, africa], ignore_index=True)

    # Group the data
    df = (
        df.groupby(["year", "recipient_group", "prices"], dropna=False, observed=True)[
            ["value"]
        ]
        .sum()
        .reset_index()
    )

    return df


def group_by_grouper(df: pd.DataFrame, grouper: list[str]) -> pd.DataFrame:
    return df.groupby(grouper, dropna=False, observed=True)["value"].sum().reset_index()


def health_share_trend(
    start_year: int = 1990,
    end_year: int = 2023,
    prices: str = "constant",
    base_year: int = 2022,
) -> pd.DataFrame:

    # Define the grouper
    grouper = ["year"]

    # Get the data for all sectors
    all_sectors = get_total_bilateral_oda(
        start_year=start_year, end_year=end_year, prices=prices, base_year=base_year
    ).pipe(group_by_grouper, grouper=grouper)

    # Get the data for health
    health = get_bilateral_health_oda(
        start_year=start_year, end_year=end_year, prices=prices, base_year=base_year
    ).pipe(group_by_grouper, grouper=grouper)

    # Merge the data
    data = pd.merge(all_sectors, health, on=grouper, suffixes=("_total", "_health"))

    # Calculate the share
    data["share"] = round(100 * data["value_health"] / data["value_total"], 2)

    return data


def pre_post_covid_trend(
    prices: str = "constant",
    base_year: int = 2022,
) -> pd.DataFrame:

    # Define the grouper
    grouper = ["sector", "indicator"]

    # Get the data for health
    health_pre = (
        get_bilateral_health_oda(
            start_year=2017, end_year=2019, prices=prices, base_year=base_year
        )
        .assign(sector="Health", indicator="Pre-COVID")
        .groupby(["year"] + grouper, dropna=False, observed=True)["value"]
        .sum()
        .reset_index()
        .groupby(grouper, dropna=False, observed=True)["value"]
        .mean()
        .reset_index()
    )

    # Get the data for health
    health_post = (
        get_bilateral_health_oda(
            start_year=2020, end_year=2022, prices=prices, base_year=base_year
        )
        .assign(sector="Health", indicator="Post-COVID")
        .groupby(["year"] + grouper, dropna=False, observed=True)["value"]
        .sum()
        .reset_index()
        .groupby(grouper, dropna=False, observed=True)["value"]
        .mean()
        .reset_index()
    )
    # Merge the data
    data = (
        pd.concat([health_pre, health_post], ignore_index=True)
        .pivot(index="sector", columns="indicator", values="value")
        .reset_index()
    )

    return data


if __name__ == "__main__":
    lic_africa = low_income_and_africa_trend(1990, 2022)
    lic_africa.pivot(
        index=["year", "prices"], columns="recipient_group", values="value"
    ).to_csv(config.Paths.health_oda / "total_health_oda_trend.csv")

    health_share = health_share_trend(1990, 2022)
    health_share.rename(
        columns={
            "value_total": "Total ODA",
            "value_health": "Health ODA",
            "share": "Health Share",
        }
    ).to_csv(config.Paths.health_oda / "health_share_trend.csv", index=False)

    covid = pre_post_covid_trend()
    covid.to_csv(config.Paths.health_oda / "pre_post_covid_trend.csv", index=False)
