# 📊 Dataset Documentation: Yulu Bike Sharing Dataset

## 📁 Source & Context
The dataset contains hourly rental logs for Yulu electric bikes and shared bicycles. It spans 10,886 hourly records across two years, capturing customer rental volumes alongside environmental, seasonal, and calendar indicators.

- **File Name:** `bike_sharing.csv`
- **Total Records:** 10,886 rows
- **Total Attributes:** 12 columns
- **Missing Values:** 0 null values across all columns

---

## 📋 Data Dictionary & Column Profiling

| Column Name | Data Type | Description | Values / Range | Business Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| `datetime` | String (Timestamp) | Hourly date and timestamp | `2011-01-01 00:00:00` to `2012-12-19 23:00:00` | Temporal tracking of rental trends. |
| `season` | Integer (Categorical) | Four operational seasons | `1`: Spring<br>`2`: Summer<br>`3`: Fall<br>`4`: Winter | Macro weather cycles affecting customer commuting behavior. |
| `holiday` | Integer (Binary) | Official public holiday indicator | `0`: Non-holiday<br>`1`: Public holiday | Identifies state and national non-working holidays. |
| `workingday` | Integer (Binary) | Working day indicator | `0`: Weekend or holiday<br>`1`: Regular weekday | Separates commuter-driven days from leisure-driven days. |
| `weather` | Integer (Categorical) | Weather severity classification | `1`: Clear, few clouds<br>`2`: Mist and cloudy<br>`3`: Light snow, light rain<br>`4`: Heavy rain, ice pellets (Severe) | Environmental condition during the rental hour. |
| `temp` | Float | Actual ambient temperature | `0.82°C` to `41.0°C` | Direct thermal condition in Celsius. |
| `atemp` | Float | "Feels-like" temperature | `0.76°C` to `45.455°C` | Subjective thermal comfort in Celsius. |
| `humidity` | Integer | Relative humidity percentage | `0%` to `100%` | Moisture level in air. |
| `windspeed` | Float | Wind speed | `0.0` to `56.99` km/h | Atmospheric wind velocity. |
| `casual` | Integer | Count of non-registered riders | `0` to `367` rentals | Pay-per-ride users and leisure cyclists. |
| `registered`| Integer | Count of registered riders | `0` to `886` rentals | Daily commuters and subscription holders. |
| `count` | Integer | Total rental bike count | `1` to `977` rentals | Target variable (`count = casual + registered`). |

---

## 🔍 Critical Data Sanity Notes & Edge Cases

1. **Target Additivity:**
   - Formula: `count = casual + registered`
   - Verified across all 10,886 rows with zero discrepancies.
2. **Right-Skewed Target Distribution:**
   - Mean: **191.57** rentals/hour
   - Median: **145.00** rentals/hour
   - Maximum: **977** rentals/hour
   - Standard deviation: **181.14**
3. **Severe Weather Imbalance (Weather 4):**
   - Weather 1 (Clear): **7,192** records (66.07%)
   - Weather 2 (Mist): **2,834** records (26.03%)
   - Weather 3 (Light Rain/Snow): **859** records (7.89%)
   - Weather 4 (Heavy Rain/Ice): **1 record only** (0.01%)
   - *Statistical Impact:* Variance cannot be calculated for a sample size of $n=1$. This requires special handling during ANOVA and Chi-Square tests.
4. **Multicollinearity:**
   - `temp` and `atemp` exhibit a Pearson correlation of $r = 0.985$, indicating redundant temperature tracking.
