import re
import fileinput
import os
import operator
#####################Scanner####################
def scanner ():
	file = input ( "Type full input file name here and hit enter (case sensitive): " )
	cwd = os.path.dirname ( os.path.abspath( file ) )

	# outputs list of tokens into a log for error checking
	with open ( file ) as fin:
		output_name = cwd + "\\scanner_output.txt"
		with open ( output_name , "a" ) as fout:
			for line in fin:
				
				fin_lines = line.split ()

				for x in fin_lines:
					temp = ""
					prev = ""
					# regex to look for any char that's not a letter, num, or -+*|();:=/ symbols
					invalid_char = re.search ( "[^a-zA-Z0-9-+*|();:=/]", x ) 
					if invalid_char:
						fout.write ( x + "|ERROR, INVALID TOKEN\n" )
						print ( "Error Occured, Program Shutting Down" )
						sys.exit ( 0 )

					# looks to see if word starts with num or word
					num_check = re.search ( "^\d", x ) 
					word_check = re.search ( "^[a-zA-Z]", x )
					num_first = False
					word_first = False
					eqtemp = False
					if num_check:
						num_first = True
					
					if word_check:
						word_first = True
					
					# checks for nums, chars, and symbols, and uses it to categorize the invidual code
					for elements in x:
						match1 = re.search ( "\d", elements )
						match2 = re.search ( "[a-zA-Z]", elements )
						match3 = re.search ( "^(\+|\-|\*|\||\(|\)|\:|\=|/|;)$", elements )
					
						if match1:
							if ( prev == "p" ):
								num_first = True
							temp += elements
							prev = "d"
						
						# variables names cannot have a char proceed a num in requirements
						if match2:
							if ( prev == "d" and num_first == True ):
								fout.write ( x + "|ERROR, INVALID TOKEN\n" )
								print ( "Error Occurred, Program Shutting Down")
								sys.exit ( 0 )
							elif ( prev == "p" ):
								word_first = True
							temp += elements
							prev = "w"
					
						if match3:
							if ( word_first == True ):
								keyword_check = re.search ( "^(?i)(if|then|else|endif|while|do|endwhile|skip)$", temp )
								if keyword_check:
									fout.write ( temp + "|KEYWORD\n" )
								else:
									fout.write ( temp + "|IDENTIFIER\n" )
							elif ( num_first == True ):
								fout.write ( temp + "|NUMBER\n" )
							if ( elements == ":" ):
								eqtemp = True
								continue
							if ( elements == "=" ):
									if ( eqtemp == True ):
										eqtemp = False
										num_first = False
										word_first = False	
										temp = ""
										prev = "p"
										fout.write ( ":=" + "|PUNCTUATION\n" )
										continue
									else:
										fout.write ( "=" + "|ERROR, INVALID TOKEN" )	
							num_first = False
							word_first = False	
							temp = ""
							prev = "p"
							fout.write ( elements + "|PUNCTUATION\n" )
					
					if ( word_first == True ):
						keyword_check = re.search ( "^(?i)(if|then|else|endif|while|do|endwhile|skip)$", temp )
						if keyword_check:
							fout.write ( temp + "|KEYWORD\n" )
						else:
							fout.write ( temp + "|IDENTIFIER\n" )
					elif ( num_first == True ):
						fout.write ( temp + "|NUMBER\n" )
	return cwd
########################Parser###############################
class Tree:
	def __init__( self,left,mid,right,data,ttype ):
		self.left = left
		self.mid = mid
		self.right = right
		self.data = data
		self.ttype = ttype

# Grammar functions to assemble the list of tokens to a tree
def parse_statement ( tokens, tree ):
	global index
	node = parse_basestatement ( tokens, tree )
	# try except pass to not error out on end of token list
	try:
		while ( ( tokens[ index ][ 0 ] ) == ";" ):
			index += 1
			node2 = parse_basestatement ( tokens, tree )
		
			node = Tree ( node, None, node2, ";", "PUNCTUATION" )
	except:
		pass
	return node

def parse_basestatement ( tokens, tree ):
	global index
	if ( ( tokens[ index ][ 0 ] ) == "if" ):
		node = parse_if ( tokens, tree )
	elif ( ( tokens[ index ][ 0 ] ) == "while" ):
		node = parse_while ( tokens, tree )
	elif ( ( tokens[ index ][ 0 ] ) == "skip" ):
		node = Tree ( None, None, None, "skip", "KEYWORD" )
		index += 1
	else:
		node = parse_assignment ( tokens, tree )
	
	return node

def parse_assignment ( tokens, tree ):
	global index
	node1 = Tree ( None, None, None, ( tokens[ index ][ 0 ] ), "IDENTIFIER" )
	index += 2
	node2 = parse_exp ( tokens, tree )
	
	return Tree ( node1, None, node2, ":=", "PUNCTUATION" )

def parse_if ( tokens, tree ):
	global index
	index += 1
	express = parse_exp ( tokens, tree )
	
	index += 1
	then_stat = parse_statement ( tokens, tree )
	
	index += 1
	else_stat = parse_statement ( tokens, tree )
	
	index += 1 
	return Tree ( express, then_stat, else_stat, "if-statement", "" )

def parse_while ( tokens, tree ):
	global index
	index += 1
	while_cond = parse_exp ( tokens, tree )
	
	index += 1
	do_state = parse_statement ( tokens, tree )
	
	index += 1
	return Tree ( while_cond, None, do_state, "while-loop", "" )

def parse_exp ( tokens , tree ):
	global index
	term = parse_term ( tokens, tree )
	
	while ( tokens [ index ][ 0 ] == "+" ):
		index += 1
		term2 = parse_term ( tokens, tree )
	
		term = Tree ( term, None, term2, "+", "PUNCTUATION" )
	return term

def parse_term ( tokens , tree ):
	global index
	factor = parse_factor ( tokens, tree )
	
	while ( tokens [ index ][ 0 ] == "-" ):
		index += 1
		factor2 = parse_factor ( tokens, tree )
	
		factor = Tree ( factor, None, factor2, "-", "PUNCTUATION" )
	return factor

def parse_factor ( tokens , tree ):
	global index
	piece = parse_piece ( tokens, tree )
	
	while ( tokens [ index ][ 0 ] == "/" ):
		index += 1
		piece2 = parse_term ( tokens, tree )
	
		piece =  Tree ( piece, None, piece2, "/", "PUNCTUATION" )
	return piece

def parse_piece ( tokens, tree ):
	global index
	element = parse_element ( tokens, tree )
	
	while ( tokens [ index ][ 0 ] == "*" ):
		index += 1
		element2 = parse_element ( tokens, tree )
	
		element = Tree ( element, None, element2, "*", "PUNCTUATION" )
	return element

def parse_element ( tokens, tree ):
	global index
	if ( tokens [ index ][ 0 ] == "(" ):
		index += 1
		node = parse_exp ( tokens, tree )
		index += 1
	elif ( tokens [ index ][ 1 ] == "NUMBER" ):
		node = Tree ( None, None, None, ( tokens[ index ][ 0 ] ), "NUMBER" )
		index += 1
	else:
		node = Tree ( None,None, None, ( tokens[ index ][ 0 ] ), "IDENTIFIER" )
		index += 1
	
	return node

# takes assembled tree and put into output log for error checking
def parser_output ( tree, path ):
	output_name = path + "\\parser_output.txt"
	with open ( output_name, "a" ) as fout:
		tabs = ""
		traversal ( tree, tabs, fout )

def traversal ( node, tabs, file ):
	try:
		if node.data:
			file.write ( tabs + node.ttype + " " + node.data + "\n" )
			tabs += "\t"
			traversal ( node.left, tabs, file )

			traversal ( node.mid, tabs, file )
			
			traversal ( node.right, tabs, file )
	except:
		pass
# main parser function that calls the tree creation functions
def parser ( path ):
	tree = Tree ( None,None,None,None,None )
	tkarr = []
	file = path + "scanner_output.txt"
	with open ( file ) as fin:
		for line in fin:
			fin_lines = line.split ( "|" )
			fin_lines[1] = fin_lines[1].strip ( '\n' )
			temp = ( fin_lines[0], fin_lines[1] )
			tkarr.append ( temp )
	tree = parse_statement ( tkarr, tree )
	parser_output ( tree, path )
	return tree
####################Evaluator###########################
def evaluator ( tree, path ):
	global memory
	evaluate ( tree )
	file = path + "\\evaluator_output.txt"
	with open ( file, "a" ) as fout:
		for element in memory:
			fout.write ( element + " : " + str ( memory [ element ] ) + "\n" )
	return

def evaluate ( tree ):
	if tree is not None:
		if tree.data:
			if tree.data == ';':
				evaluate ( tree.left )
				evaluate ( tree.right )
	
			else:	
				# dict of string to function
				next_func = { 
				':=' : assignment,
				'if-statement' : ifstatement,
				'while-loop' : whileloop,
				'skip' : do_nothing,
				'+' : exp,
				'-' : exp,
				'*' : exp,
				'/' : exp,
				}
				next_func [ tree.data ] ( tree )
	return

def assignment ( tree ):
	global memory
	new_value = exp ( tree.right )
	memory [ tree.left.data ] = int ( new_value )
	return

def ifstatement ( tree ):
	condition = exp ( tree.left )
	if condition > 0:
		evaluate ( tree.mid )

	else:
		evaluaute ( tree.right )
	return

def whileloop ( tree ):
	condition = exp ( tree.left )

	while condition > 0:
		evaluate ( tree.right )
		condition = exp ( tree.left )
	return

def exp ( tree ):
	global memory
	if ( tree.ttype == "NUMBER" ):
		return int ( tree.data )

	elif ( tree.ttype == "IDENTIFIER" ):
		return int ( memory [ tree.data ] )
	
	elif ( tree.ttype == "PUNCTUATION" ):
		oper = {'+' : operator.add,
				'-' : operator.sub,
				'*' : operator.mul,
				'/' : operator.truediv,
				}
		fn = oper [ tree.data ]
		return fn ( exp ( tree.left ), exp ( tree.right ) )

def do_nothing ( tree ):
	return

def main ():
	path = scanner()
	print ( "Scanning Done" )
	tree = parser ( path )
	print ( "Parsing Done" )
	evaluator ( tree, path )
	print ( "Evaluating Done" )
# Global indexer for parser	
index = 0
# Global memory for evaluator
memory ={}
main ()
