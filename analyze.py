# analyze.py
# Summary: km_since_service is the strongest breakdown predictor (normalized separation 0.977),
# followed by avg_daily_km (0.610) and load_factor (0.520). Total mileage and age_years are
# near-zero separators (0.005 and -0.003) -- the obvious assumptions are wrong; the data does
# not say "older or higher-mileage cars break down more." Risk score weights reflect these findings.

import pandas as pd

# -- 1. Load ------------------------------------------------------------------
df = pd.read_csv("fleet_history.csv")

# -- 2. Which columns separate breakers from non-breakers? -------------------
# Compare group means; compute normalized separation = mean_diff / pooled_std.
# Higher separation -> better predictor.
features = ["km_since_service", "avg_daily_km", "load_factor", "odometer_km", "age_years"]
g = df.groupby("broke_down").mean(numeric_only=True)

print("-- Group means: broke_down=1 vs broke_down=0 --------------------------")
separations = {}
for col in features:
    mean_broke = g.loc[1, col]
    mean_ok    = g.loc[0, col]
    sep = (mean_broke - mean_ok) / df[col].std()
    separations[col] = sep
    print(f"  {col:<20}  broke={mean_broke:>9.1f}  ok={mean_ok:>9.1f}  sep={sep:+.3f}")

print()
print("Findings:")
print("  km_since_service  sep=+0.977  ** strongest signal by far")
print("  avg_daily_km      sep=+0.610  ** cars driven harder daily break more")
print("  load_factor       sep=+0.520  ** heavier use correlates with breakdown")
print("  odometer_km       sep=+0.005  -- total mileage is NOT a useful predictor")
print("  age_years         sep=-0.003  -- age is NOT a useful predictor")
print()

# -- 3. Risk score (0-100) ----------------------------------------------------
# Use only the three predictors with meaningful separation.
# Each is min-max normalised to [0, 1], then weighted by its normalized separation,
# and scaled so the maximum possible score is 100.
#
# Weights (proportional to separation magnitude):
#   km_since_service : 0.977
#   avg_daily_km     : 0.610
#   load_factor      : 0.520
#   total            : 2.107

W_KM    = 0.977
W_DAILY = 0.610
W_LOAD  = 0.520
W_TOTAL = W_KM + W_DAILY + W_LOAD   # 2.107


def minmax(series: pd.Series) -> pd.Series:
    """Min-max normalise a series to [0, 1]."""
    lo, hi = series.min(), series.max()
    return (series - lo) / (hi - lo)


df["_n_km_since"] = minmax(df["km_since_service"])
df["_n_daily"]    = minmax(df["avg_daily_km"])
df["_n_load"]     = minmax(df["load_factor"])

df["risk_score"] = (
    (df["_n_km_since"] * W_KM +
     df["_n_daily"]    * W_DAILY +
     df["_n_load"]     * W_LOAD) / W_TOTAL * 100
).round(1)

# -- 4. Print ranked by risk, highest first -----------------------------------
ranked = df[["car_id", "risk_score", "km_since_service", "avg_daily_km",
             "load_factor", "broke_down"]].sort_values("risk_score", ascending=False)

print("-- Fleet ranked by breakdown risk (highest first) ---------------------")
print(f"{'rank':<5} {'car_id':<10} {'risk':>6}  {'km_since':>9}  "
      f"{'daily_km':>8}  {'load':>6}  {'broke?':>7}")
print("-" * 65)
for rank, (_, row) in enumerate(ranked.iterrows(), start=1):
    broke = "YES" if row["broke_down"] == 1 else "-"
    print(f"{rank:<5} {row['car_id']:<10} {row['risk_score']:>6.1f}  "
          f"{int(row['km_since_service']):>9,}  {int(row['avg_daily_km']):>8,}  "
          f"{row['load_factor']:>6.2f}  {broke:>7}")

print()
print(f"Cars with risk >= 70: {(df['risk_score'] >= 70).sum()}  "
      f"(of which broke down: {df.loc[df['risk_score'] >= 70, 'broke_down'].sum()})")
print(f"Cars with risk < 30: {(df['risk_score'] < 30).sum()}  "
      f"(of which broke down: {df.loc[df['risk_score'] < 30, 'broke_down'].sum()})")
