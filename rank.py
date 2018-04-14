import os
from os import listdir
from os.path import isfile, join

import subprocess
from threading import Thread

SUBMISSIONS_DIR = './submissions/'
NUM_TRIALS = 15

def removeExtension(file_name):
    idx = -1
    for i, c in enumerate(file_name):
        if c == '.':
            idx = i
            break
    if idx >= 0:
        return file_name[:idx]
    return file_name

def getOutput(file_a, file_b):
    try:
        output = str(subprocess.check_output(['python2.7',
                            'capture.py',
                            '-r',
                            join(SUBMISSIONS_DIR, file_a),
                            '-b',
                            join(SUBMISSIONS_DIR, file_b),
                            '-l',
                            'RANDOM',
                            '-q']))
    except:
        return 'invalid'
    return output

def write_output(file_a, file_b):
    file_name_a = removeExtension(file_a)
    file_name_b = removeExtension(file_b)
    file_name = file_name_a + '.' + file_name_b + '.dat'
    file_output = ''
    if not os.path.exists('./match_results'):
        os.makedirs('./match_results')
    with open('./match_results/' + file_name, 'a') as f:
        print('Testing opponents: ' + file_name_a + ' vs. ' + file_name_b)
        for t in range(NUM_TRIALS):
            print('Running match', t + 1)
            if t % 2 == 0:
                match_output = getOutput(file_a, file_b)
                if 'The Red team has returned' in match_output:
                    file_output += file_name_a + '\n'
                    print(file_name_a, 'won!')
                elif 'The Blue team has returned' in match_output:
                    file_output += file_name_b + '\n'
                    print(file_name_b, 'won!')
                elif 'Tie game!' in match_output:
                    file_output += 'tie' + '\n'
                    print('Tied game.')
                else:
                    file_output += 'invalid\n'
                    print('Invalid match...')
            else:
                match_output = getOutput(file_b, file_a)
                if 'The Red team has returned' in match_output:
                    file_output += file_name_b + '\n'
                    print(file_name_b, 'won!')
                elif 'The Blue team has returned' in match_output:
                    file_output += file_name_a + '\n'
                    print(file_name_a, 'won!')
                elif 'Tie game!' in match_output:
                    file_output += 'tie' + '\n'
                    print('Tied game.')
                else:
                    file_output += 'invalid\n'
                    print('Invalid match...')
        f.write(file_output)
        print('Done with', file_name_a, 'vs.', file_name_b)

if __name__ == '__main__':
    files = sorted([f for f in listdir(SUBMISSIONS_DIR) if isfile(join(SUBMISSIONS_DIR, f)) and f[-1] != 'c'])

    threads = []
    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            thread = Thread(target=write_output, args=(files[i], files[j]))
            threads.append(thread)

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
