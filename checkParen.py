# checkParen is from https://www.geeksforgeeks.org/check-for-balanced-parentheses-in-python/
# balanced parentheses in an expression   
# Function to check parentheses: This doesnt work unless its all parentheses/brackets.
# need functionality to determine if brackets are balanced regardelss of text in between
# should kick out a warning, and return a boolian indicating if the pedigree is malformed
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

# checkParen("()[(())]") # works
# checkParen("(A)[B((D))]") # doesnt work