import re
import shutil
from os import listdir
from os.path import isfile, join

RAW_SUBMISSIONS_DIR = './raw_submissions/'
SUBMISSIONS_DIR = './submissions/'

def removeExtension(file_name):
    idx = -1
    for i, c in enumerate(file_name):
        if c == '.':
            idx = i
            break
    if idx >= 0:
        return file_name[:idx]
    return file_name

def keepLine(line):
    # Remove all whitespace
    line = re.sub(r'\s+', '', line)
    if len(line) == 0:
        return False
    b = True
    b = b & ('print' not in line)
    return b

def processFileName(file_name):
    processed = file_name.lower()
    processed = removeExtension(file_name).strip()
    processed = re.sub(r'[^A-Za-z0-9]+', '_', processed)
    processed = re.sub(r'([_]+)$', '', processed)
    return processed + '.py'

if __name__ == '__main__':
    raw_files = sorted([f for f in listdir(RAW_SUBMISSIONS_DIR) if isfile(join(RAW_SUBMISSIONS_DIR, f))])
    files = [processFileName(f) for f in raw_files]
    for raw, processed in zip(raw_files, files):
        # Copy file
        shutil.copy2(RAW_SUBMISSIONS_DIR + raw, SUBMISSIONS_DIR + processed)

        # Read file contents
        contents = open(SUBMISSIONS_DIR + processed, 'r', errors='ignore')
        processed_contents = []
        for line in contents:
            # If not print statement, add to new contents
            if keepLine(line):
                processed_contents.append(line)
            elif len(re.sub(r'\s+', '', line)) > 0:
                print(line)

        # Delete existing file contents
        contents.close()
        contents = open(SUBMISSIONS_DIR + processed, 'w')
        contents.truncate()
        for line in processed_contents:
            contents.write(line)
