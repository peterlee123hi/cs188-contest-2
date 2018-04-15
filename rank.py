import os
from os import listdir
from os.path import isfile, join

import subprocess
from multiprocessing import Process

SUBMISSIONS_DIR = './single_submissions/'
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

def log_output(file_a, file_b, output):
    f = open('match_outputs.log', 'a')
    f.write('Output for match ' + file_a + ' vs. ' + file_b + '\n')
    f.write(str(output) + '\n')
    f.write('-' * 8 + '\n\n')
    f.close()

def log_error(file_a, file_b, output):
    f = open('match_errors.log', 'a')
    f.write('Error in match ' + file_a + ' vs. ' + file_b + '\n')
    f.write(str(output) + '\n')
    f.write('-' * 8 + '\n\n')
    f.close()

def write_output(file_a, file_b):
    file_name_a = removeExtension(file_a)
    file_name_b = removeExtension(file_b)
    file_name = file_name_a + '_vs_' + file_name_b + '.dat'

    if not os.path.exists('./match_results'):
        os.makedirs('./match_results')

    with open('./match_results/' + file_name, 'a') as f:
        print('Testing opponents: ' + file_name_a + ' vs. ' + file_name_b)
        for t in range(NUM_TRIALS):
            print('Running match', t + 1, 'for', file_name_a, 'vs.', file_name_b)
            if t % 2 == 0:
                match_output = getOutput(file_a, file_b)
                if 'Red team wins' in match_output:
                    f.write(file_name_a + '\n')
                    print(file_name_a, 'beat', file_name_b)
                elif 'Blue team wins' in match_output:
                    f.write(file_name_b + '\n')
                    print(file_name_b, 'beat', file_name_a)
                elif 'Tie game!' in match_output:
                    f.write('tied' + '\n')
                    print('Tied game.')
                else:
                    f.write('invalid' + '\n')
                    # log_error(file_a, file_b, match_output)
                    print('Invalid match...')
                # log_output(file_a, file_b, match_output)
            else:
                match_output = getOutput(file_b, file_a)
                if 'Red team wins' in match_output:
                    f.write(file_name_b + '\n')
                    print(file_name_b, 'beat', file_name_a)
                elif 'Blue team wins' in match_output:
                    f.write(file_name_a + '\n')
                    print(file_name_a, 'beat', file_name_b)
                elif 'Tie game!' in match_output:
                    f.write('tied' + '\n')
                    print('Tied game.')
                else:
                    f.write('invalid' + '\n')
                    # log_error(file_a, file_b, match_output)
                    print('Invalid match...')
                # log_output(file_a, file_b, match_output)
        print('Done with', file_name_a, 'vs.', file_name_b)

if __name__ == '__main__':
    files = sorted([f for f in listdir(SUBMISSIONS_DIR) if isfile(join(SUBMISSIONS_DIR, f)) and f[-1] != 'c'])

    processes= []
    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            process = Process(target=write_output, args=(files[i], files[j]))
            processes.append(process)

    NUM_PROCESSES = 32
    for idx in range(0, len(processes), NUM_PROCESSES):
        for process in processes[idx:min(idx+NUM_PROCESSES,len(processes))]:
            process.start()
        for process in processes[idx:min(idx+NUM_PROCESSES,len(processes))]:
            process.join()

