import sys
import re
import argparse

# argument to pass to script
parser = argparse.ArgumentParser(description='Recursively parse pedigrees and produce a three column pedigree [individual, mother, father]')
parser.add_argument("-f", '--file', type=str, help='input file name with two fields, line and pedigree')
parser.add_argument("-o", '--out', type=str, default = "result", help='output directory and file prefix')
parser.add_argument("-s", '--sep', type=str, default = ",", help='field separator for input file, default is a comma')
parser.add_argument("-t", '--outsep', type=str, default = "\t", help='field separator for output file, default is a tab')
parser.add_argument('-r', '--remove', nargs='*', help='patterns to be removed from pedigrees before parsing')
parser.add_argument('-m', '--missing', type=str, default = "", help='string to use for missing parents, default is empty string')
parser.add_argument('-p', '--parents', help='print parents with no parents')
parser.add_argument('-n', '--nested', help='parse nested pedigrees')
args = parser.parse_args()

# assign arguments to shorter variable names
file = args.file
out = args.out
sep = args.sep
outsep = args.outsep
rmChar = args.remove
miss = args.missing


# file='ped.txt'
# out = 'testrun'
# sep = ","
# outsep = "\t"
# rmChar = ["\"", ',\s*F[0-9]']
# miss = ""

# function to clean up white space surrounding cross slashes
# "  / " -> "/"
def formatPed(ped):
	return re.sub("\s*/\s*", "/", ped)
# should we try to have exactly one space before and after each cross indicator?
	# ped = "A   / B//  C /3/D"
	# ped = re.sub("\s*/", " /", ped)
	# ped = re.sub("/\s*", "/ ", ped)
	# ped = re.sub("/ /", "//", ped) # this is pretty hacky
	# ped = re.sub("/ [0-9] /", "/[0-9]/", ped) 
		
# function to get the last cross made indicator
def getLastCross(ped):
	# find all crosses with integers (e.g.  '/3/' but not '/' or '//')
	crosses = re.findall(r'/([0-9])/', ped)
	# get cross number as integers
	crossNo = [ int(x) for x in crosses ]
	# if integers exist, get max integer
	if len(crossNo):
		lastCross = "/" + str(max(crossNo)) + "/"	
	else:
	# else, find last cross character/pattern 
		# look for '//''
		if(re.search(r'//', ped)):
			lastCross = "//"
		# if no '//', look for '/'
		elif(re.search(r'/', ped)):
			lastCross = "/"
		# if no '/', return empty
		else:
			lastCross = ""
	return lastCross


def writePed(lineped, na = ""):
	##########################################################################################
	# parse nested pedigrees in this section
	# move this to the end?
	# get nested pedigrees (i.e. parent pedigree / information)
	parinfo = re.findall('\(.*?\)|\[.*?\]',lineped[1])

	# process parent pedigrees, using recursion
	if parinfo and args.nested:
		for j in parinfo:	
			# need to figure out which parent each nested pedigree comes from
			writePed(["parentX", j[1:(len(j)-1)]]) 
	# how do we make sure that nested pedigrees are paired with the proper individual?
	##########################################################################################
	# remove nested pedigrees
	pedNoPar = re.sub("[\[].*?[\]]", "", lineped[1])
	pedNoPar = re.sub("[\(\[].*?[\)\]]", "", pedNoPar)
	# find last cross character/pattern
	lc = getLastCross(pedNoPar)
	if len(lc):
		# split on last cross character/pattern
		mf = pedNoPar.split(lc)
		# clean up strings
		mf = [ x.strip() for x in mf ]
		mf = [ formatPed(i) for i in mf ]
		# add line name back in as first element
		mf.insert(0, lineped[0])
		# then write line, mother, father
		outfile.write(outsep.join(mf) + "\n")
		# if parent names are pedigrees themselves, parse them
		parisped = [ i for i, x in enumerate(mf[1:]) if re.search(r'/', x) ]
		if parisped:
			for j in [ mf[i+1] for i in parisped ]:	
				writePed([j, j])
		# if -p option, then write each (simple) parent as its own line
		if args.parents:
			# check which parent names are not pedigrees
			parisnotped = [x for x in [0,1] if x not in parisped]
			# for each non pedigree parent, write parent name as own line, with empty mother father
			for j in [ mf[j+1] for j in parisnotped ]:
				par = [j, na, na]
				# print(outsep.join(par) + "\n")
				outfile.write(outsep.join(par) + "\n")
	else:
		# if no last cross ,just write parent
		mf = [lineped[0], na, na]
		outfile.write(outsep.join(mf) + "\n")

# examples:
# l = "P992231A1-2-1 / LA01*425" + sep + "P992231A1-2-1 / LA01*425"
# l = "line,Patton // Patterson / Bizel /3/ 9346"
# l="VA16W-229,P992231A1-2-1 (Patton // Patterson / Bizel /3/ 9346) / LA01*425 (PION2571/Y91-6B) // Shirley (VA03W-409)"
# l="LA10042D-66-4,\"MD08-26-A10-3 / LA09175,F1(VA01-205/AGS2060)\""
# l="VA20W-4,VA08MAS-369 [McCORMICK(VA98W-591)/ GA881130LE5] / GA031134-10E29 [Pioneer26R38/ 2*GA961565-2E46] // Hilliard (VA11W-108), F7"
# l="VA20W-16,VA11MAS-7520-2-3-255 [Oglethorpe (GA951231-4E25) / SS8404//Shirley(VA03W-409)] / Jamestown (VA02W-370), F6"

# l="VA16W-229,P992231A1-2-1 (Patton // Patterson / Bizel /3/ 9346) / LA01*425 (PION2571/Y91-6B) // Shirley (VA03W-409)"


# l="VA16W-229,P992231A1-2-1 / LA01*425 (PION2571/Y91-6B) // Shirley (VA03W-409)"
# l="VA20W-16, VA11MAS-7520-2-3-255  / Jamestown"
# "VA11MAS-7520-2-3-255, Oglethorpe (GA951231-4E25) / SS8404//Shirley(VA03W-409)"
# l="Hilliard (VA12345)"
# l="VA11MAS-7520-2-3-255,Oglethorpe (GA951231-4E25) / SS8404//Shirley(VA03W-409)"

outfile = open(out + ".ped", "w")

with open(file) as f:
	for l in f:
		for i in rmChar:
			l=re.sub(i,  "", l)

		l=l.split(sep)
		writePed(l, na = miss)

outfile.close()

