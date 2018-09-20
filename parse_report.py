"""STAR report parser

Workflow to detect all final.out files, parse their contents and plot the stats

get_file_list >> parse_list_of_files >> merge_data >> plot_datadict
"""


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import re
import glob
import fnmatch

general_info = ["Number of input reads", "Uniquely mapped reads %", "% of reads mapped to multiple loci", "% of reads mapped to too many loci"]
splice_info = ["Number of splices: Total", "Number of splices: GT/AG", "Number of splices: GC/AG", "Number of splices: AT/AC","Number of splices: Non-canonical" ]

def get_file_list(working_directory = os.getcwd()):
    """Walk down working directory and get list of report files
    """
    filelist = []
    for root, dir, file in os.walk(working_directory):
    	filelist.extend([os.path.join(root, f) for f in file if fnmatch.fnmatch(f, "*final.out")])
    return filelist

def parse_one_file(filename, infolist):
    """Open a single report file and extract the rows indicated in infolist

       To be called by parse_list_of_files
    """   		
    outp_dict = {}
    with open(filename, "r") as fh:
            for line in fh:
                for pat in infolist:
                    if re.search(pat, line):
                         outp_dict[pat] = line.split("|")[1].strip().replace("%","")
    return outp_dict   

def parse_list_of_files(filelist, infolist):
    """Process a list of report files
    """
    outp_dic = {"/".join([filename.split("/")[-2], filename.split("/")[-1]]).replace("Log.final.out", "") : parse_one_file(filename, infolist) for filename in filelist}
    return outp_dic

def merge_data(filedict):
    """Convert dictionary of report files to dictionary of alignment metrics
    """
    samplelist = [name for name in filedict]
    infolist = [name for name in filedict[samplelist[0]]]
    
    outp_dict = {}
    for info in infolist:
        
        outp_dict[info] = {k : v for (k,v) in zip(filedict.keys(), [val[info] for val in list(filedict.values())])}
    return outp_dict

def plot_datadict(datadict):
    """Plot dictionary output from merge_data
    """
    
    plt.figure(figsize=(20,20))
    num_plots = len(datadict)
    for i in range(len(datadict)):
        dataname = list(datadict.keys())[i]
        dataframe = pd.DataFrame(datadict[list(datadict.keys())[i]], index=["val"])
        dataseries = dataframe.stack().astype(np.float).reset_index().iloc[:,1:3].rename({"level_1":"file", 0:"val"}, axis="columns")
        dataseries["pass"] = dataseries["file"].str.split("/", expand=True)[0]
        dataseries["sample"] = dataseries["file"].str.split("/", expand=True)[1]
        plt.subplot(np.ceil(num_plots/2),2,(i+1))
        g = sns.barplot(data = dataseries, x="sample", y="val", hue="pass")
        plt.title(dataname)
        plt.xticks(rotation=90)
    plt.tight_layout()    
    plt.show()
