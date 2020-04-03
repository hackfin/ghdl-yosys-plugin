import sys

import random

def generate(f, n):
	for i in range(n):
		f.write("%04x\n" % random.randint(0, 0xffff))

f = open(sys.argv[1], "w")
generate(f, 256)
f.close()
