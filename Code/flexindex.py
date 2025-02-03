#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 12:27:52 2020

@author: hessil
"""

#3 = base of neck 6= center spine 9=base of tail
import h5py as h5
import os
import statistics 
import pandas as pd
import argparse
import csv
import re
minconf=0.3

def extractdata(in_file):
    pose_dir,filename = os.path.split(in_file)
    os.chdir(pose_dir)
    
    s=h5.File(filename, 'r')
    h=s['poseest']
    points=h['points']
    confs=h['confidence']
    
    df0=pd.DataFrame.from_records(data=points)
    df1=df0.iloc[:,3]
    df2=df0.iloc[:,6]
    df3=df0.iloc[:,9]
    dfpoints=pd.DataFrame.from_records(data=(df1,df2,df3))
    #dfpoints.to_csv(r"/Users/hessil/Box/agingALL/dfpoints.csv")
    
    dfc0=pd.DataFrame.from_records(data=confs)
    dfc1=dfc0.iloc[:,3]
    dfc2=dfc0.iloc[:,6]
    dfc3=dfc0.iloc[:,9]
    dfconfs=pd.DataFrame.from_records(data=(dfc1,dfc2,dfc3))
    #dfconfs.to_csv(r"/Users/hessil/Box/agingALL/dfconfs.csv")
    
    #print('part 1 run!')
    return(dfpoints, dfconfs)
    
def removeconfs(points, confs):
    frames=[]
    
    for i in range(confs.shape[1]):
        if confs.iloc[0,i]<minconf:
            points=points.drop(columns=confs.columns.values[i])
            #print ('dropped',i)
        elif confs.iloc[1,i]<minconf:
            points=points.drop(columns=confs.columns.values[i])
            #print ('dropped',i)
        elif confs.iloc[2,i]<minconf:
            points=points.drop(columns=confs.columns.values[i])
            #print ('dropped',i)
        else:
            frames.append(str(i))
            
#    print(points.shape[1])        
#    print(len(frames))
    #points.to_csv(r"/Users/hessil/Box/agingALL/FI/pointsremoved.csv")
    #print('low confs removed')
    return(points)
    
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

def distB(A,B,C):
    mp=[]
    mp.append((A[0]+C[0])/2)
    mp.append((A[1]+C[1])/2)
    return(distance(mp,B))

def lengthSquare(X, Y):  
    xDiff = X[0] - Y[0]  
    yDiff = X[1] - Y[1]  
    return xDiff * xDiff + yDiff * yDiff 
      
def angle(A, B, C):  
    import math 
    # Square of lengths be a2, b2, c2  
    a2 = lengthSquare(B, C)  
    b2 = lengthSquare(A, C) 
    c2 = lengthSquare(A, B)
  
    # length of sides be a, b, c  
    a = (math.sqrt(a2)) 
    b = (math.sqrt(b2)) 
    c = (math.sqrt(c2)) 
  
    # From Cosine law  
    try:
        betta = math.acos((a2 + c2 - b2) / (2 * a * c))
        betta = betta * 180 / math.pi
        return (betta)
    except:
        
        return(180)
    
def perframe(pointsr, out_filename_base):
    
    dAC=[]
    dB=[]
    aABC=[]
    frames=pointsr.columns.values.tolist()   
    rowdex=['dAC','dB','aABC']
    #print(frames)
    for i in range(0,pointsr.shape[1]):
        A=extractpoints(pointsr.iloc[0,i])
        B=extractpoints(pointsr.iloc[1,i])
        C=extractpoints(pointsr.iloc[2,i])
        
        dAC.append(distance(A,C))
        dB.append(distB(A,B,C))
        aABC.append(angle(A,B,C))
        
    maxdAC= max(dAC)
    rdAC=[i/maxdAC for i in dAC]

    
    
    perframes=pd.DataFrame(data=[rdAC,dB,aABC], columns=frames, index=rowdex)
    #perframes.to_csv(out_filename_base+'_perframe.csv')
    return(perframes)
    
    
def vidfeatures(perframft,out_filename_base ):
    dAC=[]
    dB=[]
    aABC=[]
    nrows=[dAC,dB,aABC]
    output_root_dir,pose_name=os.path.split(out_filename_base)
    colmns=['mean','standard deviation', 'min','max','median']
    rowdex=['dAC :'+str(pose_name),'dB :'+str(pose_name),'aABC :'+str(pose_name)]
    for i in range(perframft.shape[0]):
        alls=perframft.iloc[i, :].tolist()
        nrows[i].append(statistics.mean(alls))
        nrows[i].append(statistics.stdev(alls))
        nrows[i].append(min(alls))
        nrows[i].append(max(alls))
        nrows[i].append(statistics.median(alls))
    #print(dAB)
    pervideofts=pd.DataFrame(data=nrows, columns=colmns, index=rowdex)
    #pervideofts.to_csv(out_filename_base+'_pervideo.csv')
    return(pervideofts)
    
    
    
def windowfeatures(perframft, windowd, out_filename_base):
    perframft=perframft.iloc[:, 1:1000]
    #window=windowd*30
    
    windows=windowd*30
    frames=[int(m) for m in (perframft.columns.values.tolist())]
    #colmns=['mean','standard deviation', 'min','max','median']
#    window1=[]
#    window3=[]
#    window9=[]
#    windowlist=[window1,window3,window9]
#    
#    for l in range(len(windowlist)):
   
    dAC=[]
    dB=[]
    aABC=[]
    nrows=[dAC,dB,aABC]
    rowdex=['dAC','dB','aABC']
    for u in range(perframft.shape[0]):
            #print('u', u)
        for i in range(perframft.shape[1]-1):
            #print(i)
            #frames=frames[0:(len(frames)-600)]
            firstfr=frames[i]
            ender=firstfr+windows
            try:
                endfr = list(map(lambda i: i> ender, frames)).index(True) 
                
            except:
#                    for h in range(perframft.shape[1]-1-i):
#                        nrows[u].append('NA')
                break
            
            finally:
                alls=perframft.iloc[u, i:(endfr-1)].tolist()
                if len(alls)<5:
                    for m in range(0,5):
                        nrows[u].append('NA')
                else:    
                        
                    nrows[u].append(statistics.mean(alls))
                    nrows[u].append(statistics.stdev(alls))
                    nrows[u].append(min(alls))
                    nrows[u].append(max(alls))
                    nrows[u].append(statistics.median(alls))
                #print(i)
#        windowlist[l].append(nrows)        
        
    perwindowfts=pd.DataFrame(data=nrows, index=rowdex)      
    perwindowfts.to_csv(out_filename_base+'_window_'+str(windowd)+".csv")    

    
def main():
    # os.chdir('/Users/hessil/Box/agingALL/FI')
    
    parser = argparse.ArgumentParser(
        description='Flexibility Indexing')
    
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

    print('HELLO')
    
    input_file_paths = []
    with open(args.video_file_list) as video_file_list_file:
        print(video_file_list_file)
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
    
    print(len(input_file_paths))
    netfiles=[]
    pervidfeats=[]
    

    
    for i,in_rel_file in enumerate(input_file_paths):
        print('i:', i)
        in_file = os.path.join(input_root_dir, in_rel_file) 
        pose_dir, pose_filename = os.path.split(in_file)
        netfilesub=re.sub('_pose_est_v2.h5','.avi',in_rel_file)
        pose_name, _ = os.path.splitext(pose_filename)
        out_filename_base = os.path.join(
                output_root_dir,
                pose_name )
       
        try:
            points,confs=extractdata(in_file)
            perframedf=perframe(removeconfs(points, confs), out_filename_base)
            pervids=vidfeatures(perframedf, out_filename_base)
            pervidfeats.append(pervids)
        #windowfeatures(perframedf,9, out_filename_base)
            m=0
            while m<3:
            
                netfiles.append(netfilesub)
                m=m+1
        except Exception as e:
            print(e)
            print(in_rel_file)
            cols=['mean','standard deviation','min','max','median']
            a=[np.nan,np.nan,np.nan,np.nan,np.nan]
            b=[np.nan,np.nan,np.nan,np.nan,np.nan]
            c=[np.nan,np.nan,np.nan,np.nan,np.nan]
            d=[a,b,c]
            dex=[str(in_rel_file)+'1',str(in_rel_file)+'2',str(in_rel_file)+'3']
            newp=pd.DataFrame.from_records(data=d, columns=cols,index=dex)
            pervidfeats.append(newp)
            m=0
            while m<3:
                netfiles.append(in_rel_file)
                m=m+1
    
    allpervideos=pd.concat(pervidfeats)
    allpervideos['NetworkFilename']=netfiles
    allpervideos.set_index('NetworkFilename')
    allpervideos.to_csv(output_root_dir+'/flexdexraw.csv')

    dAC=allpervideos.iloc[0::3, :]
    dB=allpervideos.iloc[1::3, :]
    aABC=allpervideos.iloc[2::3, :]
    these=[dAC,dB,aABC]
    text=['dAC','dB','aABC']
    
    for y in range(len(these)):
        these[y].columns=[text[y]+'_mean',text[y]+'_stdev',text[y]+'_min',text[y]+'_max',text[y]+'_median','NetworkFilename']
    
    dAC.to_csv(output_root_dir+"/dAC.csv")
    dB.to_csv(output_root_dir+"/dB.csv")
    aABC.to_csv(output_root_dir+"/aABC.csv")
   
main()
