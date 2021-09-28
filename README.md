# vFI-features
Code for running features for the visual FI model
There are 5 python scripts to run the different vFI features

## Requirements

Developed in Python 3.6 and Python 3.7
Many of these scripts require pose files generated from the Kumar Lab's mouse pose estimation neural network. Contact us for more information. 

## Rear Paw Widths

rearpawwidths.py will produce the median and mean rear paw width features.
It requires the following packages:

```
h5py
os
statistics
pandas
argparse
csv
re
```

Running it requires 3 arguments:
```
--input-root-dir: the root directory for input files
--output-root-dir: the root directory for output files (defaults to same as input dir)
--video-file-list: the csv list of videos to process (default is all AVI files in the input dir). Pose files of the videos should be in the same directory as the videos
```

Example code for command line:
```
python /home/user/code/rearpawwidths.py --input-root-dir /home/user/data --output-root-dir /home/user/results --video-file-list /home/user/mousefiles.csv
```

## Flexibility Index

flexindex.py will produce the spinal mobility measures (dAC, dB, aABC).

It requires the following packages:
```
h5py
os
statistics
pandas
argparse
csv
re
```

Running it requires 3 arguments:
```
--input-root-dir: the root directory for input files
--output-root-dir: the root directory for output files (defaults to same as input dir)
--video-file-list: the csv list of videos to process (default is all AVI files in the input dir). Pose files of the videos should be in the same directory as the videos
```

Example code for command line:
```
python /home/user/code/flexindex.py --input-root-dir /home/user/data --output-root-dir /home/user/results --video-file-list /home/user/mousefiles.csv
```

## Rearing
rearingmetrics.py will produce the rearing features.

It requires the following packages:
```
h5py
os
statistics
pandas
argparse
csv
re
imageio
numpy
cv2
```

Running it requires 3 arguments:
```
--input-root-dir: the root directory for input files
--output-root-dir: the root directory for output files (defaults to same as input dir)
--video-file-list: the csv list of videos to process (default is all AVI files in the input dir). Pose files of the videos should be in the same directory as the videos
```



Example code for command line:

```
python /home/user/rearingmetrics.py --input-root-dir /home/user/data --output-root-dir /home/user/results --video-file-list /home/user/mousefiles.csv
```


