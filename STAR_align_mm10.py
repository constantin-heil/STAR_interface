"""STAR_align

This module contains two functions for automating 2-pass STAR alignment of RNA-seq data.

Paths to STAR executable, genome and genome annotation are hardcoded.
This version is for mouse mm10
"""

import os
import sys
import glob
import fnmatch
from subprocess import run



def run_aligner(working_path = os.getcwd(), sjdb_list = None):

	"""Call STAR aligner

	If called with sjdb list will write to directroy ./second_pass, otherwise ./first_pass
	"""	
	
	file_list = glob.glob(working_path + "/*.fq.gz")
	STAR_path = "/home/bioinf/bio_work/bio_tools/STAR-2.5.4b/source/STAR"
	genome_dir = "/home/bioinf/bio_work/genomes/Mm_m38/STAR_ix"
	gtf_file = "/home/bioinf/bio_work/genomes/Mm_m38/Mus_musculus.GRCm38.92.gtf"
	fixed_settings = ["--outSAMattributes NH HI AS nM XS", "--sjdbOverhang 100", "--outSAMtype BAM SortedByCoordinate", "--runThreadN 10", "--readFilesCommand zcat"]
	command_list = [[STAR_path, "--genomeDir", genome_dir, "--sjdbGTFfile", gtf_file, "--readFilesIn", in_file, "--outFileNamePrefix", in_file.split("/")[-1].split(".")[0]] + fixed_settings for in_file in file_list]
	
	

	if sjdb_list:
		second_wd = os.path.join(working_path, "second_pass")
		command_list = [e + ["--sjdbFileChrStartEnd"] + sjdb_list for e in command_list]
		os.mkdir(second_wd)
		print(f"Running second pass alignment with {second_wd} as working directory")
		proc_list = [run(command, cwd = second_wd) for command in command_list]
			
	else:
		first_wd = os.path.join(working_path, "first_pass")
		os.mkdir(first_wd)
		print("Running first pass")
		proc_list = [run(command, cwd = first_wd) for command in command_list]


def get_sjdb_list(working_path = os.getcwd()):

	"""Scan current path and children for files ending in SJ.out.tab
	"""
	sjdb_list = []

	for root, dir, files in os.walk(working_path):
		for match in fnmatch.filter(files, "*SJ.out.tab"):
			sjdb_list.append(os.path.join(root, match))

	return sjdb_list 
