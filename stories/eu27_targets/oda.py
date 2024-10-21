import json

import pandas as pd
from oda_data import donor_groupings, set_data_path, ODAData
from pydeflate import set_pydeflate_path

from stories import config
from stories.aid_to_africa.g7_plus_eui import download_all_official_eui
from stories.eu27_targets.common import (
    CURRENCY,
    EU27,
    LOWER_TARGET,
    TARGET,
    LOWER_TARGET_COUNTRIES,
)
from stories.eu27_targets.eui_share import download_eu_x_eui

set_data_path(config.Paths.raw_data)
set_pydeflate_path(config.Paths.raw_data)


def export_targets() -> None:
    eu_countries = donor_groupings()["eu27_countries"]

    goals = {}
    for code, country in eu_countries.items():
        goals[country] = TARGET if code not in LOWER_TARGET_COUNTRIES else LOWER_TARGET

    # Save as json
    with open(config.Paths.eu_project_data / "targets.json", "w") as f:
        json.dump(goals, f)


def get_total_oda_and_gni(
    years: int | list[int] = 2023, currency: str = "EUR"
) -> pd.DataFrame:

    oda = ODAData(years=years, donors=EU27 + [20918, 918], currency=currency)

    oda.load_indicator(["total_oda_official_definition", "gni"])

    df = (
        oda.get_data()
        .pivot(index=["year", "donor_code"], columns="indicator", values="value")
        .reset_index()
    )

    return df


def get_total_refugee_spending(years: int | list[int] = 2023) -> pd.DataFrame:

    oda = ODAData(years=years, donors=EU27 + [20918, 918], currency=CURRENCY)

    oda.load_indicator(["total_oda_official_definition", "idrc_ge_linked"])

    df = (
        oda.get_data()
        .pivot(index=["year", "donor_code"], columns="indicator", values="value")
        .reset_index()
    )

    df["idrc_share"] = (
        100 * df["idrc_ge_linked"] / df["total_oda_official_definition"].round(2)
    )
    return df


def get_total_ukraine_spending(years: int | list[int] = 2023) -> pd.DataFrame:

    oda = ODAData(
        years=years,
        donors=EU27 + [20918, 918],
        currency=CURRENCY,
    )

    oda.load_indicator(["recipient_total_flow_net"])

    df = oda.get_data().assign(
        share=lambda d: d.groupby(["year"])["value"].transform(
            lambda x: 100 * x / x.sum()
        )
    )

    df = df.pivot(
        index=["year", "donor_code", "recipient_code"],
        columns="indicator",
        values="value",
    ).reset_index()

    df = df.query("recipient_code == 85")

    return df


def remove_total_eu27_contributions(
    data: pd.DataFrame, years: int | list[int] = 2023
) -> pd.DataFrame:

    oda = ODAData(years=years, donors=EU27, currency=CURRENCY)

    oda.load_indicator(["eu_core_ge_linked"])

    df = (
        oda.get_data()
        .groupby(["year"], dropna=False)["value"]
        .sum()
        .reset_index()
        .rename(columns={"value": "eu_value"})
    )

    data = data.merge(df, on="year", how="left")

    data["total_oda_official_definition"] = data["total_oda_official_definition"].mask(
        data["donor_code"] == 918,
        data["total_oda_official_definition"] - data["eu_value"],
    )

    return data.drop(columns=["eu_value"])


def calculate_oda_gni_ratio(df: pd.DataFrame) -> pd.DataFrame:

    df["oda_gni_ratio"] = df["total_oda_official_definition"] / df["gni"]

    return df


def calculate_missing_oda(df: pd.DataFrame) -> pd.DataFrame:
    df["target"] = df.donor_code.map(
        lambda x: LOWER_TARGET if x in LOWER_TARGET_COUNTRIES else TARGET
    )
    df["missing_oda_target"] = (
        df["gni"] * df["target"] - df["total_oda_official_definition"]
    )

    df["missing_oda_target"] = df["missing_oda_target"].clip(lower=0)

    return df.drop(columns=["target"])


def add_target_column(df: pd.DataFrame) -> pd.DataFrame:
    df["target"] = df.donor_code.map(
        lambda x: LOWER_TARGET if x in LOWER_TARGET_COUNTRIES else TARGET
    )

    return df


def add_target_oda(df: pd.DataFrame) -> pd.DataFrame:
    df = add_target_column(df)
    df["target_oda"] = df["gni"] * df["target"]

    return df.drop(columns=["target"])


def calculate_missing_oda_07(df: pd.DataFrame) -> pd.DataFrame:
    df["missing_oda_07"] = df["gni"] * TARGET - df["total_oda_official_definition"]

    return df


def eu_countries_summary(df: pd.DataFrame) -> pd.DataFrame:
    data = df.groupby(["year"]).sum().reset_index()

    data["oda_gni_ratio"] = data["total_oda_official_definition"] / data["gni"]

    return data


def yearly_g7_share_of_eui():

    # Get all core contributions to EUI
    all_eui = (
        download_all_official_eui()
        .filter(["year", "value"])
        .groupby(["year"], as_index=False)["value"]
        .sum()
    )

    # Get G7 contributions to EUI
    eu27_eui = download_eu_x_eui(currency=CURRENCY).filter(["year", "value"])

    # Merge the two dataframes
    df = all_eui.merge(eu27_eui, on="year", suffixes=("_all", "_g7"), how="outer")

    # Calculate the share of G7 contributions to EUI
    df["g7_eui_share"] = df["value_g7"] / df["value_all"]

    return df.filter(["year", "g7_eui_share"])


def format_eu_totals_chart(data: pd.DataFrame) -> pd.DataFrame:
    data = data.filter(
        [
            "year",
            "oda_gni_ratio",
            "total_oda_official_definition",
            "missing_oda_target",
            "missing_oda_07",
        ]
    )

    data["oda_gni_ratio"] = (100 * data["oda_gni_ratio"]).round(2)
    data = data.rename(
        columns={
            "total_oda_official_definition": "Total ODA",
            "missing_oda_target": "Missing ODA (to individual targets)",
            "missing_oda_07": "Missing ODA (to collective 0.7% target)",
            "oda_gni_ratio": "ODA/GNI",
        }
    )
    return data


def get_total_oda_data(
    years: int | list[int],
    include_ukraine: bool = True,
    include_idrc: bool = True,
    use_2022_ukraine: bool | None = None,
    currency: str = "EUR",
) -> pd.DataFrame:
    """"""

    oda = get_total_oda_and_gni(years=years, currency=currency)

    if not include_idrc:
        refugees = (
            get_total_refugee_spending(years=years)
            .filter(["year", "donor_code", "idrc_ge_linked"])
            .fillna(0)
        )
        oda = oda.merge(refugees, on=["year", "donor_code"], how="left")
        oda["total_oda_official_definition"] = (
            oda["total_oda_official_definition"] - oda["idrc_ge_linked"]
        )
        oda = oda.drop(columns=["idrc_ge_linked"])

    if not include_ukraine:
        ukr = get_total_ukraine_spending(years=years)
        oda = oda.merge(ukr, on=["year", "donor_code"], how="left")

        if use_2022_ukraine:
            # For each donor_code, forward fill with 2022 value
            oda["recipient_total_flow_net"] = oda.groupby("donor_code")[
                "recipient_total_flow_net"
            ].transform(lambda x: x.ffill())

        else:
            oda = oda.fillna({"recipient_total_flow_net": 0})

        oda["total_oda_official_definition"] = (
            oda["total_oda_official_definition"] - oda["recipient_total_flow_net"]
        )
        oda = oda.drop(columns=["recipient_total_flow_net", "recipient_code"])

    return oda


if __name__ == "__main__":
    # oda_df = get_total_oda_and_gni(list(range(2018, 2024))).pipe(
    #     remove_total_eu27_contributions, years=list(range(2018, 2024))
    # )
    #
    # oda_df = calculate_oda_gni_ratio(oda_df)
    # oda_df = calculate_missing_oda(oda_df)
    # oda_df = calculate_missing_oda_07(oda_df)
    # eu_summary = eu_countries_summary(oda_df)
    # eu_summary.pipe(format_eu_totals_chart).to_clipboard(index=False)
    #
    # refugees_df = get_total_refugee_spending(list(range(2018, 2024)))
    # eu_refugees = (
    #     refugees_df.groupby(["year"], dropna=False).sum(numeric_only=True).reset_index()
    # ).assign(
    #     idrc_share=lambda d: (
    #         100 * d["idrc_ge_linked"] / d["total_oda_official_definition"]
    #     ).round(2)
    # )

    df = get_total_oda_data(
        years=list(range(2018, 2024)), include_ukraine=False, use_2022_ukraine=True
    )

    # eu_summary = exchange(
    #     eu_summary.assign(donor="France"),
    #     source_currency="USA",
    #     target_currency="FRA",
    #     rates_source="oecd_dac",
    #     id_column="donor",
    #     id_type="regex",
    #     date_column="year",
    #     value_column="missing_oda",
    #     target_column="missing_oda_eur",
    # )
