#!/usr/bin/env python
#Jianheng Liu, 20180709
#Usage: create SJM files

import sys,os
from sjm_tools.sjm_tools import job

if not sys.argv[1]:
	print "Usage: python %s [directory] [submit(optional)]" % (sys.argv[0])
	
#metadata
genome_index = '/share/public6/data/huangt/database/zebrafish/metadata/Danio_rerio.GRCz11.dna_sm.primary_assembly'
trans_index = '/share/public6/data/huangt/database/zebrafish/metadata/tophat2_index/Danio_rerio.GRCz11'
rRNA_seq = '/share/public1/data/liujh/database/zebrafish/rRNA/Danio_rerio.GRCz11.rRNA.19bp.fa'
sortmerna_db = '/share/public1/data/liujh/database/zebrafish/rRNA/sortmerna_db/'
gtf = '/share/public6/data/huangt/database/zebrafish/Danio_rerio.GRCz11.92.gtf'

#environment
perl = '/share/public1/data/liujh/software/perlbrew/perls/perl-5.24.1/bin/perl'
python = '/share/public/apps/bin/python'
samtools = '/share/public1/data/liujh/software/bin/samtools'
tophat2 = '/share/public/apps/bin/tophat2'
cutadapt = '/share/public/data/zhanglab/shared_data/softwares/python-2.7.10/bin/cutadapt'
trimmomatic = '/share/public1/data/liujh/software/Trimmomatic/Trimmomatic-0.36/trimmomatic-0.36.jar'
java = '/share/public1/data/liujh/software/java/jre1.8.0_131/bin/java'
sortmerna = '/share/public/apps/sortmerna-2.1/sortmerna'
htseq = '/share/public/apps/python/3.6.3/bin/htseq-count'
samtools = '/share/public/apps/bin/samtools'
#namespace
PATH = sys.argv[1]
if os.path.isdir(PATH) == False:
	os.mkdir(PATH)

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
		
		#Remove rRNA
		JOB.step_start(step_name="rRNA",memory="100G")
		JOB.add_process("{sortmerna} --ref {rRNA_seq},{sortmerna_db} --reads {name}.trim.fastq --sam --num_alignments 1 --fastx --aligned {name}.rRNA --other {name}.non_rRNA --log -v;\n".format(sortmerna=sortmerna,rRNA_seq=rRNA_seq,sortmerna_db=sortmerna_db,name=name))
		JOB.step_end()
		
		#Remove alignment with tophat2
		JOB.step_start(step_name="Tophat2",memory="100G")
		JOB.add_process("{tophat2} --transcriptome-index {trans_index} -N 1 -p 8 -x 5 -G {gtf} -o ./tophat2_output {name}.non_rRNA.fastq ;\n".format(tophat2=tophat2,genome_index=genome_index,trans_index=trans_index,gtf=gtf,name=name))
		JOB.add_process("{samtools} index ./tophat2_output/accepted_hist.bam ;\n".format(samtools=samtools,genome_index=genome_index,trans_index=trans_index,gtf=gtf,name=name))
		JOB.step_end()
		
		#HTseq 
		JOB.step_start(step_name="HTseq",memory="100G")
		JOB.add_process("{htseq} -f bam  --strand yes -t CDS --nonunique none tophat_out/accepted_hits.bam {gtf} > {name}.count".format(htseq=htseq,gtf=gtf,name=name))
		JOB.step_end()
		
		#END
		JOB.job_finish()
		#JOB.submit()
