#!/usr/bin/env python
#---change log
#---date                author          descption
#---2016-01-21 18:07    zp8613			output a sine wave to stdout
import time,sys,random,math
i = 1
while 1:
    i=i+1
    sys.stdout.writelines(str(math.sin(2*math.pi*i/300.0)*0.5+0.5)+'\n')
    if i > 200:
        i=0
    sys.stdout.flush()
    time.sleep(0.1)
