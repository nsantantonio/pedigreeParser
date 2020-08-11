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

# function to clean up white space surrounding cross slashes
# "  / " -> "/"

# checkParen is from https://www.geeksforgeeks.org/check-for-balanced-parentheses-in-python/
# balanced parentheses in an expression 
  
# Function to check parentheses: This doesnt work unless its all parentheses.
def checkParen(myStr):
	open_list = ["[","{","("]
	close_list = ["]","}",")"]
	stack = []
	for i in myStr:
	    if i in open_list:
	        stack.append(i)
	    elif i in close_list:
	        pos = close_list.index(i)
	        if ((len(stack) > 0) and (open_list[pos] == stack[len(stack)-1])):
	            stack.pop()
	    else:
	        return "Unbalanced"
	if len(stack) == 0:
	    return "Balanced"
	else:
	    return "Unbalanced"

# checkParen("(A)[B((D))]")
# checkParen("()[(())]")

def formatPed(ped):
	return re.sub("\s*/\s*", "/", ped)
# should we try to have exactly one space before and after each cross indicator?

# remove_text_inside_brackets from https://stackoverflow.com/questions/14596884/remove-text-between-and-in-python
def remove_text_inside_brackets(text, brackets="()[]"):
    count = [0] * (len(brackets) // 2) # count open/close brackets
    saved_chars = []
    for character in text:
        for i, b in enumerate(brackets):
            if character == b: # found bracket
                kind, is_close = divmod(i, 2)
                count[kind] += (-1)**is_close # `+1`: open, `-1`: close
                if count[kind] < 0: # unbalanced bracket
                    count[kind] = 0  # keep it
                else:  # found bracket to remove
                    break
        else: # character is not a [balanced] bracket
            if not any(count): # outside brackets
                saved_chars.append(character)
    return ''.join(saved_chars)



def formatBC(ped):
	crossOrder = ["/", "//", ] + ["/" + str(i) + "/" for i in range(3, 10)]
	lc = getLastCross(ped)
	nBCleft = [int(x) for x in re.findall(r'\*([0-9])/', ped) ]
	nBCright = [int(x) for x in re.findall(r'/([0-9])\*', ped) ]
	if len(nBCleft):
		lped = [ped]
	# for i in nBCleft[::-1]: # does this really need to be reversed?
		for i in nBCleft: # does this really need to be reversed?
			if len(lped) == 1:
				lped = lped[0].split(r"*" + str(i))
			else:
				lped = [ lped.split(i) for x in lped ]
			repPar = [ bc for bc in [lped[0]] for j in range(i) ]
			nextCross = [j+1 for j, x in enumerate(crossOrder) if lc == x][0] # NOte: [0] doesnt allow more than 1 backcross!
			cross = crossOrder[nextCross:nextCross+nBCleft[0]-1]
			cross.append("")
		lped[0] = ''.join([j + k for j , k in zip(repPar, cross)])
		ped = ''.join(lped)
	if len(nBCright):
		rped = [ped]
	# for i in nBCleft[::-1]: # does this really need to be reversed?
		for i in nBCright: # does this really need to be reversed?
			if len(rped) == 1:
				rped = rped[0].split(str(i) + "*")
			else:
				rped = [ rped.split(i) for x in rped ]
			rpedi = len(rped) -1
			repPar = [ bc for bc in [rped[rpedi]] for j in range(i) ]
			nextCross = [j+1 for j, x in enumerate(crossOrder) if lc == x][0] # NOte: [0] doesnt allow more than 1 backcross!
			cross = crossOrder[nextCross:nextCross+nBCright[0]-1]
			cross.append("")
		rped[rpedi] = ''.join([j + k for j , k in zip(repPar, cross)])
		ped = ''.join(rped)
	return(ped)


# formatBC("AAA/3*BB")
# formatBC("AAA*3/BB")
# formatBC("D/A*3/3/B//C")
# formatBC("AAA/3*BB")
# 
# ped = "AAA/3*BB"
# ped = "AAA*3/BB"

# ped = "A*2//B/C"
# "A/3/A//B/C"
# ped = "A/*2B/C"
# "A/3/A//B/C"
# ped = "D/A*3/3/B//C"
# "D/A*3/3/B//C"


# "D/A*3/3/B//C"

		
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

# def stripNested(x):
# 	noNest = re.sub("[\[].*?[\]]", "", x)
# 	noNest = re.sub("[\(\[].*?[\)\]]", "", noNest)
# 	return noNest

def stripNested(x):
	return(remove_text_inside_brackets(x))
	# 	return noNest

def getShortMatch(p1, p2, ped):
	p1pos = []
	p2pos = []
	for match in re.finditer(p1, ped):
		p1pos.append(match.span())
	p1start = [x[0] for x in p1pos]
	p1end = [x[1] for x in p1pos]
	for match in re.finditer(p2, ped):
		p2pos.append(match.span())
	p2start = [x[0] for x in p2pos]
	p2end = [x[1] for x in p2pos]
	i1 = p1start[0]
	i2 = p2end[0]
	diff = abs(p1start[0] - p2end[0])
	for i in p1start:
		for j in p2end:
			diffi = abs(i - j)
			if diff > diffi:
				i1 = i
				i2 = j
				diff = diffi
	return [i1,i2]



def writePed(lineped, na = ""):
	# remove nested pedigrees
	# pedNoPar = re.sub("[\[].*?[\]]", "", lineped[1])
	# pedNoPar = re.sub("[\(\[].*?[\)\]]", "", pedNoPar)
	pednoast = re.sub(r'\*', '\*', lineped[1])
	stripNested(pednoast)
	pedNoPar = stripNested(lineped[1])
	# print("pedigrees without parents:")
	# print(pedNoPar)
	# find last cross character/pattern
	lc = getLastCross(pedNoPar)
	# print("last cross char:")
	# print(lc)
	if len(lc):
		# split on last cross character/pattern
		mf = pedNoPar.split(lc)
		# clean up strings
		mf = [ x.strip() for x in mf ]
		mf = [ formatPed(i) for i in mf ]
		
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
				# parent = stripNested(parPed[0])
				parents = [ stripNested(i) for i in parPed ]
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
					
					pindex = getShortMatch(p1, pl, lineped[1])
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
					parPed = p.split(getLastCross(p))
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

