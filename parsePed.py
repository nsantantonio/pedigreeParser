
# import standard libraries
import sys
import re
import argparse
import time

startTime = time.time()

# Import custom libraries, we can collapse these into one library once weve finished. 
import getShortMatch
import stripNested
import getLastCross
import formatBC
import formatPed
import checkParen




# argument to pass to script
parser = argparse.ArgumentParser(description='Recursively parse pedigrees and produce a three column pedigree [individual, mother, father]')
parser.add_argument("-f", '--file', type=str, help='input file name with two fields, line and pedigree')
parser.add_argument("-o", '--out', type=str, default = "result", help='output directory and file prefix')
parser.add_argument("-s", '--sep', type=str, default = ",", help='field separator for input file, default is a comma')
parser.add_argument("-t", '--outsep', type=str, default = "\t", help='field separator for output file, default is a tab')
parser.add_argument('-r', '--remove', nargs='*', help='patterns to be removed from pedigrees before parsing')
parser.add_argument('-m', '--missing', type=str, default = "", help='string to use for missing parents, default is empty string')
parser.add_argument('-p', '--parents', action = 'store_true', help='print parents with no parents?')
parser.add_argument('-n', '--nested', action = 'store_true', help='parse nested pedigrees')
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

# should we try to have exactly one space before and after each cross indicator?


def writePed(lineped, na = ""):
	# remove nested pedigrees
	# pedNoPar = re.sub("[\[].*?[\]]", "", lineped[1])
	# pedNoPar = re.sub("[\(\[].*?[\)\]]", "", pedNoPar)
	pednoast = re.sub(r'\*', '\*', lineped[1])
	# stripNested.rmInParen(pednoast)
	pedNoPar = stripNested.rmInParen(lineped[1])
	# print("pedigrees without parents:")
	# print(pedNoPar)
	# find last cross character/pattern
	lc = getLastCross.getLastCross(pedNoPar)
	# print("last cross char:")
	# print(lc)
	if len(lc):
		# split on last cross character/pattern
		mf = pedNoPar.split(lc)
		# clean up strings
		mf = [ x.strip() for x in mf ]
		mf = [ formatPed.formatPed(i) for i in mf ]
		
		# add line name back in as first element
		mf.insert(0, lineped[0])
		# print("pedigree line:")
		# print(mf)
		# then write line, mother, father
		outfile.write(outsep.join(mf) + "\n")

		# check which parent names are pedigrees
		parisped = [ i for i, x in enumerate(mf[1:]) if re.search(r'/', x) ]
		# get which parent names are NOT pedigrees
		parisnotped = [ x for x in [0,1] if x not in parisped ]
		
		# print(parisnotped)
		for p in parisnotped:
			# need nested list of all parents, then flatten and assign index to nested peds
			# print("This is what IM going to search for")
			# print(mf[p+1] + '\s*\(.*?\)|' + mf[p+1] + '\s*\[.*?\]')
			parPed = re.findall(mf[p+1] + '\s*\(.*?\)|' + mf[p+1] + '\s*\[.*?\]', lineped[1])
			# print("This is where the parent pedigree is:")
			# print(parPed)

			if len(parPed):
				# parent = stripNested.rmInParen(parPed[0])
				parents = [ stripNested.rmInParen(i) for i in parPed ]
				parents = [ i.strip() for i in parents ]
				# print("these are the parents after:")
				# print(parents)
				if len(parents) > 1:	
					print("WARNING! More than 1 match in parents!")
				if len(parPed) > 1:	
					print("more than 1 match in parped")
					parPed = list(set(parPed))
					if len(parPed) > 1:	
						print("WARNING! More than 1 match in pedigree!")

				# print("here is the nested pedigree that needs to be parsed")
				# print(parPed)
				if args.nested and re.search(r'\(|\)|\[|\]', parPed[0]):
					parinfo = re.findall('\(.*?\)|\[.*?\]', parPed[0])[0]
					# print("this nested pedigree will be parsed:")
					# print(parinfo)
					parlineped = [parents[0], parinfo[1:len(parinfo)-1]]
					# print("this is input to recursive call:")
					# print(parlineped)
					if re.search(r'/', parlineped[1]):
						writePed(parlineped)
					else:
						if args.parents:
							# print("nested is not a pedigree")
							alias = [parlineped[0], na, na, parlineped[1]]
							# print("here is the alias:")
							# print(alias)
							outfile.write(outsep.join(alias) + "\n")
				# else:

		# for each non pedigree parent, write parent name as own line, with empty mother father
		for j in [ mf[j+1] for j in parisnotped ]:
			# print("parent " + str(j) + " is NOT a pedigree!")
			npp = [j, na, na]
			# print(outsep.join(par) + "\n")
			if args.parents:
				outfile.write(outsep.join(npp) + "\n")
		# if parent names are pedigrees themselves, parse them
		if parisped:
			# for j in [ mf[i+1] for i in parisped ]:	
			for j in parisped:	
				p = mf[j+1]
				if re.search(r'\(|\)|\[|\]', p):
					psplit = p.split("/")
					p1 = re.sub(r'\*', '\*', psplit[0])
					pl = re.sub(r'\*', '\*', psplit[len(psplit)-1])

					# print("first: " + p1)
					# print("last: " + pl)
					# print("Gonna look for this now")
					# print(p1 + '.*' + pl + '\s*\(.*?\)|' + p1 + '.*' + pl + '\s*\[.*?\]')
					# print(p1 + '.*' + pl + '\s*\(.*?\)')

						# this is kinda hacky. Matches first match, or truncated begining to grab the second match, by selecting the shortest of 2 matches
						# pindex = getShortMatch(p1, pl, lineped[1])
					
					pindex = getShortMatch.getShortMatch(p1, pl, lineped[1])
					parPed = re.findall(p1 + '.*?' + pl + '\s*\(.*?\)|' + p1 + '.*' + pl + '\s*\[.*?\]', lineped[1][pindex[0]:])
					# cant find because nested sep by /
					if not len(parPed):
						# if the same parent is used twice, then this breaks cause it grabs 
						# good for first match (lazy) , problem for second. I.e. 'abc / xyz // xyz / def' returns 'abc / xyz' for first, but 'xyz // xyz / def' for second... FML					
						parPed = re.findall(p1 + '.*?' + pl, lineped[1][pindex[0]:])

					if len(parPed) > 1:
						print("2: more than 1 match in parent")
						parPed = list(set(parPed))
						if len(parPed) > 1:	
							# print("WARNING! More than 1 match in pedigree!")
							print("2: WARNING! multiple matches found! errors may occur!")
					# print("parent " + mf[j+1] + " has nested pedigree:")
					# print(parPed)
					# print("parent " + j + " is pedigree:")
				else:
					parPed = p.split(getLastCross.getLastCross(p))
				# print(mf)
				writePed([p, parPed[0]])
		# if -p option, then write each (simple) parent as its own line
	else:
		# print("there is no cross here, printing parent:")
		# if no last cross ,just write parent
		if args.parents:
			mf = [lineped[0], na, na]
			# print(mf)
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

# l = "VA20FHB-25,M10-1615 (IL99-15867/M03-3002) / VA12W-26 [MPV57 (VA97W-24)/M99*3098 (TX85-264/VA88-52-69) // '3434' (VA03W-434)]"
# l = "VA20FHB-25,M10-1615 (IL99-15867/M03-3002) / VA12W-26 [MPV57 (VA97W-24)/M99*3098 (TX85-264/VA88-52-69) // '3434' (VA03W-434)]"
# lineped = ['VA12W-26', "MPV57 (VA97W-24)/M99*3098 (TX85-264/VA88-52-69) // '3434' (VA03W-434)"]
# l = "VA20FHB-29,P05222A1-7 [99840/INW0304//INW0304/ INW0316] / Branson // VA12W-102 [VA03W-436 (ROANE/ CK9835// VA96-54-270) / IL99-15867 (IL93-2879/ P881705A-1-X-60)], F6"

# lineped=['P05222A1-7/Branson', 'P05222A1-7 [99840/INW0304//INW0304/ INW0316] / Branson']
# lineped=['P05222A1-7', '99840/INW0304//INW0304/ INW0316']
# lineped=['P05222A1-7', '99840/INW0304 (E) //INW0304[A/B(C)]/ INW0316 [X(Y/Z)]']

# l="VA20W-49","UX1334-4 [Shirley/3/Shirley(VA03W-409)/ Sr26recA//Shirley] / VA12FHB-34 [GA991109-4-1-3 (Ernie/Pion2684// GA901146)/PIONEER26R15], F6"

# lineped=["UX1334-4", "Shirley/3/Shirley(VA03W-409)/ Sr26recA//Shirley"] 
# lineped=["UX1347-1", "McCormick*2//(IL00-8061// TA5605 (Lr58)/ McCormick)/(SS8641*2// McCormick/KS92WGRC15(Lr21))"]



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
			# print(l)
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

