---
title: EU ODA targets
toc: true
sidebar: false
---


```js
const  targetData = await FileAttachment("./data/targets.json").json()
const targetTableData = Object.entries(targetData).map(([country, target]) => ({country, target}))
```

```js display
const targetTable = Inputs.table(targetTableData,
{sort: "target", reverse: false, rows:23.5, format: {target: d3.format(".1%")}})
```


# EU ODA Targets

This is a working document which presents an overview of our methodological considerations and options for  estimating the ODA required for EU countries to meet their ODA targets.

<div class="note">
For this work, we use ODA and GNI data from the OECD Development Assistance Committee. We also use economic projections from the IMF World Economic Outlook
</div>

---

## Where are we today?
The latest year with available ODA data is 2023. These numbers are preliminary and subject to change. This data includes GNI estimates for all donors.

Since 2022, there has been a significant increase in in-donor refugee costs and aid to Ukraine. Since 2020, donors have also spent a significant amount of ODA on COVID-19 response. Since 2023 numbers are preliminary, we do not have a full picture of how much ODA was spent on these items in 2023.

In 2023, the EU collectively spent **0.57%** of its GNI, or **€96.5 billion**, on ODA. That is **€32 billion** short of its collective target of 0.7% of GNI.

In 2018, it spent 0.44% of its GNI, or €60 billion. That year, it was €36.7 billion short of its collective target of 0.7% of GNI.

While EU countries have committed to spending 0.7% of their collective GNI on ODA, individual countries have different targets.

<div class="grid grid-cols-2"style="grid-auto-rows: auto;">

<div class="card grid-rowspan-2" style="max-width: 640px;">
<h2>Total EU ODA spending and missing ODA to targets</h2><br>
<iframe src='https://flo.uri.sh/story/2462747/embed' title='Interactive or visual content' class='flourish-embed-iframe' frameborder='0' scrolling='no' style='width:100%;height:550px;' sandbox='allow-same-origin allow-forms allow-scripts allow-downloads allow-popups allow-popups-to-escape-sandbox allow-top-navigation-by-user-activation'></iframe>
</div>

<div class=card style="max-width:440px;">
<h2>Individual country targets</h2><br>
${targetTable}
</div>

</div>


### A more complex picture

A significant portion of EU ODA is spent on in-donor refugee costs. They can only be counted for the first year after refugees arrive in donor countries. That means they don't represent a stable increase in ODA spending.

In 2023, this accounted for **€14.8 billion**, or **13%** of total EU ODA. This is a significant increase from the average of 2018-2021, for example, when EU countries spent €5.5 billion per year on average, or 7% of total EU ODA.
 
Similarly, while EU support to Ukraine has increased significantly since Russia's invasion started. In 2022, it accounted for some **21%** of total EU ODA, or **€20 billion**. Full data for 2023 is not yet available.

In comparison, in 2021, total EU ODA to Ukraine was €2 billion, or just over 2% of total EU ODA.

### What about the EU Institutions?
EU Member states provide core funding to the EU Institutions through a number of instruments. The EU Institutions also have their own resources, which they can use to provide ODA.

The share of ODA provided by the EU Institutions has been x% on average over the current MFF period (2020 - to date). Over the previous MFF period (2014-2020), it was y%.

The EU Institutions spend an average of €x billion per year, out of their own resources. This is z% of their total yearly spending and represents a% of total EU ODA.



---

## Projecting the required spending

We project the required ODA spending for EU countries to meet their ODA targets. We use the IMF World Economic Outlook projections for GDP growth. Using them as a proxy for GNI growth, we and apply them to the latest GNI numbers. 

We assume that EU countries will meet their ODA targets by 2030, and that they will get to their targets with linear yearly increases.

For countries who are already spending above their target, we assume that they will sustain their current level of ODA spending as a percentage of GNI.

We evaluate four scenarios. In all cases, donors meet their targets by 2030 and continue spending their target ODA/GNI until 2034.
1. The starting point for their trajectory towards their 2030 target is their preliminary 2023 ODA/GNI ratio.
2. The starting point is 2023 spending, excluding only in-donor refugee costs.
3. The starting point is 2023 spending, excluding only aid to Ukraine.
4. The starting point is 2023 spending excluding in-donor refugee costs and aid to Ukraine.

```js
const scenarioData = FileAttachment("./data/scenario_totals.json").json()
```

In  total, for the 2028 to 2034 period, EU countries would need to spend the following amounts to meet their ODA targets. All amounts are in 2025 constant prices.

<div class="grid grid-cols-4">

<div class="card">
<h2> Scenario 1</h2>
<div class="big">€${(scenarioData['full']/1e3).toFixed(0)} billion</div>
<div class="muted">Including IDRC and Ukraine spending</div>
</div>

<div class="card">
<h2> Scenario 2</h2>
<div class="big">€${(scenarioData['no_idrc']/1e3).toFixed(0)} billion</div>
<div class="muted">Excluding IDRC spending</div>
</div>

<div class="card">
<h2> Scenario 3</h2>
<div class="big">€${(scenarioData['no_ukr']/1e3).toFixed(0)} billion</div>
<div class="muted">Excluding Ukraine spending</div>
</div>

<div class="card">
<h2> Scenario 4</h2>
<div class="big">€${(scenarioData['no_ukr_no_idrc']/1e3).toFixed(0)} billion</div>
<div class="muted">Excluding Ukraine and IDRC spending</div>
</div>

</div>


---

## What does this mean for individual countries?

Not taking into account additional spending by the EU Institutions our of own resources, the following table shows how much EU 27 countries would have to spend per year to meet their **individual** targets by 2030, and sustain that spending (as a share of GNI) until 2034. 

```js
const additionalSpendingData = FileAttachment("./data/additional_spending_yearly.csv").csv({typed:true})
```


```js
const selectScenario = view(Inputs.radio(additionalSpendingData.map(d => d.indicator), {unique:true, value: "Full", label: "Select scenario"}))
```

<div class="card" style="max-width: 700px">

```js
const additionalSpendingTable = view(Inputs.table(additionalSpendingData.filter(d => d.indicator == selectScenario),{
    rows: 15.5,
    columns: ["year","name_short", "oda_gni_ratio", "oda", "additional_oda"],
    header: {"year": "Year", "oda_gni_ratio": "ODA/GNI (%)", "oda": "Projected ODA", "additional_oda": "Additional ODA",
        "name_short": "Country",
    },
    width: {
        "year": 100,
        "name_short": 130
     },
     layout: "auto",

     format:{
        year: d=>d.toFixed(0),
        oda_gni_ratio: d => (100*d).toFixed(2),
        oda: d=> d.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 1}),
        additional_oda: d=> d.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 1}),
     },
     align:{
        year: "left"
     }

}))
```

</div>
