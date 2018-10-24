#!/usr/bin/env python
import subprocess
import time

current_time = lambda: int(round(time.time()))

f = open('rockyou.txt', 'r')
steg_path = '~/Downloads/steg.jpg'
s_time = current_time()
c_time = current_time()
attempts = 0

print('Bruteforcing stegfile...')
for line in f:
    try:
        attempt = subprocess.check_output('steghide extract -sf %s -p %s' % (steg_path, line[:-1]), shell=True, stderr=subprocess.STDOUT)
        attempts += 1
        if 'could not extract' in attempt:
            if(current_time() - c_time > 5):
                print('... trying ~%d passwords/second.' % (attempts / 5))
                c_time = current_time()
                attempts = 0
            continue
        elif 'wrote extracted data' in attempt:
            print('pwd: %s\n\t... Success!' % line[:-1])
            print('Brutforce completed in %d seconds.' % (current_time() - s_time))
            break
    except subprocess.CalledProcessError as e:
        if 'could not extract' in e.output:
            attempts += 1
            if(current_time() - c_time > 20):
                print('... trying ~%d passwords/second.' % (attempts / 20))
                c_time = current_time()
                attempts = 0
            continue
        elif 'wrote extracted data' in e.output:
            print('pwd: %s\n\t... Success!' % line[:-1])
            print('Brutforce completed in %d seconds.' % (current_time() - s_time))
            break

f.close()
