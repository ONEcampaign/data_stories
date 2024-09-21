import pandas as pd

from stories import config
from stories.health_oda.common import (
    filter_low_income_countries,
    filter_african_countries,
)
from stories.health_oda.get_oda import get_bilateral_health_oda


def low_income_trend(
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


if __name__ == "__main__":
    df = low_income_trend(1990, 2022)
    df.pivot(
        index=["year", "prices"], columns="recipient_group", values="value"
    ).to_csv(config.Paths.health_oda / "total_health_oda_trend.csv")
