#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 19:34:53 2020

@author: hessil
"""
import os
import pandas as pd
import argparse
import csv
import re
import numpy as np
import statistics


def process(df,nets):
    newdfstuff=[]
    #nets=df.index.values.tolist()
    for i in range(df.shape[0]):
        #print(i)
        metrics=[]
        thislist=df.iloc[i,:].tolist()
        #print(thislist)
        realist=[s for s in thislist if s != -50]
        realist=[s for s in realist if s != -110]
        realist=[s for s in realist if str(s) != 'nan']
        realist=[s for s in realist if type(s)!=str]
        #print((realist))
        metrics.append(statistics.mean(realist))
        metrics.append(statistics.median(realist))
        newdfstuff.append(metrics)
        
    dfmets=pd.DataFrame.from_records(data=newdfstuff, columns=['mean','median'])  
    dfmets['NetworkFilename']=nets
    dfmets=dfmets.set_index('NetworkFilename')
    print(dfmets)
    #dfmets.to_csv('ellfit_metrics.csv')
    return(dfmets)

def makenewdf(df,output):
    
    os.chdir(output)
    width=df.iloc[0::2,:]
    width.columns=['mean_width','median_width']
    length=df.iloc[1::2,:]
    length.columns=['mean_length','median_length']
    ellipsefit=width.merge(length,how='outer', left_index=True, right_index=True)
    print(ellipsefit.shape)
    ellipsefit.to_csv('ellipsefit.csv')

def extractdata(in_file):
    ellfit=np.load(in_file)
    width=[u[2] for u in ellfit]   
    length=[u[3] for u in ellfit]
        
    return(width,length)

def main():
    # os.chdir('/Users/hessil/Box/agingALL/FI')
    
    parser = argparse.ArgumentParser(
        description='Ellipse fit width and length')
    
    parser.add_argument(
        '--input-root-dir',
        required=True,
        help='the root directory for input files',
    )
    parser.add_argument(
        '--output-root-dir',
        required=False,
        help='the root directory for output files (defaults to same as input dir)',
    )
    parser.add_argument(
        '--video-file-list',
        required=True,
        help='the list of videos to process (default is all AVI files in the input dir)',
    )
    
    
    args = parser.parse_args()
    input_root_dir = args.input_root_dir
    output_root_dir = args.output_root_dir
    if output_root_dir is None:
        output_root_dir = input_root_dir
    
    missing=[]
    input_file_paths = []
    with open(args.video_file_list, newline='') as video_file_list_file:
        video_file_list_reader = csv.reader(video_file_list_file, delimiter='\t')
        
        for i, row in enumerate(video_file_list_reader):
            
            if row and row[0]:
                # skip header row
                if i > 0 or row[0] != 'NetworkFilename':
                    ##
                    name=row[0]
                    row[0]=re.sub('.avi','_ellfit.npy', row[0])
                    ##
                    pose_filepath = os.path.join(input_root_dir, row[0])
                    if os.path.isfile(pose_filepath):
                        input_file_paths.append(row[0])
                    else:
                        print('missing file:', pose_filepath)
                        missing.append(name)
    print(i)
    # filepd=pd.Series(missing)
    # filepd.to_csv(output_root_dir+'/missing_ellfit.csv')
    print(len(input_file_paths))
    netfiles=[]
    permouse=[]
    
    for i,in_rel_file in enumerate(input_file_paths):
        print('i:', i)
        in_file = os.path.join(input_root_dir, in_rel_file) 
        pose_dir, pose_filename = os.path.split(in_file)
        netfilesub=re.sub('_ellfit.npy','.avi',in_rel_file)
        print(netfilesub)
        #pose_name, _ = os.path.splitext(pose_filename)
       # out_filename_base = os.path.join(output_root_dir,pose_name )
       
        width,length=extractdata(in_file)
        
        permouse.append(width)
        permouse.append(length)
        netfiles.append(netfilesub)
        netfiles.append(netfilesub)
         
        
    
    allpervideos=pd.DataFrame.from_records(data=permouse)
    allpervideos['NetworkFilename']=netfiles
    allpervideos.set_index('NetworkFilename')
    #print(allpervideos.shape[0])
    df=process(allpervideos,netfiles)
    makenewdf(df, output_root_dir)
    
    
main()