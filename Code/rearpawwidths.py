#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 13:30:41 2020

@author: hessil
"""

import h5py as h5
import os
import statistics 
import pandas as pd
import argparse
import csv
import re
minconf=0.3

def removeconfs(points, confs):
    frames=[]
    
    for i in range(confs.shape[1]):
        if confs.iloc[0,i]<minconf:
            points=points.drop(columns=i)
        elif confs.iloc[1,i]<minconf:
            points=points.drop(columns=i)
        else:
            frames.append(str(i))
            
    return(points)
    
def extractdata(in_file):
    pose_dir,filename = os.path.split(in_file)
    os.chdir(pose_dir)
    
    s=h5.File(filename, 'r')
    h=s['poseest']
    points=h['points']
    confs=h['confidence']
    
    df0=pd.DataFrame.from_records(data=points)
    df1=df0.iloc[:,7]
    df3=df0.iloc[:,8]
    dfpoints=pd.DataFrame.from_records(data=(df1,df3))
    
    dfc0=pd.DataFrame.from_records(data=confs)
    dfc1=dfc0.iloc[:, 7]
    dfc3=dfc0.iloc[:, 8]
    dfconfs=pd.DataFrame.from_records(data=(dfc1,dfc3))

    return(dfpoints, dfconfs)
    
def extractpoints(point):
    point=str(point)
    
    point=point.replace(']','')
    point=point.replace('[','')
    
    numbers = [int(word) for word in point.split() if word.isdigit()]
    #print(numbers)
    return(numbers)

def distance(A,C):
    import math
    sq1 = (A[0]-C[0])**2
    sq2 = (A[1]-C[1])**2
    return (math.sqrt(sq1 + sq2))

def perframe(pointsr):
    
    dAC=[]
    frames=pointsr.columns.values.tolist()   
    for i in range(0,pointsr.shape[1]):
        A=extractpoints(pointsr.iloc[0,i])
        C=extractpoints(pointsr.iloc[1,i])
        
        dAC.append(distance(A,C))
        
    meandAC= statistics.mean(dAC)
    meddAC=statistics.median(dAC)
    return(meandAC,meddAC)

    
def main():
    parser = argparse.ArgumentParser(
        description='Rear paw width')
    
    parser.add_argument(
        '--input-root-dir',
        required=True,
        help='the root directory for input files',
    )
    parser.add_argument(
        '--output-root-dir',
        required=True,
        help='the root directory for output files',
    )
    
    parser.add_argument(
        '--video-file-list',
        required=True,
        help='the list of videos to process (default is all AVI files in the input dir)',
    )
    
    
    args = parser.parse_args()
    input_root_dir = args.input_root_dir
    output_root_dir = args.output_root_dir
    video_file_list= args.video_file_list

    input_file_paths = []
    with open(video_file_list, newline='') as video_file_list_file:
        video_file_list_reader = csv.reader(video_file_list_file, delimiter='\t')
        
        for i, row in enumerate(video_file_list_reader):
            
            if row and row[0]:
                # skip header row
                if i > 0 or row[0] != 'NetworkFilename':
                    ##
                    row[0]=re.sub('.avi','_pose_est_v2.h5', row[0])
                    ##
                    pose_filepath = os.path.join(input_root_dir, row[0])
                    if os.path.isfile(pose_filepath):
                        input_file_paths.append(row[0])
                    else:
                        print('missing file:', pose_filepath)
    
    maxlen=[]
    mico=[]
    with open(input_root_dir+'/rearpawsave.csv', 'a') as outfile:
        writer = csv.writer(outfile)
        for i,in_rel_file in enumerate(input_file_paths):
            print('i:', i)
            in_file = os.path.join(input_root_dir, in_rel_file) 
            pose_dir, pose_filename = os.path.split(in_file)
            netfilesub=re.sub('_pose_est_v2.h5','.avi',in_rel_file)
            pose_name, _ = os.path.splitext(pose_filename)
            try:
                points,confs=extractdata(in_file)
                this=perframe(removeconfs(points, confs))
                maxlen.append(this)
                writer.writerow(this)
                mico.append(netfilesub)
            except:
                print('i='+str(i)+' unable to open: '+in_file)
            
    
    maxlendf=pd.DataFrame(maxlen,columns=['mean_rearpaw','median_rearpaw'])
    maxlendf['NetworkFilename']=mico
    mxlendf=maxlendf.set_index('NetworkFilename')
    maxlendf.to_csv(output_root_dir+'/rearpaw.csv')

main()