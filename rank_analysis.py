from os import listdir
from os.path import isfile, join

def removeExtension(file_name):
    idx = -1
    for i, c in enumerate(file_name):
        if c == '.':
            idx = i
            break
    if idx >= 0:
        return file_name[:idx]
    return file_name

files = sorted([f for f in listdir('./bots') if isfile(join('./bots/', f)) and f[-1] != 'c'])
names = sorted([removeExtension(f) for f in files])

