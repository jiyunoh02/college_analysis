# 📊 Does Paying More for College Lead to Higher Earnings?
### U.S. College ROI Analysis — College Scorecard Data (2025)

---

## Project Overview

This project analyzes whether tuition cost predicts earnings after graduation — and shows how the answer changes completely depending on how you process the data.

- **Data Source:** U.S. Department of Education — College Scorecard (2025)
- **Schools analyzed:** 1,601 four-year colleges (Public & Private Non-Profit)
- **Tools:** Python (pandas, numpy, matplotlib, seaborn)

---

## The Question

> **Does paying more for college lead to higher earnings after graduation?**

At first glance, the answer seems obvious. But the conclusion changes at every step of data processing. This project documents that journey across 5 layers of analysis.

---

## Step 1: Column Selection

The raw College Scorecard dataset contains **3,000+ columns**. I narrowed it down to 11 based on what would meaningfully capture the relationship between cost and outcome.

| Column | What It Measures | Why I Included It |
|---|---|---|
| `INSTNM` | School name | Identifier |
| `CONTROL` | Public / Private / For-profit | To split school types |
| `PREDDEG` | Predominant degree granted | To isolate 4-year schools |
| `COSTT4_A` | Annual sticker price (tuition) | Main cost variable |
| `NPT4_PUB` / `NPT4_PRIV` | Net price after financial aid | Real cost after aid |
| `MD_EARN_WNE_P10` | Median earnings 10yr after enrollment | Main outcome variable |
| `GRAD_DEBT_MDN` | Median debt at graduation | Financial burden |
| `C150_4` | 6-year graduation rate | Completion rate |
| `UGDS` | Undergraduate enrollment size | School scale |
| `STABBR` | State | Geographic context |

I chose **earnings 10 years after enrollment** (not 6 years) because it better reflects settled career income rather than entry-level salaries.

---

## Step 2: Data Cleaning Decisions

### 2-1. Keeping Only 4-Year Schools
```python
df = df[df['PREDDEG'] == 3]
```
`PREDDEG == 3` means the school predominantly grants bachelor's degrees. I excluded community colleges (2-year) and certificate programs because they serve different purposes and comparing them to 4-year universities would distort the analysis.

### 2-2. Removing For-Profit Schools
```python
df = df[df['CONTROL'].isin([1, 2])]
# 1 = Public, 2 = Private Non-Profit, 3 = For-Profit (excluded)
```
For-profit schools (e.g. University of Phoenix) have fundamentally different cost structures, student populations, and outcomes. Including them would conflate two separate markets. I kept only Public and Private Non-Profit institutions, which are the schools most students consider when making college decisions.

### 2-3. Removing 'PrivacySuppressed' Values
```python
df = df[df['MD_EARN_WNE_P10'] != 'PrivacySuppressed']
```
The Department of Education masks earnings data for schools where the sample size is too small to report without identifying individuals. These aren't missing by chance — they're structurally absent. Treating them as NaN and imputing would introduce bias, so I dropped them entirely.

### 2-4. Net Price: Two Separate Columns
```python
df['net_price'] = np.where(df['CONTROL'] == 1, df['NPT4_PUB'], df['NPT4_PRIV'])
```
The dataset stores net price in two separate columns depending on school type. I merged them into one `net_price` column for analysis. This is not a standard merge — it required understanding what each column actually represents.

**After all cleaning steps:**
```
Raw:     6,429 schools
→ 4-year only:           1,983
→ Public/Private NP:     1,827
→ Remove missing/masked: 1,601 ✓
```

---

## Step 3: Visualizations — Design Choices

### Fig 1 — Scatter Plot (Tuition vs Earnings)
I chose a scatter plot to show the **distribution** of schools, not just averages. A bar chart would have hidden how much variance exists at every tuition level. Color-coded by school type to layer in a second variable without adding a separate chart.

![](figures/fig1_tuition_vs_earnings.png)

### Fig 2 — Box Plot (Public vs Private)
Box plots were more appropriate than bar charts here because the goal was to show the **spread and median** simultaneously. Bar charts showing only the mean would have been misleading given how skewed tuition distributions are.

![](figures/fig2_public_vs_private.png)

### Fig 3 — Scatter Plot (Sticker vs Net Price)
I added a diagonal reference line (where sticker = net price = no aid) so the reader can immediately see the **distance** between what schools advertise and what students actually pay. This makes the discount visible at a glance.

![](figures/fig3_sticker_vs_net_price.png)

### Fig 4 — Before/After Comparison
Instead of just showing the filtered result, I placed the before and after side by side so the impact of controlling for graduation rate is directly visible. The correlation coefficient is annotated on both panels for easy comparison.

![](figures/fig4_grad_rate_effect.png)

### Fig 5 — Horizontal Bar Chart (Variable Comparison)
I chose a horizontal bar chart to rank predictors clearly. The strongest predictor is highlighted in a distinct color so the key finding is visible in under 3 seconds.

![](figures/fig5_summary.png)

---

## Key Findings

| Layer | Finding |
|---|---|
| 1. Simple correlation | Tuition vs earnings: **r = 0.52** |
| 2. School type split | Public schools show better ROI per dollar spent |
| 3. Sticker vs net price | Private schools discount ~40% on average — sticker price is misleading |
| 4. Graduation rate control | Low-graduation schools distort earnings data downward |
| 5. Best predictor | **Graduation rate (r = 0.63)** outperforms tuition as an earnings predictor |

> The variable that best predicts earnings is not tuition — it's graduation rate.  
> Schools that get students across the finish line produce higher earners, regardless of price.

---

## Reflection

This project highlighted that data cleaning decisions are not neutral — every choice about what to include or exclude changes the conclusion. Removing for-profit schools, handling PrivacySuppressed values, and choosing net price over sticker price each shifted the results meaningfully. The most important skill wasn't writing the visualization code — it was deciding what the data should look like before any code was written.

