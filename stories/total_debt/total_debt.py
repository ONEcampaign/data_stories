from bblocks import (
    WorldEconomicOutlook,
    set_bblocks_data_path,
    add_short_names_column,
    convert_id,
)

from stories import config

set_bblocks_data_path(config.Paths.raw_data)


weo = WorldEconomicOutlook()

print(weo.available_indicators())

# INTEREST = (OVERALL_FISCAL_BALANCE, "-", PRIMARY_BALANCE)

OVERALL_FISCAL_BALANCE = "GGXCNL_NGDP"
PRIMARY_BALANCE = "GGXONLB_NGDP"

GG_NET_DEBT = "GGXWDN_NGDP"

G7 = ["CAN", "DEU", "FRA", "ITA", "JPN", "GBR", "USA"]


weo.load_data([OVERALL_FISCAL_BALANCE, PRIMARY_BALANCE, GG_NET_DEBT])

overall = weo.get_data(OVERALL_FISCAL_BALANCE).query("year.dt.year == 2023")
primary = weo.get_data(PRIMARY_BALANCE).query("year.dt.year == 2023")
debt = weo.get_data(GG_NET_DEBT).query("year.dt.year == 2023")

df = overall.merge(primary, on=["iso_code", "year"], suffixes=("_overall", "_primary"))
df["Interest Payments"] = round(df.value_overall - df.value_primary, 2)

df = add_short_names_column(df, id_column="iso_code", id_type="ISO3")
df["continent"] = convert_id(df.iso_code, from_type="ISO3", to_type="continent")

df = df.loc[lambda d: (d.iso_code.isin(G7)) | (d.continent == "Africa")]

df = df.sort_values("Interest Payments", ascending=False)


debt = add_short_names_column(debt, id_column="iso_code", id_type="ISO3")
debt["continent"] = convert_id(debt.iso_code, from_type="ISO3", to_type="continent")


debt = debt.loc[lambda d: (d.iso_code.isin(G7)) | (d.continent == "Africa")]

indicator = {GG_NET_DEBT: "General government net debt (Percent of GDP)"}

debt = debt.assign(indicator_name=lambda d: d.indicator.map(indicator))

debt = debt.sort_values("value", ascending=False)
