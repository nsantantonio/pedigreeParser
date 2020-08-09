import sys
import re
import argparse
import time

startTime = time.time()

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
parser.add_argument('-S', '--skip', help='skip n lines', type = int, default = 0)
args = parser.parse_args()

# assign arguments to shorter variable names
file = args.file
out = args.out
sep = args.sep
outsep = args.outsep
rmChar = args.remove
miss = args.missing
skip = args.skip


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

def stripNested(x):
	noNest = re.sub("[\[].*?[\]]", "", x)
	noNest = re.sub("[\(\[].*?[\)\]]", "", noNest)
	return noNest

def writePed(lineped, na = ""):
	# remove nested pedigrees
	# pedNoPar = re.sub("[\[].*?[\]]", "", lineped[1])
	# pedNoPar = re.sub("[\(\[].*?[\)\]]", "", pedNoPar)
	pedNoPar = stripNested(lineped[1])
	print("pedigrees without parents:")
	print(pedNoPar)
	# find last cross character/pattern
	lc = getLastCross(pedNoPar)
	print("last cross char:")
	print(lc)
	if len(lc):
		# split on last cross character/pattern
		mf = pedNoPar.split(lc)
		# clean up strings
		mf = [ x.strip() for x in mf ]
		mf = [ formatPed(i) for i in mf ]
		
		# add line name back in as first element
		mf.insert(0, lineped[0])
		print("pedigree line:")
		print(mf)
		# then write line, mother, father
		outfile.write(outsep.join(mf) + "\n")

		# check which parent names are pedigrees
		parisped = [ i for i, x in enumerate(mf[1:]) if re.search(r'/', x) ]
		# get which parent names are NOT pedigrees
		parisnotped = [ x for x in [0,1] if x not in parisped ]
		
		print(parisnotped)
		for p in parisnotped:
			# need nested list of all parents, then flatten and assign index to nested peds
			print("This is what IM going to search for")
			print(mf[p+1] + '\s*\(.*?\)|' + mf[p+1] + '\s*\[.*?\]')
			parPed = re.findall(mf[p+1] + '\s*\(.*?\)|' + mf[p+1] + '\s*\[.*?\]', lineped[1])
			print("This is where the parent pedigree is:")
			print(parPed)

			if len(parPed):
				# parent = stripNested(parPed[0])
				parents = [ stripNested(i) for i in parPed ]
				parents = [ i.strip() for i in parents ]
				print("these are the parents after:")
				print(parents)
				if len(parents) > 1:	
					print("WARNING! More than 1 match in parents!")
				if len(parPed) > 1:	
					print("more than 1 match in parent")
					parPed = list(set(parPed))
					if len(parPed) > 1:	
						print("WARNING! More than 1 match in pedigree!")

				print("here is the nested pedigree that needs to be parsed")
				print(parPed)
				if re.search(r'\(|\)|\[|\]', parPed[0]):
					parinfo = re.findall('\(.*?\)|\[.*?\]', parPed[0])[0]
					print("this nested pedigree will be parsed:")
					print(parinfo)
					parlineped = [parents[0], parinfo[1:len(parinfo)-1]]
					print("this is input to recursive call:")
					print(parlineped)
					if re.search(r'/', parlineped[1]):
						writePed(parlineped)
					else:
						if args.parents:
							print("nested is not a pedigree")
							alias = [parlineped[0], na, na, parlineped[1]]
							print("here is the alias:")
							print(alias)
							outfile.write(outsep.join(alias) + "\n")
				# else:

		# for each non pedigree parent, write parent name as own line, with empty mother father
		for j in [ mf[j+1] for j in parisnotped ]:
			print("parent " + str(j) + " is NOT a pedigree!")
			npp = [j, na, na]
			# print(outsep.join(par) + "\n")
			if args.parents:
				outfile.write(outsep.join(npp) + "\n")
		# if parent names are pedigrees themselves, parse them
		if parisped:
			for j in [ mf[i+1] for i in parisped ]:	
				print(j)
				psplit = j.split("/")
				p1 = psplit[0]
				pl = psplit[len(psplit)-1]
				print("first: " + p1)
				print("last: " + pl)
				print("Gonna look for this now")
				print(p1 + '.*' + pl + '\s*\(.*?\)|' + p1 + '.*' + pl + '\s*\[.*?\]')
				# print(p1 + '.*' + pl + '\s*\(.*?\)')
				parPed = re.findall(p1 + '.*' + pl + '\s*\(.*?\)|' + p1 + '.*' + pl + '\s*\[.*?\]', lineped[1])
				# cant find becuase nested sep by /
				if not len(parPed):
					parPed = re.findall(p1 + '.*' + pl, lineped[1])
				if len(parPed) > 1:
					print("more than 1 match in parent")
					parPed = list(set(parPed))
					if len(parPed) > 1:	
						# print("WARNING! More than 1 match in pedigree!")
						print("WARNING! multiple matches found! errors may occur!")
				print("parent " + j + " has nested pedigree:")
				print(parPed)
				# print("parent " + j + " is pedigree:")

				writePed([j, parPed[0]])
		# if -p option, then write each (simple) parent as its own line
	else:
		print("there is no cross here, printing parent:")
		# if no last cross ,just write parent
		mf = [lineped[0], na, na]
		print(mf)
		outfile.write(outsep.join(mf) + "\n")
	##########################################################################################
	# parse nested pedigrees in this section
	# move this to the end?
	# get nested pedigrees (i.e. parent pedigree / information)
	# parinfo = re.findall('\(.*?\)|\[.*?\]', lineped[1])
	# print(parinfo)
	# # process parent pedigrees, using recursion
	# if parinfo and args.nested:
	# 	for j in parinfo:	
	# 		# need to figure out which parent each nested pedigree comes from
	# 		writePed(["parentX", j[1:(len(j)-1)]]) 
	# how do we make sure that nested pedigrees are paired with the proper individual?
	##########################################################################################
	# return [pcnt, ]
# examples:
# l = "P992231A1-2-1 / LA01*425" + sep + "P992231A1-2-1 / LA01*425"
# l = "line,Patton // Patterson / Bizel /3/ 9346"
# l="VA16W-229,P992231A1-2-1 (Patton // Patterson / Bizel /3/ 9346) / LA01*425 (PION2571/Y91-6B) // Shirley (VA03W-409)"
# l="LA10042D-66-4,\"MD08-26-A10-3 / LA09175,F1(VA01-205/AGS2060)\""
# l="VA20W-4,VA08MAS-369 [McCORMICK(VA98W-591)/ GA881130LE5] / GA031134-10E29 [Pioneer26R38/ 2*GA961565-2E46] // Hilliard (VA11W-108), F7"
# l="VA20W-16,VA11MAS-7520-2-3-255 [Oglethorpe (GA951231-4E25) / SS8404//Shirley(VA03W-409)] / Jamestown (VA02W-370), F6"
# lineped=["VA20W-16","VA11MAS-7520-2-3-255 [Oglethorpe (GA951231-4E25) / SS8404//Shirley(VA03W-409)] / Jamestown (VA02W-370)"]
# j = "Oglethorpe/SS8404"
# l="VA16W-229,P992231A1-2-1 (Patton // Patterson / Bizel /3/ 9346) / LA01*425 (PION2571/Y91-6B) // Shirley (VA03W-409)"


# l="VA16W-229,P992231A1-2-1 / LA01*425 (PION2571/Y91-6B) // Shirley (VA03W-409)"
# l="VA20W-16, VA11MAS-7520-2-3-255  / Jamestown"
# "VA11MAS-7520-2-3-255, Oglethorpe (GA951231-4E25) / SS8404//Shirley(VA03W-409)"
# l="Hilliard (VA12345)"
# l="VA11MAS-7520-2-3-255,Oglethorpe (GA951231-4E25) / SS8404//Shirley(VA03W-409)"

outfile = open(out + ".ped", "w")

cnt=0
with open(file) as f:
	for l in f:
		cnt += 1
		if cnt > skip:	
			if rmChar is not None:
				for i in rmChar:
					l=re.sub(i,  "", l)
			l=l.split(sep)
			writePed(l, na = miss)
outfile.close()


secs = time.time() - startTime
if secs > 3600:
	t = round(secs / 3600, 1)
	print("Parsed " + str(cnt) + " pedigrees in %s hours" % (t))
elif secs > 60:
	t = round(secs / 60, 1)
	print("Parsed " + str(cnt) + " pedigrees in %s minutes" % (t))
else:
	t = round(secs, 3)
	print("Parsed " + str(cnt) + " pedigrees in %s seconds" % (t))

