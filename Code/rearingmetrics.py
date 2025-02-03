#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 08:17:11 2020

@author: hessil
"""


import h5py as h5
import os
import statistics 
import pandas as pd
import argparse
import csv
import re
import yaml
import imageio
import numpy as np
import cv2
minconf=0.3

def extractdata(in_file):
    pose_dir,filename = os.path.split(in_file)
    os.chdir(pose_dir)
    
    s=h5.File(filename, 'r')
    h=s['poseest']
    points=h['points']
    confs=h['confidence']
    
    df0=pd.DataFrame.from_records(data=points)
    df1=df0.iloc[:,0]
    df2=df0.iloc[:,1]
#    df3=df0.iloc[:,3]
#    df4=df0.iloc[:,4]
    dfc0=pd.DataFrame.from_records(data=confs)
    dfc1=dfc0.iloc[:,0]
    dfc2=dfc0.iloc[:,1]
#    dfc3=dfc0.iloc[:,3]
    
    points=pd.DataFrame.from_records(data=(df1,df2))#,df3,df4))
    confs=pd.DataFrame.from_records(data=(dfc1,dfc2))#, dfc3))
    return(points ,confs)
    
def removeconfs(points, confs):
    #frames=[]
    for i in range(confs.shape[1]):
        
        if confs.iloc[0,i]<minconf:
            points=points.drop(columns=confs.columns.values[i])
    
    return (points)  
#    for a in range(points.shape[0]-1):
#        point=points.iloc[a:a+1,:]
#        for i in range(confs.shape[1]):
#            if confs.iloc[a,i]<minconf:
#                point=point.drop(columns=confs.columns.values[i])
#            #print ('dropped',i)
#        frames.append(point)
#            
#    return(frames)


def extractpoints(point):
    point=str(point)
    point=point.replace(']','')
    point=point.replace('[','')
    
    numbers = [int(word) for word in point.split() if word.isdigit()]
  
    return(numbers)
    
def extractpoints2(point):
    point=str(point)
    point=point.replace('(','')
    point=point.replace(')','')
    point=point.replace(',','')
#    print(point)
#    print(point.split())
    numbers = [int(word) for word in point.split() if word.isdigit()]
#    print('numbers')
#    print(numbers)
    return(numbers)

def checkforrear(points, max_contour):
    print('checking for rear')
    frames=[]
    xs=[]
    ys=[]
    ff=[]
    fr=points.columns.values.tolist()
    for i in range(points.shape[1]):
       
        x=int(extractpoints(points.iloc[0,i])[1])
        y=int(extractpoints(points.iloc[0,i])[0])
        #print(x,y)
        xs.append(x)
        ys.append(y)
        ff.append(fr[i])
        #print(max_contour)
        dist=cv2.pointPolygonTest(max_contour, (x,y), True)
        
        if dist<(-5):
            frames.append(points.columns.values[i])
    return(frames,xs,ys,ff,dist)
    
def rearbouts(frames):
    newlist = []
    start = 0
    #end=0
    lens=[]
    
    while frames[start+1]<frames[-1]:
        end=start
        
        while frames[end+1]<(frames[end]+10):
                end=end+1
                if end+1==len(frames):
                    break
        if len(frames[start:end])>0:
            lens.append(len(frames[start:end]))
            newlist.append(frames[start:end])
        start=end+1
            
        if start+1>(len(frames)-1):
            break

    #print(sum(lens))
    return(newlist)

def boutcheck(rearlist):
    startframes=[]
    duration=[]
    boutlens=[]
    
    for i in range(len(rearlist)):
        
        boutlens.append(len(rearlist[i])/30)
        startframes.append((rearlist[i][0]/30))
        duration.append((len(rearlist[i])/30))
        
    avboutlen=statistics.mean(boutlens)
    return(avboutlen, startframes, duration)

def makebins(startframe):
    bins=[]
    bins.append(startframe)
    newbin=int(startframe)
    for i in range(0,8):
        newbin=newbin+9000
        bins.append(newbin)
        
    #print((bins))
    return(bins)

def databins(bins, mouseframes):
    popbins=[]
    for u in range(len(bins)):
#        print('U:'+str(u))
#        print(bins[u])
        
        count=0
        for i in range(len(mouseframes)):
            if u!=(len(bins)-1):
                #try:
#                print(i)
#                print(mouseframes[i]*30)
#                print(bins[u+1])
                if bins[u]<(mouseframes[i]*30)<bins[u+1]:
                    count=count+1
                #except:
                   
            else:
                if bins[u]<(mouseframes[i]*30)<(bins[u]+9000):
                    count=count+1
        popbins.append(count)
    #print(popbins)
    return(popbins)
               

def contour(video):
    reader = imageio.get_reader(video)
    img_iter = reader.iter_data()
    raw_frame = next(img_iter)
    gray = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2GRAY)
# Apply an adaptive threshold [center - (7 pixel window mean) - 10 >= 0]
    thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,7,10)
# Find contours/lines
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
# Plot them (for later)
    img_cont = np.zeros(gray.shape, np.uint8)
    img_cont = cv2.drawContours(img_cont, contours, -1, (255,0,0), 1)
# Find the largest area
    max_area = -1
    max_contour = None
    for ind_cont in contours:
        if cv2.contourArea(ind_cont) > max_area:
            max_area=cv2.contourArea(ind_cont)
            max_contour=ind_cont
    print(max_contour)
    print(max_area)
    print(np.power(raw_frame.shape[0]/2, 2))
    if max_area>=np.power(raw_frame.shape[0]/2, 2):
        print('contour good')
        return(max_contour)

    else:
        return('hi')

def cornerpoints(input_root_dir,yam):
    print(input_root_dir+'/'+yam)
    with open(input_root_dir+'/'+yam,'r') as file:
        
        corners=yaml.full_load(file).get('corner_coords')
        print('got')
        
        xs=corners.get('xs')
        ys=corners.get('ys')
    
    xmin=(xs[0]+xs[2])/2
    xmax=(xs[1]+xs[3])/2

    ymin=(ys[0]+ys[1])/2
    ymax=(ys[2]+ys[3])/2
    corn=[[[int(xs[0]),int(ys[0])]],[[int(xs[1]),int(ys[1])]],[[int(xs[2]),int(ys[2])]],[[int(xs[3]),int(ys[3])]]]
    
    coords=[xmin,xmax,ymin,ymax]
    print(coords,corn)
    return(coords,corn)   

                     
def main():
   
    
    parser = argparse.ArgumentParser(
        description='Rearing metrics')
    
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
        
    
    vids=[]
    input_file_paths = []
    corners=[]

    with open(args.video_file_list) as video_file_list_file:
        video_file_list_reader = csv.reader(video_file_list_file, delimiter='\t')
        
        for i, row in enumerate(video_file_list_reader):
            
            if row and row[0]:
                # skip header row
                if i > 0 or row[0] != 'NetworkFilename':
                    
                    pose=re.sub('.avi','_pose_est_v2.h5', row[0])
                    
                    pose_filepath = os.path.join(input_root_dir, row[0])
                    if os.path.isfile(pose_filepath):
                        input_file_paths.append(pose)
                        vids.append(row[0])
                        corners.append(re.sub('.avi','_corners_v2.yaml',row[0]))
                    else:
                        print('missing file:', pose_filepath)
    
    netfiles=[]
    netfiles2=[]
    pervidfeats=[]
    startframe=[]
    #allframes=[]
    badcon=[]
    
    print(len(vids),len(input_file_paths),len(corners))
    for i,in_rel_file in enumerate(input_file_paths):
        print('i:', i)
        in_file = os.path.join(input_root_dir, in_rel_file) 
        pose_dir, pose_filename = os.path.split(in_file)
        netsname=re.sub('_pose_est_v2.h5','.avi',in_rel_file)
        netfilesub=re.sub('_pose_est_v2.h5','.avi',in_rel_file)
        pose_name, _ = os.path.splitext(pose_filename)
        print(netfilesub)
        print(corners[i])
        print(vids[i])
        try:
        #if i>-1:
            
            coords=contour(input_root_dir+'/'+vids[i])
            # try:
            #     coords,corn=cornerpoints(input_root_dir,corners[i])
            # except:
            #     print('no yaml')
            #     coords=contour(input_root_dir+'/'+vids[i])
                
            # if type(coords)!=str:
            #     corn=[coords[0][0],coords[1][0],coords[2][0],coords[3][0]]
            netfiles.append(netsname)
            # vid=os.path.join(input_root_dir,netsname)
            # max_contour=contour(vid)
            #drw_contour=max_contour+4

            
            if type(coords)==str:
                print('contour bad')
                print(in_rel_file)
                thisrow=['na','na']
                pervidfeats.append(thisrow)
                startframe.append(['na'])
                startframe.append(['na'])
                netfiles2.append(netsname)
                netfiles2.append(netsname)
                badcon.append(netsname)


            else:
                
                point,confs=extractdata(in_file)
                print('extracted')
                points=(removeconfs(point, confs))
                print('cleaned')
                frames,xs,ys,ff,dist=checkforrear(points, coords)
                rearlist=rearbouts(frames)
                numbouts=len(rearlist)
#                    #print(numbouts)
                avbout,startframes,duration=(boutcheck(rearlist))
                thisrow=[numbouts, avbout]
                pervidfeats.append(thisrow)
                startframe.append(startframes)
                startframe.append(duration)
                netfiles2.append(netsname+'_start')
                netfiles2.append(netsname+'_len')
        
        except Exception as e:
             print(in_rel_file,' failed')
             print(e)
             thisrow=['na','na']
             pervidfeats.append(thisrow)
             startframe.append(['na'])
             startframe.append(['na'])
             netfiles2.append(netsname+'_start')
             netfiles2.append(netsname+'_len')


# #       


    allpervideos=pd.DataFrame.from_records(data=pervidfeats,columns=['rear_count', 'avg_bout_len'])
    allpervideos['NetworkFilename']=netfiles
    allpervideos.set_index('NetworkFilename').to_csv(output_root_dir+'/rearingmetrics.csv')

    framos=pd.DataFrame.from_records(data=startframe)
    framos['NetworkFilename']=netfiles2
    framos.set_index('NetworkFilename')
    framos.to_csv(output_root_dir+'/rearing_bouts.csv')

#    frames=framos.set_index('NetworkFilename').iloc[0::2,:]
#    print(frames)
#    frames.to_csv(output_root_dir+'/rearingbouts_2.csv')
#    newdata=[]
#    netfiles=frames.index.values.tolist()
#    for i in range(frames.shape[0]):
#        startframe=frames.iloc[i,0]
#        
#        bins=makebins(startframe)
#        popbins=databins(bins,frames.iloc[i,3:].tolist())
#        newdata.append(popbins)
        
# # ##        
#    binframes=pd.DataFrame.from_records(data=newdata)
#    binframes['NetworkFilename']=netfiles
#    binframes.set_index('NetworkFilename')
#    binframes.to_csv(output_root_dir+'/rearingtimebinmetrics.csv')

    


 
main()
    
