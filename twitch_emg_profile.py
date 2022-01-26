import neo
import numpy as np

filepath = '/Users/stuartbman/Google Drive/us_emg_shared/recordings- 2021.05.13/142427_000.smrx'
reader = neo.io.Spike2IO(filename=filepath)


data = reader.read(lazy=False)[0]

import sonpy.lib