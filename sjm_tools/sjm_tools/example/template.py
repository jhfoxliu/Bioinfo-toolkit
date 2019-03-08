#!/usr/bin/env python
import sys,os
from sjm_tools import job,check_env

# just an example

#SJM = sys.argv[1]
#SJM = test.sjm

#metadata
#check environment
genome_index = check_env('/share/public1/data/liujh/database/zebrafish/rRNA/Danio_rerio.GRCz11.rRNA.19bp.fa')
sortmerna_db = check_env('/share/public1/data/liujh/database/zebrafish/rRNA/sortmerna_db/',is_path=True)
genome_index = check_env('/share/public6/data/huangt/database/zebrafish/metadata/Danio_rerio.GRCz11.dna_sm.primary_assembly',is_prefix=True)
gtf = check_env('/share/public6/data/huangt/database/zebrafish/Danio_rerio.GRCz11.92.gtf',unknown=True)

#environment
tophat2 = check_env('/share/public/apps/bin/tophat2')
samtools = check_env('/share/public/apps/bin/samtools')

PATH = "./"

for fn in os.listdir(sys.argv[1]):
	if os.path.isfile(fn) == True and fn.endswith("fastq"):
		SJM = fn.replace(".fastq","") + ".sjm"
		name = fn.replace(".fastq","")
		workpath = PATH + "/" + name + "/"
		JOB = job(workpath,SJM) 
		#Quality trim
		JOB.step_start(step_name="QC",memory="20G")
		JOB.add_process("{cutadapt} -a {adapter} -q 20 -e 0.25 --discard-untrimmed -m 20 -o {name}.cutadapt.fastq {name}.fastq;\n".format(cutadapt=cutadapt,adapter="ATCTCGTATGCCGTCTTCTGCTTG",name=name))
		JOB.add_process("{java} -jar {trimmomatic} SE -phred33 {name}.cutadapt.fastq {name}.trim.fastq SLIDINGWINDOW:4:20 CROP:50 MINLEN:20;\n".format(java=java,trimmomatic=trimmomatic,name=name))
		JOB.step_end()
		#END
		JOB.job_finish()
		#JOB.submit()