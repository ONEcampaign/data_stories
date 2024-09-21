import pandas as pd
from oda_data import recipient_groupings
from oda_data.clean_data.schema import OdaSchema

from stories import config

RECIPIENT_GROUPS = {
    "Developing Countries, Total": None,
    "Africa": recipient_groupings()["african_countries_regional"],
    "Sahel countries": recipient_groupings()["sahel"],
    "Least Developed Countries": recipient_groupings()["ldc_countries"],
    "France priority countries": recipient_groupings()["france_priority"],
}

CURRENCIES: dict = {"USD": "USA", "EUR": "EUI", "GBP": "GBR", "CAD": "CAN"}


def add_income_grouping(df: pd.DataFrame) -> pd.DataFrame:
    """Add the income groupings to the dataframe."""
    from bblocks import add_income_level_column, set_bblocks_data_path

    set_bblocks_data_path(config.Paths.raw_data)

    df = add_income_level_column(
        df, id_column=OdaSchema.RECIPIENT_CODE, id_type="DACCode"
    )

    return df


def get_health_purpose_codes() -> list[str]:
    """Return the purpose codes for health."""
    from oda_data.tools import sector_lists

    sectors = list()

    sectors.extend(sector_lists.health_general)
    sectors.extend(sector_lists.health_basic)
    sectors.extend(sector_lists.health_NCDs)
    sectors.extend(sector_lists.pop_RH)

    return sectors


def filter_health_sectors(df: pd.DataFrame) -> pd.DataFrame:
    # Load the list of sectors
    sectors = get_health_purpose_codes()

    # Filter the dataframe
    return df[df[OdaSchema.PURPOSE_CODE].isin(sectors)].reset_index(drop=True)


def filter_low_income_countries(df: pd.DataFrame) -> pd.DataFrame:
    """Filter the dataframe to include only low-income countries."""
    df = add_income_grouping(df)

    return df.loc[lambda d: d.income_group == "Low income"].reset_index(drop=True)
