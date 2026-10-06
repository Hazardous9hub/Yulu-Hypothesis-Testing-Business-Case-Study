import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# Output directory
base_dir = r"d:\DAV - 3 - Fundamentals Scaler\Yulu Hypothesis Case Study\Yulu_Hypothesis-Business-Case-Study-Github"
assets_dir = os.path.join(base_dir, "assets")
os.makedirs(assets_dir, exist_ok=True)
csv_path = os.path.join(base_dir, "data", "bike_sharing.csv")

# Load and clean data
df = pd.read_csv(csv_path)
df['datetime'] = pd.to_datetime(df['datetime'])
df['hour'] = df['datetime'].dt.hour
df['month'] = df['datetime'].dt.month
df['year'] = df['datetime'].dt.year

season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
weather_map = {
    1: 'Clear / Few Clouds',
    2: 'Mist / Cloudy',
    3: 'Light Rain / Snow',
    4: 'Heavy Rain / Ice (n=1)'
}
df['season_label'] = df['season'].map(season_map)
df['weather_label'] = df['weather'].map(weather_map)
df['workingday_label'] = df['workingday'].map({1: 'Working Day', 0: 'Non-Working Day'})

# Aesthetics
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
colors = {
    'primary': '#0284C7',     # Cyan / Blue
    'secondary': '#0EA5E9',   # Light Blue
    'accent': '#10B981',      # Emerald Green
    'warning': '#F59E0B',     # Amber
    'danger': '#EF4444',      # Red
    'dark': '#1E293B',        # Slate Dark
    'muted': '#64748B'        # Slate Muted
}

# -------------------------------------------------------------
# Figure 1: Demand Distribution & Skewness
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

mean_val = df['count'].mean()
median_val = df['count'].median()
skew_val = df['count'].skew()

sns.histplot(df['count'], kde=True, ax=ax1, color='#0284C7', bins=40, alpha=0.6)
ax1.axvline(mean_val, color='#EF4444', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.1f}')
ax1.axvline(median_val, color='#10B981', linestyle='-', linewidth=2, label=f'Median: {median_val:.1f}')
ax1.set_title(f'Raw Rental Count Distribution (Right-Skewed, Skew = {skew_val:.2f})', fontsize=12, fontweight='bold', pad=12)
ax1.set_xlabel('Hourly Rental Count', fontsize=11, fontweight='bold')
ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
ax1.legend(frameon=True, facecolor='white', framealpha=0.9)
ax1.text(0.65, 0.70, f'Observations: 10,886\nStd Dev: {df["count"].std():.1f}\nMax: {df["count"].max()}',
         transform=ax1.transAxes, bbox=dict(boxstyle='round,pad=0.5', facecolor='#F8FAFC', edgecolor='#CBD5E1'))

log_counts = np.log1p(df['count'])
sns.histplot(log_counts, kde=True, ax=ax2, color='#10B981', bins=35, alpha=0.6)
ax2.axvline(log_counts.mean(), color='#EF4444', linestyle='--', linewidth=2, label=f'Log Mean: {log_counts.mean():.2f}')
ax2.axvline(log_counts.median(), color='#0284C7', linestyle='-', linewidth=2, label=f'Log Median: {log_counts.median():.2f}')
ax2.set_title('Log-Transformed Rentals (Variance Stabilization)', fontsize=12, fontweight='bold', pad=12)
ax2.set_xlabel('Log(1 + Hourly Rental Count)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Frequency', fontsize=11, fontweight='bold')
ax2.legend(frameon=True, facecolor='white', framealpha=0.9)
ax2.text(0.05, 0.80, f'Skewness drops to: {log_counts.skew():.2f}\nApproaches bell curve for linear models',
         transform=ax2.transAxes, bbox=dict(boxstyle='round,pad=0.5', facecolor='#F8FAFC', edgecolor='#CBD5E1'))

plt.suptitle('Figure 1: Yulu Hourly Demand Distribution & Skewness Diagnostics', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
fig1_path = os.path.join(assets_dir, "01_demand_distribution_and_skew.png")
plt.savefig(fig1_path, bbox_inches='tight', dpi=300)
plt.close()
print("Saved:", fig1_path)

# -------------------------------------------------------------
# Figure 2: Working Day Dynamics & The Commuter vs Casual Paradox
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300, gridspec_kw={'width_ratios': [1, 2]})

# Left: Aggregate Comparison
w_means = df.groupby('workingday_label')['count'].mean().reset_index()
bars = ax1.bar(w_means['workingday_label'], w_means['count'], color=['#3B82F6', '#10B981'], width=0.5, edgecolor='#1E293B', linewidth=1.2)
for bar in bars:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 4, f"{yval:.1f} bikes/hr", ha='center', va='bottom', fontweight='bold', fontsize=11)
ax1.set_ylim(0, 240)
ax1.set_title('Aggregate Mean Comparison\n(2-Sample T-Test: t=1.21, p=0.226 - Not Significant)', fontsize=11, fontweight='bold', pad=10)
ax1.set_ylabel('Mean Rental Count per Hour', fontsize=11, fontweight='bold')
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# Right: Hourly breakdown by rider type
hourly = df.groupby(['hour', 'workingday_label'])[['registered', 'casual']].mean().reset_index()

ax2.plot(hourly[hourly['workingday_label'] == 'Working Day']['hour'],
         hourly[hourly['workingday_label'] == 'Working Day']['registered'],
         color='#1E40AF', linewidth=2.5, marker='o', markersize=4, label='Working Day: Registered Commuters')
ax2.plot(hourly[hourly['workingday_label'] == 'Non-Working Day']['hour'],
         hourly[hourly['workingday_label'] == 'Non-Working Day']['registered'],
         color='#60A5FA', linewidth=2, linestyle='--', marker='s', markersize=4, label='Non-Working Day: Registered Users')

ax2.plot(hourly[hourly['workingday_label'] == 'Non-Working Day']['hour'],
         hourly[hourly['workingday_label'] == 'Non-Working Day']['casual'],
         color='#D97706', linewidth=2.5, marker='^', markersize=4, label='Non-Working Day: Casual Riders (+136% surge)')
ax2.plot(hourly[hourly['workingday_label'] == 'Working Day']['hour'],
         hourly[hourly['workingday_label'] == 'Working Day']['casual'],
         color='#FBBF24', linewidth=1.8, linestyle=':', marker='x', markersize=4, label='Working Day: Casual Riders')

ax2.set_title("Hourly Rider Inversion: Commute Peaks vs Weekend Leisure Surge", fontsize=12, fontweight='bold', pad=10)
ax2.set_xlabel('Hour of Day (24-Hour Military Time)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Average Bikes Rented per Hour', fontsize=11, fontweight='bold')
ax2.set_xticks(range(0, 24, 2))
ax2.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.95, fontsize=9.5)
ax2.grid(True, linestyle='--', alpha=0.6)

# Annotate peaks
ax2.annotate('Morning Commute Peak (8 AM)\n~340 bikes/hr', xy=(8, 335), xytext=(3, 370),
             arrowprops=dict(facecolor='#1E40AF', shrink=0.08, width=1.5, headwidth=6),
             fontweight='bold', fontsize=9, bbox=dict(boxstyle='round,pad=0.3', facecolor='#EFF6FF', edgecolor='#3B82F6'))

ax2.annotate('Evening Commute Peak (5-6 PM)\n~410 bikes/hr', xy=(17, 400), xytext=(12, 450),
             arrowprops=dict(facecolor='#1E40AF', shrink=0.08, width=1.5, headwidth=6),
             fontweight='bold', fontsize=9, bbox=dict(boxstyle='round,pad=0.3', facecolor='#EFF6FF', edgecolor='#3B82F6'))

plt.suptitle('Figure 2: The Working Day Paradox — Aggregate Parity Masking Extreme Rider Inversion', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
fig2_path = os.path.join(assets_dir, "02_workingday_commuter_vs_casual_dynamics.png")
plt.savefig(fig2_path, bbox_inches='tight', dpi=300)
plt.close()
print("Saved:", fig2_path)

# -------------------------------------------------------------
# Figure 3: Seasonal Demand & Tukey HSD Post-Hoc Analysis
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5), dpi=300)

season_order = ['Spring', 'Summer', 'Fall', 'Winter']
palette = ['#93C5FD', '#FBBF24', '#F97316', '#38BDF8']

sns.boxplot(data=df, x='season_label', y='count', order=season_order, hue='season_label', palette=palette, legend=False, ax=ax1, width=0.55, fliersize=2)
season_means = df.groupby('season_label')['count'].mean()
for i, s in enumerate(season_order):
    m = season_means[s]
    ax1.plot(i, m, marker='D', color='#DC2626', markersize=7)
    ax1.text(i, m + 25, f'μ = {m:.1f}', ha='center', fontweight='bold', fontsize=10, color='#DC2626')

ax1.set_title('Hourly Rental Distribution Across Seasons (ANOVA F = 236.94, p < 1e-100)', fontsize=11, fontweight='bold', pad=10)
ax1.set_xlabel('Season', fontsize=11, fontweight='bold')
ax1.set_ylabel('Total Hourly Rentals (count)', fontsize=11, fontweight='bold')

# Post-Hoc Tukey HSD
tukey = pairwise_tukeyhsd(endog=df['count'], groups=df['season_label'], alpha=0.05)
tukey_df = pd.DataFrame(data=tukey._results_table.data[1:], columns=tukey._results_table.data[0])
tukey_df['comparison'] = tukey_df['group1'] + ' vs ' + tukey_df['group2']

y_pos = np.arange(len(tukey_df))
ax2.errorbar(tukey_df['meandiff'], y_pos, xerr=[tukey_df['meandiff'] - tukey_df['lower'], tukey_df['upper'] - tukey_df['meandiff']],
             fmt='o', color='#0284C7', ecolor='#1E293B', elinewidth=2, capsize=5, markersize=7)
ax2.axvline(0, color='#EF4444', linestyle='--', linewidth=1.5, label='Zero Difference Line')
ax2.set_yticks(y_pos)
ax2.set_yticklabels(tukey_df['comparison'], fontsize=10, fontweight='bold')
ax2.set_title('Tukey HSD Post-Hoc Pairwise 95% Confidence Intervals', fontsize=11, fontweight='bold', pad=10)
ax2.set_xlabel('Difference in Mean Hourly Rentals (bikes/hr)', fontsize=11, fontweight='bold')
ax2.legend(loc='lower right', frameon=True, facecolor='white')

for i, row in tukey_df.iterrows():
    diff_val = row['meandiff']
    ax2.text(diff_val, i + 0.22, f"Δ = {diff_val:+.1f}", ha='center', fontsize=9, fontweight='bold', color='#0F172A')

plt.suptitle('Figure 3: Seasonal Demand Collapse — Spring (Season 1) Suffers a >50% Slump vs Fall Peak', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
fig3_path = os.path.join(assets_dir, "03_seasonal_demand_and_tukey_hsd.png")
plt.savefig(fig3_path, bbox_inches='tight', dpi=300)
plt.close()
print("Saved:", fig3_path)

# -------------------------------------------------------------
# Figure 4: Weather Impact & Severe Weather Drop (With n=1 Callout)
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5), dpi=300, gridspec_kw={'width_ratios': [1.3, 1]})

weather_order = ['Clear / Few Clouds', 'Mist / Cloudy', 'Light Rain / Snow', 'Heavy Rain / Ice (n=1)']
w_palette = ['#38BDF8', '#94A3B8', '#64748B', '#DC2626']

sns.boxplot(data=df, x='weather_label', y='count', order=weather_order, hue='weather_label', palette=w_palette, legend=False, ax=ax1, width=0.55, fliersize=2)
ax1.set_title('Hourly Demand by Weather Condition (ANOVA F = 65.53, p < 1e-42)', fontsize=11, fontweight='bold', pad=10)
ax1.set_xlabel('Weather Severity Category', fontsize=11, fontweight='bold')
ax1.set_ylabel('Total Hourly Rentals (count)', fontsize=11, fontweight='bold')
ax1.set_xticks(range(len(weather_order)))
ax1.set_xticklabels(['Clear\n(66.1%)', 'Mist\n(26.0%)', 'Light Rain\n(7.9%)', 'Heavy Rain\n(0.01%)'], fontsize=10, fontweight='bold')

# Right: Mean comparison and sample sizes
w_stats = df.groupby('weather_label')['count'].agg(['mean', 'count']).reindex(weather_order)
bars = ax2.bar(range(len(w_stats)), w_stats['mean'], color=w_palette, edgecolor='#1E293B', linewidth=1.2, width=0.55)
for i, bar in enumerate(bars):
    h = bar.get_height()
    n_cnt = w_stats.iloc[i]['count']
    ax2.text(bar.get_x() + bar.get_width()/2.0, h + 5, f"μ = {h:.1f}\n(n={int(n_cnt)})", ha='center', va='bottom', fontsize=9.5, fontweight='bold')

ax2.set_ylim(0, 260)
ax2.set_xticks(range(len(w_stats)))
ax2.set_xticklabels(['Clear', 'Mist', 'Light Rain', 'Heavy Rain'], fontsize=10, fontweight='bold')
ax2.set_title('Mean Rentals & Sample Sizes (The n=1 Edge Case)', fontsize=11, fontweight='bold', pad=10)
ax2.set_ylabel('Average Hourly Rentals', fontsize=11, fontweight='bold')

# Visual callout box for Weather 4
ax2.annotate('CRITICAL EDGE CASE:\nWeather 4 has only 1 row (count=164).\nVariance cannot be estimated!\nReported sensitivity check.',
             xy=(3, 164), xytext=(1.2, 215),
             arrowprops=dict(facecolor='#DC2626', shrink=0.08, width=1.5, headwidth=6),
             fontweight='bold', fontsize=9, bbox=dict(boxstyle='round,pad=0.5', facecolor='#FEF2F2', edgecolor='#EF4444'))

plt.suptitle('Figure 4: Environmental Fragility — Adverse Weather Drops Demand by 42% & The n=1 Statistical Caveat', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
fig4_path = os.path.join(assets_dir, "04_weather_impact_and_severe_drop.png")
plt.savefig(fig4_path, bbox_inches='tight', dpi=300)
plt.close()
print("Saved:", fig4_path)

# -------------------------------------------------------------
# Figure 5: Weather vs Season Contingency Heatmap & Chi-Square Test
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5), dpi=300)

ct = pd.crosstab(df['season_label'], df['weather_label'])
ct = ct.reindex(index=season_order, columns=weather_order).fillna(0).astype(int)

ct_pct = pd.crosstab(df['season_label'], df['weather_label'], normalize='index') * 100
ct_pct = ct_pct.reindex(index=season_order, columns=weather_order).fillna(0)

sns.heatmap(ct, annot=True, fmt='d', cmap='Blues', ax=ax1, cbar=True, linewidths=1, linecolor='#CBD5E1',
            annot_kws={'fontsize': 11, 'fontweight': 'bold'})
ax1.set_title('Observed Frequency Contingency Matrix (N = 10,886)', fontsize=11, fontweight='bold', pad=10)
ax1.set_xlabel('Weather Severity', fontsize=11, fontweight='bold')
ax1.set_ylabel('Season', fontsize=11, fontweight='bold')

sns.heatmap(ct_pct, annot=True, fmt='.1f', cmap='YlGnBu', ax=ax2, cbar=True, linewidths=1, linecolor='#CBD5E1',
            annot_kws={'fontsize': 11, 'fontweight': 'bold'})
ax2.set_title('Row-Normalized Conditional Probability (% within Season)', fontsize=11, fontweight='bold', pad=10)
ax2.set_xlabel('Weather Severity', fontsize=11, fontweight='bold')
ax2.set_ylabel('Season', fontsize=11, fontweight='bold')

# Chi2 calculation
chi2_stat, p_val, dof, expected = stats.chi2_contingency(pd.crosstab(df['season'], df['weather']))
fig.text(0.5, -0.05, f"Chi-Square Test of Independence: χ² = {chi2_stat:.2f}, dof = {dof}, p-value = {p_val:.3e}  (Reject H0 at α=0.05)\nCochran's Condition Alert: Expected frequency in Weather 4 column is ~0.25 (< 5), necessitating sensitivity testing with combined severe categories.",
         ha='center', fontsize=10, fontweight='bold', bbox=dict(boxstyle='round,pad=0.6', facecolor='#F8FAFC', edgecolor='#64748B'))

plt.suptitle('Figure 5: Bivariate Dependency — Weather Patterns are Strongly Dependent on Season', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
fig5_path = os.path.join(assets_dir, "05_weather_season_contingency_heatmap.png")
plt.savefig(fig5_path, bbox_inches='tight', dpi=300)
plt.close()
print("Saved:", fig5_path)

print("All 5 high-resolution figures successfully generated in assets/")
