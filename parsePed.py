import sys
import re
import argparse

parser = argparse.ArgumentParser(description='Recursively parse pedigrees and produce a three column pedigree [individual, mother, father]')
parser.add_argument("-f", '--file', type=str, help='input file name with two fields, line and pedigree')
parser.add_argument("-o", '--out', type=str, default = "result", help='output directory and file prefix')
parser.add_argument("-s", '--sep', type=str, default = ",", help='field separator for input file, default is a comma')
parser.add_argument("-t", '--outsep', type=str, default = "\t", help='field separator for output file, default is a tab')
parser.add_argument('-r', '--remove', nargs='*', help='patterns to be removed from pedigrees before parsing')
parser.add_argument('-m', '--missing', type=str, default = "", help='string to use for missing parents, default is empty string')
parser.add_argument('-n', '--nested', help='parse nested pedigrees')
args = parser.parse_args()

file = args.file
out = args.out
sep = args.sep
outsep = args.outsep
rmChar = args.remove
miss = args.missing


# file='ped.csv'
# out = 'testrun'
# sep = ","
# outsep = "\t"
# # rmChar = ["\"", ',F1', ', F1']
# rmChar = ["\"", ',\s*F1']
# miss = ""

def formatPed(ped):
	return re.sub("\s*/\s*", "/", ped)
# should we try to have exactly one space before and after each cross indicator?
	# ped = "A   / B//  C /3/D"
	# ped = re.sub("\s*/", " /", ped)
	# ped = re.sub("/\s*", "/ ", ped)
	# ped = re.sub("/ /", "//", ped) # this is pretty hacky
	# ped = re.sub("/ [0-9] /", "/[0-9]/", ped) 
		

def getLastCross(ped):
	crosses = re.findall(r'/([0-9])/', ped)
	crossNo = [ int(x) for x in crosses ]
	if len(crossNo):
		lastCross = "/" + str(max(crossNo)) + "/"
	else:
		if(re.search(r'//', ped)):
			lastCross = "//"
		elif(re.search(r'/', ped)):
			lastCross = "/"
		else:
			lastCross = ""
	return lastCross


def writePed(lineped, na = ""):
	parinfo = re.findall('\(.*?\)',lineped[1])
	if parinfo and args.nested:
		for j in parinfo:	
			# need to figure out which parent each nested pedigree comes from
			writePed(["parentX", j[1:(len(j)-1)]]) 
	pedNoPar = re.sub("[\[].*?[\]]", "", lineped[1])
	pedNoPar = re.sub("[\(\[].*?[\)\]]", "", lineped[1])
	lc = getLastCross(pedNoPar)
	if len(lc):
		mf = pedNoPar.split(lc)
		mf = [ x.strip() for x in mf ]
		# mf = [ re.sub("\s*/\s*", "/", x) for x in mf ]
		mf = [ formatPed(x) for x in mf ]
		mf.insert(0, lineped[0])
		# print(" ".join(mf))
		outfile.write(outsep.join(mf) + "\n")
		
		parisped = [ i for i, x in enumerate(mf[1:]) if re.search(r'/', x) ]
		if parisped:
			for j in [ mf[i+1] for i in parisped ]:	
				writePed([j, j])
	else:
		mf = [lineped[0], na, na]
		# print(" ".join(mf))
		outfile.write(outsep.join(mf) + "\n")


# l = "P992231A1-2-1 / LA01*425" + sep + "P992231A1-2-1 / LA01*425"
# l = "Patton // Patterson / Bizel /3/ 9346"
# l="VA16W-229,P992231A1-2-1 (Patton // Patterson / Bizel /3/ 9346) / LA01*425 (PION2571/Y91-6B) // Shirley (VA03W-409)"
# l="LA10042D-66-4,\"MD08-26-A10-3 / LA09175,F1(VA01-205/AGS2060)\""


outfile = open(out + ".ped", "w")

with open(file) as f:
	for l in f:
		for i in rmChar:
			l=re.sub(i,  "", l)
		l=l.split(sep)
		writePed(l)

outfile.close()

