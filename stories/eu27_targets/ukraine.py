import pandas as pd
from oda_data import donor_groupings
from oda_reader import download_dac2a, download_dac1

from stories.config import Paths

START: int = 2018

eu27 = list(donor_groupings()["eu27_countries"].keys())


def download_eui_ukr_bilateral():

    filters = {
        "donor": "4EU001",
        "recipient": "UKR",
        "measure": "206",
        "price_base": "V",
        "unit_measure": "USD",
    }
    return download_dac2a(start_year=START, filters=filters)


def download_eui_ukr_multi():

    filters = {
        "donor": "4EU001",
        "recipient": "UKR",
        "measure": "106",
        "price_base": "V",
        "unit_measure": "USD",
    }
    return download_dac2a(start_year=START, filters=filters)


def download_ukr_bilateral():

    filters = {
        "recipient": "UKR",
        "measure": "206",
        "price_base": "V",
        "unit_measure": "USD",
    }
    return download_dac2a(start_year=START, filters=filters).pipe(filter_eu27)


def download_ukr_multi():

    filters = {
        "recipient": "UKR",
        "measure": "106",
        "price_base": "V",
        "unit_measure": "USD",
    }
    return download_dac2a(start_year=START, filters=filters).pipe(filter_eu27)


def download_eui_all_bilateral():

    filters = {
        "donor": "4EU001",
        "recipient": "DPGC",
        "measure": "206",
        "price_base": "V",
        "unit_measure": "USD",
    }
    return download_dac2a(start_year=START, filters=filters)


def download_eui_all_multi():

    filters = {
        "donor": "4EU001",
        "recipient": "DPGC",
        "measure": "106",
        "price_base": "V",
        "unit_measure": "USD",
    }
    return download_dac2a(start_year=START, filters=filters)


def download_all_bilateral():

    filters = {
        "recipient": "DPGC",
        "measure": "206",
        "price_base": "V",
        "unit_measure": "USD",
    }
    return download_dac2a(start_year=START, filters=filters).pipe(filter_eu27)


def download_all_multi():

    filters = {
        "recipient": "DPGC",
        "measure": "106",
        "price_base": "V",
        "unit_measure": "USD",
    }
    return download_dac2a(start_year=START, filters=filters).pipe(filter_eu27)


def download_to_eui():
    filters = {
        "flow_type": "1120",
        "measure": "2102",
        "price_base": "V",
        "unit_measure": "USD",
    }
    return download_dac1(start_year=START, filters=filters).pipe(filter_eu27)


def download_all_official_eui():
    filters = {
        "donor": ["DAC", "WXDAC"],
        "flow_type": "1120",
        "measure": "2102",
        "unit_measure": "USD",
        "price_base": "V",
    }
    return download_dac1(start_year=START, filters=filters)


def yearly_ukr_share_eui():
    ukr = download_eui_ukr_bilateral()
    all = download_eui_all_bilateral()

    df = (
        pd.concat([ukr, all], ignore_index=True)
        .filter(["year", "recipient_name", "value"])
        .pivot(index=["year"], columns="recipient_name", values="value")
        .reset_index()
    )

    df["share"] = df["Ukraine"] / df["Developing countries"]

    return df


def yearly_ukr_share_eui_multi():
    ukr = download_eui_ukr_multi()
    all = download_eui_all_multi()

    df = (
        pd.concat([ukr, all], ignore_index=True)
        .filter(["year", "recipient_name", "value"])
        .pivot(index=["year"], columns="recipient_name", values="value")
        .reset_index()
    )

    df["share"] = df["Ukraine"] / df["Developing countries"]

    return df


def eui_imputed_multi_ukr():
    # Get EU contributions to EUI
    eu_eui = download_to_eui().groupby(["year"], as_index=False)["value"].sum()
    eui_ukr = yearly_ukr_share_eui().filter(["year", "share"])

    # Merge the two dataframes
    df = eu_eui.merge(eui_ukr, on="year", how="outer")
    df["value"] = df["value"] * df["share"]
    return df.filter(["year", "value"])


def yearly_share_of_eui():

    # Get all core contributions to EUI
    all_eui = (
        download_all_official_eui()
        .filter(["year", "value"])
        .groupby(["year"], as_index=False)["value"]
        .sum()
    )

    # Get G7 contributions to EUI
    g7_eui = download_to_eui().filter(["year", "value"])

    # Merge the two dataframes
    df = all_eui.merge(g7_eui, on="year", suffixes=("_all", "_g7"), how="outer")

    # Calculate the share of G7 contributions to EUI
    df["g7_eui_share"] = df["value_g7"] / df["value_all"]

    return df.filter(["year", "g7_eui_share"])


def calculate_non_eu_value(eui_data: pd.DataFrame) -> pd.DataFrame:
    # Remove the part that will appear in the imputed data
    imputed_share = yearly_share_of_eui()

    return (
        eui_data.merge(imputed_share, on="year", how="left")
        .assign(eui_share=lambda d: 1 - d.eui_share)
        .assign(value=lambda d: d.value * d.eui_share)
    )


def eu_eui_ukr_bilateral():

    eu = download_eui_ukr_bilateral()
    eui = download_eui_ukr_bilateral()

    return (
        pd.concat([eu, eui], ignore_index=True)
        .groupby(["year", "recipient_name"], as_index=False)[["value"]]
        .sum()
    )


def eu_eui_all_bilateral():

    eu = download_all_bilateral()
    eui = download_eui_all_bilateral()

    return (
        pd.concat([eu, eui], ignore_index=True)
        .groupby(["year", "recipient_name"], as_index=False)[["value"]]
        .sum()
    )


def eu_eui_ukr_share() -> pd.DataFrame:
    # Get bilateral spending from all of EU + EUI to Ukraine
    ukr_bilateral = eu_eui_ukr_bilateral()

    # Get bilateral spending from all of EU + EUI to all developing countries
    all_bilateral = eu_eui_all_bilateral()

    # Total bilateral spending
    bilateral = pd.concat([ukr_bilateral, all_bilateral], ignore_index=True)

    # ----- Imputations   ------

    # Get imputed to Ukraine from EU countries
    ukr_imputed = (
        download_ukr_multi()
        .groupby(["year", "recipient_name"], dropna=False, observed=True)[["value"]]
        .sum()
        .reset_index()
    )
    # Get imputed to all developing countries from EU countries
    all_imputed = (
        download_all_multi()
        .groupby(["year", "recipient_name"])[["value"]]
        .sum()
        .reset_index()
    )

    # Get imputed from EU institutions to Ukraine
    eu_ukr_imputed = download_eui_ukr_multi()

    eui_portion_ukr_imputed = eui_imputed_multi_ukr().assign(
        recipient_name="Ukraine", value=lambda d: d.value * -1
    )
    eui_portion_all_imputed = (
        download_to_eui()
        .groupby(["year"], as_index=False)["value"]
        .sum()
        .reset_index()
        .assign(recipient_name="Developing countries", value=lambda d: d.value * -1)
    )

    imputed_to_subtract = pd.concat(
        [eui_portion_ukr_imputed, eui_portion_all_imputed], ignore_index=True
    )

    imputed = (
        pd.concat(
            [ukr_imputed, all_imputed, imputed_to_subtract, eu_ukr_imputed],
            ignore_index=True,
        )
        .groupby(["year", "recipient_name"])[["value"]]
        .sum()
        .reset_index()
        .assign(value=lambda d: d.value.clip(lower=0))
    )

    df = (
        pd.concat([bilateral, imputed], ignore_index=True)
        .groupby(["year", "recipient_name"], as_index=False)["value"]
        .sum()
    )

    df = df.pivot(
        index=["year"], columns="recipient_name", values="value"
    ).reset_index()

    df["share"] = round(100 * df["Ukraine"] / df["Developing countries"], 2)

    return df


def filter_eu27(data: pd.DataFrame) -> pd.DataFrame:
    return data.loc[lambda d: d.donor_code.isin(eu27)]


def eu_inst_ukr_share() -> pd.DataFrame:
    eu_ukr_b = yearly_ukr_share_eui()
    eu_ukr_m = yearly_ukr_share_eui_multi()

    df = (
        pd.concat([eu_ukr_b, eu_ukr_m], ignore_index=True)
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
    ...
    data = eu_eui_ukr_share()
    # data.to_csv(Paths.aid_to_africa_output / "g7_eui_africa_share.csv", index=False)

    from pydeflate import set_pydeflate_path, exchange

    #
    # set_pydeflate_path(Paths.raw_data)
    # eu_data = eu_inst_africa_share()
    #
    eu_data = exchange(
        data.assign(id_col="EU Institutions"),
        source_currency="USA",
        target_currency="FRA",
        rates_source="oecd_dac",
        id_column="id_col",
        value_column="Ukraine",
        target_column="Ukraine",
        date_column="year",
        id_type="DAC",
    )

    eu_data.to_csv(Paths.eu_project_data / "eu_ukr.csv", index=False)
    #
    # eu_data2 = exchange(
    #     eu_data2.assign(id_col="EU Institutions"),
    #     source_currency="USA",
    #     target_currency="FRA",
    #     rates_source="oecd_dac",
    #     id_column="id_col",
    #     value_column="Developing countries",
    #     target_column="Developing countries",
    #     date_column="year",
    #     id_type="DAC",
    # )

    # eu_data.to_csv(Paths.aid_to_africa_output / "eu_africa_share.csv", index=False)
