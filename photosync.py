#!/usr/bin/env python
"""
Copyright: Gregory Petukhov <lorien@lorien.name>
"""
import glob
import os
import sys
import shutil
from datetime import datetime
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
except ImportError:
    import Image
    from ExifTags import TAGS
import configparser

MOUNT_DIR1 = '/mnt/dcim'
MOUNT_DIR2 = '/mnt/DCIM'
config = configparser.ConfigParser()
config.read(os.path.expanduser('~/.photosync.ini'))
DST_DIR = os.path.expanduser(config['photosync']['export_dir'])


def get_exif(fn):
    if fn.endswith(('nef', 'NEF')):
        fn = fn.replace('.nef', '.jpg').replace('.NEF', '.JPG')
    ret = {}
    i = Image.open(fn)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret


def find_sources():
    if os.path.exists(MOUNT_DIR1):
        dirs = glob.glob(MOUNT_DIR1 + '/*')
    elif os.path.exists(MOUNT_DIR2):
        dirs = glob.glob(MOUNT_DIR2 + '/*')
    else:
        dirs = []
    # quick workaround because I am moving to Nikon D70S
    #dirs = glob.glob(MOUNT_DIR + '/*_pana')
    return dirs
    #pairs = [(int(x.split('/')[-1].split('_')[0]), x) for x in dirs]
    #last = sorted(pairs, key=lambda x: x[0], reverse=True)[0]
    #return last[1]


def process_source(source):
    dates = {}
    for fname in (glob.glob(source + '/*.jpg') +
                  glob.glob(source + '/*.JPG') +
                  glob.glob(source + '/*.nef') +
                  glob.glob(source + '/*.NEF')):
        #ctime = datetime.fromtimestamp(os.stat(fname).st_ctime)
        exif = get_exif(fname)
        ctime = datetime.strptime(exif['DateTime'], '%Y:%m:%d %H:%M:%S')
        dates.setdefault(ctime.date(), []).append(fname)
    for day, fnames in sorted(dates.iteritems(), key=lambda x: x[0]):
        dst_dir = DST_DIR + '/%d/%02d/%02d' % (day.year, day.month, day.day) 
        print 'Processing %s. Directory: %s' % (day.strftime('%d %b %Y'), dst_dir)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for fname in fnames:
            img_fname = os.path.basename(fname)
            dst_path = os.path.join(dst_dir, img_fname)
            if not os.path.exists(dst_path):
                sys.stdout.write('+')
                sys.stdout.flush()
                shutil.copy(fname, dst_path)
            else:
                sys.stdout.write('e')
                sys.stdout.flush()
        print


if __name__ == '__main__':
    for source in find_sources():
        process_source(source)
