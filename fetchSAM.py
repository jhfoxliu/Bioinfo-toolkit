#!usr/bin/env python
import sys,os
import pysam
from optparse import OptionParser

def fetchRegion(mode="print",output=None,until_eof=False,tag_only=False):
	global input,options
	if mode == "print":
		for read in input.fetch(options.fetch,until_eof=until_eof):
			if options.tag:
				tag = options.tag.split(":")
				if str(read.get_tag(tag[0])) == tag[1]:
					print read 
			else:
				print read
	elif mode == "write" and tag_only == False:
		for read in input.fetch(options.fetch,until_eof=until_eof):
			if options.tag:
				tag = options.tag.split(":")
				if str(read.get_tag(tag[0])) == tag[1]:
					output.write(read)
			else:
				output.write(read)
	elif mode == "write" and tag_only == True:
		for read in input.fetch(until_eof=until_eof):
			tag = options.tag.split(":")
			if str(read.get_tag(tag[0])) == tag[1]:
				 output.write(read)

if __name__ == "__main__":
	#Parser
	usage = "Usage: Fetch a specific reference id from RNA-seq SAM/BAM file"
	parser = OptionParser(usage=usage)
	parser.add_option("-s","--sam",dest="input",help="Sam/Bam file input")
	parser.add_option("-f","--fetch",dest="fetch",help="Fetch something")
	parser.add_option("-o","--output",dest="output",help="Bam file input, if not, output to stdout")
	parser.add_option("--tag",dest="tag",help="SAM tag, format: tag:value")
	parser.add_option("--no_index",dest="index",default=True,action="store_false",help="Do not build index for the bam output")
	(options,args) = parser.parse_args()
	
	input_name = str(options.input).split(".")[-1]
	tmp = []
	if input_name == "bam":
		with pysam.AlignmentFile(options.input,"rb") as input:
			if options.output:
				with pysam.AlignmentFile(options.output,"wb",template=input) as output:
					if options.fetch:
						fetchRegion(mode="write",output=output)
					else:
						if options.tag:
							fetchRegion(mode="write",output=output,until_eof=True)
						else:
							print "no --fetch or --tag provided, exit"
							sys.exit()
			else:
				fetchRegion(mode="print")
	else:
		print "Please provide an indexed bam."
		sys.exit()
	if options.index:
		os.system("samtools index %s" % options.output)
