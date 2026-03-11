import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

df = pd.read_csv('college_data.csv')
df = df[(df['PREDDEG'] == 3) & (df['CONTROL'].isin([1, 2]))].copy()
df = df[df['MD_EARN_WNE_P10'] != 'PrivacySuppressed']
df['MD_EARN_WNE_P10'] = pd.to_numeric(df['MD_EARN_WNE_P10'], errors='coerce')
df['GRAD_DEBT_MDN']   = pd.to_numeric(df['GRAD_DEBT_MDN'],   errors='coerce')
df['NPT4_PUB']        = pd.to_numeric(df['NPT4_PUB'],        errors='coerce')
df['NPT4_PRIV']       = pd.to_numeric(df['NPT4_PRIV'],       errors='coerce')
df['UGDS']            = pd.to_numeric(df['UGDS'],            errors='coerce')
df = df.dropna(subset=['COSTT4_A', 'MD_EARN_WNE_P10', 'C150_4'])

df['tuition']     = df['COSTT4_A']
df['earnings']    = df['MD_EARN_WNE_P10']
df['grad_rate']   = df['C150_4']
df['debt']        = df['GRAD_DEBT_MDN']
df['school_type'] = df['CONTROL'].map({1: 'Public', 2: 'Private Non-Profit'})
df['net_price']   = np.where(df['CONTROL'] == 1, df['NPT4_PUB'], df['NPT4_PRIV'])

print(f"분석 대상: {len(df):,}개 학교 (공립 {(df['CONTROL']==1).sum()}, 사립비영리 {(df['CONTROL']==2).sum()})")

colors = {'Public': '#1877F2', 'Private Non-Profit': '#E07B54'}
x_line = np.linspace(df['tuition'].min(), df['tuition'].max(), 100)

# ── Fig 1: 단순 상관관계 ──
fig, ax = plt.subplots(figsize=(10, 6))
for stype, color in colors.items():
    sub = df[df['school_type'] == stype]
    ax.scatter(sub['tuition']/1000, sub['earnings']/1000, alpha=0.4, s=25, color=color, label=stype)
z = np.polyfit(df['tuition'], df['earnings'], 1)
ax.plot(x_line/1000, np.poly1d(z)(x_line)/1000, color='gray', linewidth=2, linestyle='--', label='Trend line')
corr = df['tuition'].corr(df['earnings'])
ax.text(0.05, 0.92, f'Correlation: r = {corr:.2f}', transform=ax.transAxes, fontsize=11,
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
ax.set_xlabel('Annual Tuition Cost ($K)', fontsize=12)
ax.set_ylabel('Median Earnings 10yr After Enrollment ($K)', fontsize=12)
ax.set_title('Layer 1: Does Higher Tuition = Higher Earnings?\n(Simple Correlation — n=1,601)', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('figures/fig1_tuition_vs_earnings.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Fig 1 saved")

# ── Fig 2: 공립 vs 사립 ──
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Layer 2: Does School Type Change the Story?\n(Public vs Private Non-Profit)', fontsize=13, fontweight='bold')
for ax, (col, ylabel, title, scale, mult) in zip(axes, [
    ('tuition',   'Annual Tuition ($K)',       'Tuition Cost',   1000, 1),
    ('earnings',  'Median Earnings 10yr ($K)', 'Earnings',       1000, 1),
    ('grad_rate', 'Graduation Rate (%)',        'Grad Rate',         1, 100),
]):
    data_pub  = df[df['school_type']=='Public'][col].dropna()
    data_priv = df[df['school_type']=='Private Non-Profit'][col].dropna()
    bp = ax.boxplot([data_pub/scale*mult, data_priv/scale*mult], patch_artist=True, widths=0.5,
                    medianprops=dict(color='black', linewidth=2))
    bp['boxes'][0].set_facecolor('#1877F2'); bp['boxes'][0].set_alpha(0.7)
    bp['boxes'][1].set_facecolor('#E07B54'); bp['boxes'][1].set_alpha(0.7)
    med_pub  = data_pub.median()/scale*mult
    med_priv = data_priv.median()/scale*mult
    suffix = '%' if col == 'grad_rate' else 'K'
    ax.text(1, med_pub,  f'  {med_pub:.0f}{suffix}', va='center', fontsize=9, fontweight='bold', color='#1877F2')
    ax.text(2, med_priv, f'  {med_priv:.0f}{suffix}', va='center', fontsize=9, fontweight='bold', color='#E07B54')
    ax.set_xticks([1,2]); ax.set_xticklabels(['Public','Private\nNon-Profit'], fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10); ax.set_title(title, fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('figures/fig2_public_vs_private.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Fig 2 saved")

# ── Fig 3: 스티커 vs 실질 학비 ──
df_net = df.dropna(subset=['net_price'])
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle('Layer 3: Sticker Price vs Net Price — Are Expensive Schools Really That Expensive?', fontsize=13, fontweight='bold')
for ax, stype, color in zip(axes, ['Public','Private Non-Profit'], ['#1877F2','#E07B54']):
    sub = df_net[df_net['school_type']==stype]
    ax.scatter(sub['tuition']/1000, sub['net_price']/1000, alpha=0.5, s=30, color=color)
    ax.plot([0,90],[0,90],'k--',linewidth=1.5,alpha=0.5,label='No aid (sticker=net)')
    discount = ((sub['tuition']-sub['net_price'])/sub['tuition']*100).median()
    ax.text(0.05,0.92,f'Median discount: {discount:.0f}%',transform=ax.transAxes,fontsize=10,
            bbox=dict(boxstyle='round',facecolor='lightyellow',alpha=0.8))
    ax.set_xlabel('Sticker Price ($K)',fontsize=11); ax.set_ylabel('Net Price After Aid ($K)',fontsize=11)
    ax.set_title(stype,fontsize=12,fontweight='bold'); ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('figures/fig3_sticker_vs_net_price.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Fig 3 saved")

# ── Fig 4: 졸업률 통제 전후 ──
df_high = df[df['grad_rate'] >= 0.5]
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle('Layer 4: What Happens When We Control for Graduation Rate?', fontsize=13, fontweight='bold')
for ax, data, label in zip(axes, [df, df_high], ['All Schools', 'Grad Rate ≥ 50%']):
    for stype, color in colors.items():
        sub = data[data['school_type']==stype]
        ax.scatter(sub['tuition']/1000, sub['earnings']/1000, alpha=0.35, s=20, color=color, label=stype)
    z2 = np.polyfit(data['tuition'], data['earnings'], 1)
    ax.plot(x_line/1000, np.poly1d(z2)(x_line)/1000, 'gray', linewidth=2, linestyle='--')
    r = data['tuition'].corr(data['earnings'])
    ax.text(0.05,0.92,f'r = {r:.2f} (n={len(data):,})',transform=ax.transAxes,fontsize=10,
            bbox=dict(boxstyle='round',facecolor='lightyellow',alpha=0.8))
    ax.set_title(label,fontsize=11,fontweight='bold')
    ax.set_xlabel('Tuition ($K)'); ax.set_ylabel('Earnings ($K)'); ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('figures/fig4_grad_rate_effect.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Fig 4 saved")

# ── Fig 5: 최종 요약 ──
fig, ax = plt.subplots(figsize=(9, 5))
variables = {
    'Tuition\n(Sticker Price)':  df['tuition'].corr(df['earnings']),
    'Net Price\n(After Aid)':    df_net['net_price'].corr(df_net['earnings']),
    'Graduation Rate':           df['grad_rate'].corr(df['earnings']),
    'School Size':               df['UGDS'].corr(df['earnings']),
}
labels = list(variables.keys())
values = list(variables.values())
bar_colors = ['#E07B54' if v == max(values) else '#B0BEC5' for v in values]
bars = ax.barh(labels, values, color=bar_colors, edgecolor='white', height=0.5)
for bar, val in zip(bars, values):
    ax.text(val+0.005, bar.get_y()+bar.get_height()/2, f'{val:.2f}', va='center', fontsize=11, fontweight='bold')
ax.set_xlabel('Correlation with Earnings (r)', fontsize=11)
ax.set_title('Layer 5: Which Variable Best Predicts Earnings?\n(Correlation with Median Earnings 10yr After Enrollment)',
             fontsize=12, fontweight='bold')
ax.axvline(x=0, color='black', linewidth=0.8)
ax.set_xlim(-0.15, max(values)*1.35)
ax.legend(handles=[mpatches.Patch(color='#E07B54', label='Strongest predictor')], fontsize=10)
plt.tight_layout()
plt.savefig('figures/fig5_summary.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Fig 5 saved")

print(f"\n{'='*55}")
print(f"ANALYSIS SUMMARY")
print(f"{'='*55}")
print(f"Total schools: {len(df):,} (Public: {(df['school_type']=='Public').sum()}, Private NP: {(df['school_type']=='Private Non-Profit').sum()})")
print(f"Tuition:       ${df['tuition'].min()/1000:.0f}K ~ ${df['tuition'].max()/1000:.0f}K")
print(f"Earnings:      ${df['earnings'].min()/1000:.0f}K ~ ${df['earnings'].max()/1000:.0f}K")
print(f"r(tuition, earnings):   {df['tuition'].corr(df['earnings']):.2f}")
print(f"r(grad_rate, earnings): {df['grad_rate'].corr(df['earnings']):.2f}")
print(f"r(net_price, earnings): {df_net['net_price'].corr(df_net['earnings']):.2f}")
print(f"{'='*55}")
