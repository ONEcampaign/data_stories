---
title: EU ODA targets
toc: false
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

This page summarises the methodology we use for estimating the ODA required for EU countries to meet their ODA targets.

<div class="note">
For this work, we use ODA and GNI data from the OECD Development Assistance Committee. We also use economic projections from the IMF World Economic Outlook
</div>

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

## Projecting the required spending

We project the required ODA spending for EU countries to meet their ODA targets. We use the IMF World Economic Outlook projections for GDP growth. Using them as a proxy for GNI growth, we and apply them to the latest GNI numbers. 

We assume that EU countries will meet their ODA targets by 2030, and that they will get to their targets with linear yearly increases.

For countries who are already spending above their target, we assume that they will sustain their current level of ODA spending as a percentage of GNI.

We evaluate a few scenarios:
- EU countries meet their targets by 2030, starting from their 2023 levels which included high spending on in-donor refugee costs and Ukraine.
- EU countries meet their targets by 2030, not counting in-donor refugee costs.
- EU countries meet their targets by 2030, not counting Ukraine spending.
- EU countries meet their targets by 2030, excluding in-donor refugee costs and Ukraine spending.


<div class="card grid-rowspan-2" style="max-width: 840px;">
<h2>ODA/GNI trajectories for EU countries</h2><br>
<iframe src='https://flo.uri.sh/visualisation/18656439/embed' title='Interactive or visual content' class='flourish-embed-iframe' frameborder='0' scrolling='no' style='width:100%;height:80rem;' sandbox='allow-same-origin allow-forms allow-scripts allow-downloads allow-popups allow-popups-to-escape-sandbox allow-top-navigation-by-user-activation'></iframe>
</div>



**What does this mean for individual countries?**

Not taking into account additional spending by the EU Institutions our of own resources, the following chart shows how much EU 27 countries would have to spend per year to meet their **individual** targets by 2030. 

Meeting all of the targets, without additional spending from the EU institutions, would only get EU countries to about 0.66-0.69% of GNI by 2030 (depending on the starting point (whether including current IDRC and Ukraine spending or not)).

By 2030, EU countries would need to spend between **€126 billion** and **€131 billion** (in 2025 constant prices) to meet their individual targets. That translates to about €165 billion to €171 billion in current prices.

The following chart also shows the amounts that individual countries would need to spend to meet their ODA targets by 2030. 

<div class="card grid-rowspan-2" style="max-width: 720px;">
<h2>Spending trajectories for EU countries</h2><br>
<iframe src='https://flo.uri.sh/story/2467931/embed' title='Interactive or visual content' class='flourish-embed-iframe' frameborder='0' scrolling='no' style='width:100%;height:600px;' sandbox='allow-same-origin allow-forms allow-scripts allow-downloads allow-popups allow-popups-to-escape-sandbox allow-top-navigation-by-user-activation'></iframe>
</div>