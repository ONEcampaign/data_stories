import pandas as pd
from oda_reader import download_dac2a, download_dac1

from stories.config import Paths

START: int = 1960


def download_eui_africa_bilateral():

    filters = {"donor": "4EU001", "recipient": "F", "measure": "206", "price_base": "V"}
    return download_dac2a(start_year=START, filters=filters)


def download_eui_africa_multi():

    filters = {"donor": "4EU001", "recipient": "F", "measure": "106", "price_base": "V"}
    return download_dac2a(start_year=START, filters=filters)


def download_g7_africa_bilateral():

    filters = {"donor": "G7", "recipient": "F", "measure": "206", "price_base": "V"}
    return download_dac2a(start_year=START, filters=filters)


def download_g7_africa_multi():

    filters = {"donor": "G7", "recipient": "F", "measure": "106", "price_base": "V"}
    return download_dac2a(start_year=START, filters=filters)


def download_eui_all_bilateral():

    filters = {
        "donor": "4EU001",
        "recipient": "DPGC",
        "measure": "206",
        "price_base": "V",
    }
    return download_dac2a(start_year=START, filters=filters)


def download_eui_all_multi():

    filters = {
        "donor": "4EU001",
        "recipient": "DPGC",
        "measure": "106",
        "price_base": "V",
    }
    return download_dac2a(start_year=START, filters=filters)


def download_g7_all_bilateral():

    filters = {"donor": "G7", "recipient": "DPGC", "measure": "206", "price_base": "V"}
    return download_dac2a(start_year=START, filters=filters)


def download_g7_all_multi():

    filters = {"donor": "G7", "recipient": "DPGC", "measure": "106", "price_base": "V"}
    return download_dac2a(start_year=START, filters=filters)


def download_g7_eui():
    filters = {"donor": "G7", "flow_type": "1120", "measure": "2102", "price_base": "V"}
    return download_dac1(start_year=START, filters=filters)


def download_all_official_eui():
    filters = {
        "donor": ["DAC", "WXDAC"],
        "flow_type": "1120",
        "measure": "2102",
        "price_base": "V",
    }
    return download_dac1(start_year=START, filters=filters)


def yearly_africa_share_eui():
    africa = download_eui_africa_bilateral()
    all = download_eui_all_bilateral()

    df = (
        pd.concat([africa, all], ignore_index=True)
        .filter(["year", "recipient_name", "value"])
        .pivot(index=["year"], columns="recipient_name", values="value")
        .reset_index()
    )

    df["share"] = df["Africa"] / df["Developing countries"]

    return df


def yearly_africa_share_eui_multi():
    africa = download_eui_africa_multi()
    all = download_eui_all_multi()

    df = (
        pd.concat([africa, all], ignore_index=True)
        .filter(["year", "recipient_name", "value"])
        .pivot(index=["year"], columns="recipient_name", values="value")
        .reset_index()
    )

    df["share"] = df["Africa"] / df["Developing countries"]

    return df


def g7_eui_imputed_multi_africa():
    # Get G7 contributions to EUI
    g7_eui = download_g7_eui().filter(["year", "value"])
    eui_africa = yearly_africa_share_eui().filter(["year", "share"])

    # Merge the two dataframes
    df = g7_eui.merge(eui_africa, on="year", how="outer")
    df["value"] = df["value"] * df["share"]
    return df.filter(["year", "value"])


def yearly_g7_share_of_eui():

    # Get all core contributions to EUI
    all_eui = (
        download_all_official_eui()
        .filter(["year", "value"])
        .groupby(["year"], as_index=False)["value"]
        .sum()
    )

    # Get G7 contributions to EUI
    g7_eui = download_g7_eui().filter(["year", "value"])

    # Merge the two dataframes
    df = all_eui.merge(g7_eui, on="year", suffixes=("_all", "_g7"), how="outer")

    # Calculate the share of G7 contributions to EUI
    df["g7_eui_share"] = df["value_g7"] / df["value_all"]

    return df.filter(["year", "g7_eui_share"])


def calculate_non_g7_value(eui_data: pd.DataFrame) -> pd.DataFrame:
    # Remove the part that will appear in the imputed data
    imputed_share = yearly_g7_share_of_eui()

    return (
        eui_data.merge(imputed_share, on="year", how="left")
        .assign(g7_eui_share=lambda d: 1 - d.g7_eui_share)
        .assign(value=lambda d: d.value * d.g7_eui_share)
    )


def g7_eui_africa_bilateral():

    g7 = download_g7_africa_bilateral()
    eui = download_eui_africa_bilateral()

    return (
        pd.concat([g7, eui], ignore_index=True)
        .groupby(["year", "recipient_name"], as_index=False)[["value"]]
        .sum()
    )


def g7_eui_all_bilateral():

    g7 = download_g7_all_bilateral()
    eui = download_eui_all_bilateral()

    return (
        pd.concat([g7, eui], ignore_index=True)
        .groupby(["year", "recipient_name"], as_index=False)[["value"]]
        .sum()
    )


def g7_eui_africa_share() -> pd.DataFrame:
    africa_bilateral = g7_eui_africa_bilateral()
    all_bilateral = g7_eui_all_bilateral()

    bilateral = pd.concat([africa_bilateral, all_bilateral], ignore_index=True)

    africa_imputed = download_g7_africa_multi()
    all_imputed = download_g7_all_multi()

    eu_africa_imputed = download_eui_africa_multi()

    eui_portion_africa_imputed = g7_eui_imputed_multi_africa().assign(
        recipient_name="Africa", value=lambda d: d.value * -1
    )
    eui_portion_all_imputed = (
        download_g7_eui()
        .filter(["year", "value"])
        .assign(recipient_name="Developing countries", value=lambda d: d.value * -1)
    )

    imputed_to_subtract = pd.concat(
        [eui_portion_africa_imputed, eui_portion_all_imputed], ignore_index=True
    )

    imputed = pd.concat(
        [africa_imputed, all_imputed, imputed_to_subtract, eu_africa_imputed],
        ignore_index=True,
    ).filter(["year", "recipient_name", "value"])

    df = (
        pd.concat([bilateral, imputed], ignore_index=True)
        .groupby(["year", "recipient_name"], as_index=False)["value"]
        .sum()
    )

    df = df.pivot(
        index=["year"], columns="recipient_name", values="value"
    ).reset_index()

    df["share"] = round(100 * df["Africa"] / df["Developing countries"], 2)

    return df


def eu_inst_africa_share() -> pd.DataFrame:
    eu_afr_b = yearly_africa_share_eui()
    eu_afr_m = yearly_africa_share_eui_multi()

    df = (
        pd.concat([eu_afr_b, eu_afr_m], ignore_index=True)
        .groupby("year", as_index=False, dropna=False)[
            ["Africa", "Developing countries"]
        ]
        .sum()
    ).assign(
        donor_name="EU Institutions",
        share=lambda d: d.Africa / d["Developing countries"],
        currency="USD",
        prices="current",
    )

    return df


if __name__ == "__main__":
    data = g7_eui_africa_share()
    data.to_csv(Paths.aid_to_africa_output / "g7_eui_africa_share.csv", index=False)

    eu_data = eu_inst_africa_share()
    eu_data.to_csv(Paths.aid_to_africa_output / "eu_africa_share.csv", index=False)
