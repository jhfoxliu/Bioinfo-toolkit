__all__ = ["sjm_tools"]

__name__ = "sjm_tools"

__doc__ = """
A module for quick deploy SJM submission.

Tutorial:

#import
from sjm_tools.sjm_tools import job

class job:
JOB = job(workpath,SJM) #workpath = which directory the files will in; SJM = SJM file name

Add job cycles:
JOB.step_start(step_name="QC")
JOB.add_process([Your cmd, string])
JOB.step_end()

When finished:
JOB.job_finish()

Submit:
JOB.submit()

Delay a step:
JOB.delay(time=[how long?]) #e.g. 10s 100min 1h 1hr

"""

__version__ = "0.0.1"

__author__ = "Jianheng Liu"

__time__ = "20180709"