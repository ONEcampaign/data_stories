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
{sort: "country", reverse: false, select:false, rows:10.1, format: {target: d3.format(".2%")}})
```


# EU Official Development Assistance (ODA) targets

This page presents our methodology to estimate the required ODA spending for EU countries to meet their ODA targets by 2030. It also outlines how we use historical data to estimate the required spending for the EU Institutions for the 2027-2034 period.

<div class="note">
For this work, we use ODA and GNI data from the OECD Development Assistance Committee. We also use economic projections from the IMF World Economic Outlook. We present ODA data following OECD DAC conventions and definitions. Data from 2018 is presented as grant equivalents. Unless otherwise noted, all amounts are in 2025 constant prices.
</div>

---

## Where are we today?
The latest year with available ODA data is 2023. These numbers are preliminary and subject to change. This data includes GNI estimates for all donors.

Since 2022, there has been a significant increase in in-donor refugee costs and aid to Ukraine. Since 2020, donors have also spent a significant amount of ODA on COVID-19 response. We do not yet have a full picture of how much ODA was spent on these items in 2023.

In 2023, the EU collectively spent **0.57%** of its GNI, or **€96.5 billion**, on ODA.  
<br>

## What are the targets?

While EU countries have committed to spending 0.7% of their collective GNI on ODA, individual countries have different targets. Some have committed to spending 0.70% of their GNI by 2030, while others have committed to spending 0.33% as ODA.

<br>

<div style="max-width:440px; margin-left:5%">
<h3>Individual country targets</h3>
${targetTable}
</div>

<br>
<br>


## Estimating the required spending to meet the targets

In order to estimate how much countries will need to spend by 2030 in order to meet their targets, we need two basic ingredients:
1. Data on how much they are spending now, a share of GNI.
2. Projections for how much their GNI will grow in the future.

#### ODA/GNI data
For the first, we use the latest available data, for 2023, as reported to the OECD DAC. This data measures Official Development Assistance (in grant equivalent terms) as a share of Gross National Income (GNI) for each EU country.

#### GNI growth projections
For the second, we use the IMF World Economic Outlook (WEO) projections for GDP growth. We use these projections as a proxy for GNI growth. We apply these projections to the latest GNI numbers to estimate how much countries will need to spend in the future to meet their targets.

The WEO projections are available up to 2028. For years beyond 2028, we use the average growth rate for 2026-28, and assume it will hold constant until 2034.

#### Projecting the required spending
We assume that countries will meet their ODA targets by 2030, and that they will get to their targets with linear yearly increases. For countries who are already spending above their target, we assume that they will sustain their current level of ODA spending as a percentage of GNI.

The following table shows how much EU 27 countries would have to spend per year to meet their **individual** targets by 2030, and sustain that spending (as a share of GNI) until 2034. 


```js
const additionalSpendingData = FileAttachment("./data/additional_spending_yearly.csv").csv({typed:true})
```

```js
const country = view(Inputs.select(["All"].concat(additionalSpendingData.map(d=>d.name_short)), {value: "All", label: "Select a country", unique: true, sort:true}));
```


<div class="card" style="max-width: 720px; padding: 0;">

```js
const additionalSpendingTable = view(Inputs.table(additionalSpendingData.filter(d => d.indicator == "Full" && d.name_short == country || country=="All"),{
    rows: 13.2,
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
        oda: d=> d.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 1})+"m",
        additional_oda: d=> d.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 1})+"m",
     },
     align:{
        year: "left"
     }

}))
```

</div>

Putting it all together, for the 2028 to 2034 period, EU countries would need to spend **€916 billion** euros to meet their ODA targets (in 2025 constant prices).

The following chart shows actual and required ODA spending for EU Member States, from 2018 to 2034.

<div class="card" style="max-width: 720px; padding: 0;">
<iframe src='https://flo.uri.sh/visualisation/19898927/embed' title='Interactive or visual content' class='flourish-embed-iframe' frameborder='0' scrolling='no' style='width:100%;height:600px;' sandbox='allow-same-origin allow-forms allow-scripts allow-downloads allow-popups allow-popups-to-escape-sandbox allow-top-navigation-by-user-activation'></iframe>
</div>


---

## The role of the EU Institutions?



EU Member states provide core funding to the EU Institutions through a number of instruments. The EU Institutions also have their own resources, which they can use to provide ODA.

The share of EU ODA provided by the EU Institutions has been **23.1% on average** over the current MFF period (2020 - 2022). Over the previous MFF period (2014-2020), it was 24.6%.

The EU Institutions spend an average of **€3.9 billion** per year (2020-2022), out of their own resources. This is **20.6%** of their total yearly spending (during the current MFF).

<div class="card" style="max-width: 640px;">

## EU Institutions ODA spending

<iframe src='https://flo.uri.sh/visualisation/19459650/embed' title='Interactive or visual content' class='flourish-embed-iframe' frameborder='0' scrolling='no' style='width:100%;height:550px;' sandbox='allow-same-origin allow-forms allow-scripts allow-downloads allow-popups allow-popups-to-escape-sandbox allow-top-navigation-by-user-activation'></iframe>
</div>
