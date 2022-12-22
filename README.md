# cycling-stats - Calculate advanced cycling statistics from power and/or heart rate data

Calculate statistics such as time spent in individualized heart rate and power zones, normalized power, intensity factor, training stress score, variability index, efficiency factor, chronic training load, acute training load and training stress balance, from heart rate and power meters.

## Installation
The package is available under pypi:
```
pip install cycling-stats
```

## Usage
You can use the package as follows. A simple example: you can import the function `training_stress_score` as follows.
```python
from cyclingstats.stats import training_stress_score
```

The package requires that you have your data in a `pandas.DataFrame`. The following example illustrates when you have a time series from multiple separate training sessions, and you wish to calculate statistics separately for each day of cycling.

```python
import pandas as pd
from cyclingstats.stats import calc_hr_zones, calc_power_zones, agg_zones, agg_power 
from cyclingstats.stats import chronic_training_load, acute_training_load, training_stress_balance

# read time series of power and/or heart rate
df = pd.read_csv("PATH_TO_YOUR_HEARTRATE_AND_POWER_DATA")
df['date'] = pd.to_datetime(df['timestamp'].dt.date)
# perform any other preprocessing steps here

# ---------- zones
# define LTHR and FTP to calculate custom Coggan heart rate and power zones
LTHR = # TODO: fill in a number for the lactate threshold heart rate [bpm]
FTP = # TODO: fill in a number for the functional threshold power [W]

hr_zones = calc_hr_zones(LTHR)
power_zones = calc_power_zones(FTP)

# calculate hr and power zones
df_zones = df.groupby('date').apply(agg_zones, hr_zones=hr_zones, power_zones=power_zones)

# ---------- power
df = df.set_index('timestamp')

# calculate power statistics
df_power = df.groupby('date').apply(agg_power, FTP=FTP

# fill up dates for which we don't have an entry to get exponential weighted mean (ewm)
dates = df_power.index
df_power = df_power.reindex(date_range)

# calculate ctl, atl and tsb
df_power['chronic_training_load'] = chronic_training_load(df_power['training_stress_score'])
df_power['acute_training_load'] = acute_training_load(df_power['training_stress_score'])
df_power['training_stress_balance'] = training_stress_balance(df_power['chronic_training_load'], df_power['acute_training_load'])

# get back to indices for which there is a training session
df_power = df_power.loc[dates]
```

If you are running into problems, feel welcome to contact the author (evanweenen@ethz.ch).

## License
This code is &copy; E. van Weenen, 2022, and it is made available under the MIT license enclosed with the software.

Over and above the legal restrictions imposed by this license, if you use this software for an academic publication then you are obliged to provide proper attribution. 
```
E. van Weenen. cycling-stats: Calculate advanced cycling statistics from power and/or heart rate data, v0.1 (2022). github.com/evavanweenen/cycling-stats.
```