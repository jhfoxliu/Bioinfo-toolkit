# SJM tools

**SJM (Simple Job Manager)** <https://github.com/StanfordBioinformatics/SJM> is a pretty wrapper for SGE in task management. But it's not elegant to repeat writing SJM files when handling huge number of tasks.
This module is a wrapper for SJM, involing a class ``sjm_tools``, which can support you quickly generate and upload SJM files with syntax check. 

Installation
==========================================================================================================
``pip install <path to sjm_tools>``


Usage
==========================================================================================================
To import the module:
::
  import sjm_tools
::

Check if your paths are right:
::
  from sjm_tools import check_env 
  fasta_file = check_env(<PATH_TO_A_FILE>)
  bowtie2_dir = check_env(<PATH_TO_DIRECTORY>,is_path=True)
  bowtie2_index = check_env(<PATH_TO_FILE_PREFIX>,is_prefix=True)
  unknow_item = check_env(<PATH_TO_UNKOWN>,unknown=True)
::

Basic structure:
::
  Create job 
  
  Create step 1
  Add prefix 1
  Add process 1-1
  Add process 1-2
  ...
  Add suffix 1
  
  Add step 2
  Add preifx 2
  Add process 2-1
  Add process 2-2
  ...
  Add suffix 2
  
  ...
  
  Finsihed
  Submit (optional)
::


Codes:
::
  from sjm_tools import job

  # add a new job
  JOB = job(workpath=workpath,SJM=<SJM file>,SJM_path=<PATH_TO_SJM>)
  
  # add a step
  JOB.step_start(step_name=step_name,directory=<WORK_DIRECTORY>) #If no directory specified, use current directory
  
  # add SJM prefix, required
  JOB.add_prefix()
 
  # add a SJM process
  JOB.add_process("cat {something}".format(cmd=<Your CMD>)) # <- put your CMD here
 
  # add a SJM suffix
  JOB.add_end()
  
  # repeat prefix-process-suffix to append process cycles.
  
  # all finished, this will generate a sjm file.
  JOB.job_finish()
  
  # if you want to submit the file
  JOB.submit()
::
