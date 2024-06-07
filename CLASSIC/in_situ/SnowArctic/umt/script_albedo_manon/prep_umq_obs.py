import pandas as pd
import xarray as xr
import numpy as np
import datetime as dt
import pdb
from prep_obs import prep_obs

# Albedo

df = pd.read_csv(r'/home/mag009/crocus/Simulation/run_all_new/obs_eval/umq/Umiujaq_rad_tundra.tab', sep = '\t', engine='python', header=23)

# Create time index
df.index = pd.DatetimeIndex(df['Date/Time'])
df.index.rename('time', inplace=True)

# Remove unnecessary variables
df = df.drop(columns=['Date/Time','LWD [W/m**2]','LWU [W/m**2]','QF LWD','QF LWU'])
df.columns = ['GLOB','QFG','REFL','QFR']
df['GLOB'] = df.GLOB[df.QFG==0]
df['REFL'] = df.REFL[df.QFR==0]
df.drop(columns=['QFG','QFR'], inplace=True)

# Convert the dataframe into a dataset
ds = df.to_xarray()


df = pd.read_csv(r'/home/mag009/crocus/Simulation/run_all_new/obs_eval/umq/Umiujaq_snow_height.tab', sep = '\t', engine='python', header=19)
df = df[df['Event']=='Umiujaq_2012-2021_Tundra']

# Create time index
df.index = pd.DatetimeIndex(df['Date/Time'])
df.index.rename('time', inplace=True)

# Remove unnecessary variables
df = df.drop(columns=['Date/Time','Event','Vegetation type'])
df.columns = ['snd_man']

# Convert the dataframe into a dataset
ds2 = df.to_xarray()

# Add one dataset to the other
ds['snd_man'] = ds2.snd_man
ds2.close()
ds = ds.astype('float32')
ds = ds.loc[dict(time=slice('2012-09-02','2020-09-01'))]

prep_obs(ds, 'umq')