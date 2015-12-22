#import numpy as np
import sys

def read_file(filename):
	eFile = open(filename, 'r')
	content = eFile.read()
	eFile.close()
	return content

# takes an int
def readable(x):
	i = 0
	s = str(x)
	while i < (len(str(x))-1) / 3:
		s = s[:-3*(i+1)-i] + "," + s[-3*(i+1)-i:]
		i += 1
	
	return s
	
		
	
def uniq(array):
	seen = set()
	seen_add = seen.add
	return [ x for x in array if not (x in seen or seen_add(x))]

def getPattern(word):
	usedLetters = {}
	pat= ""
	i = 0
	for letter in word:
		try:
			pat += usedLetters[letter]
		except KeyError:
			abstractLetter = chr(97 + i)
			usedLetters[letter] = abstractLetter
			pat += abstractLetter
			i += 1
	return pat
	
def x(w1, w2):
	v = uniq(w1+w2)
	indexMapping = []
	for l in v:
		try:
			indexMapping.append((w1.index(l), w2.index(l)))
		except ValueError:
			pass
	return indexMapping

def y(ws1, ws2, indexMapping):
	res = [(w1, w2) for w1 in ws1 for w2 in ws2 if sorted(x(w1, w2)) == sorted(indexMapping)]
	return res

# finds all non-repeating pairs 
# returned size = (N^2)/2 - N/2
def z(ws):
	i = 0
	res = []
	while i < len(ws):
		for other in ws[i+1:]:
			res.append((ws[i], other))
		i += 1
	return res

#orders them according to patterns with the least possibilities
# this is for speed - the order pair-possibilities get reduced matters!
def zSorted(ws, patMap):
	i = 0
	res = []
	while i < len(ws):
		for other in ws[i+1:]:
			res.append((len(patMap[ws[i]]) * len(patMap[other]),(ws[i], other)))
		i += 1
	return [tuple[1] for tuple in sorted(res)]

# all ws same length
def xx(ws):
	n = len(ws[0])
	fixedIndexes = range(0, n)
	for i in range(0, n):
		for w in ws:
			if w[i] != ws[0][i]:
				fixedIndexes.remove(i)
				break
	return fixedIndexes
			
def mapLetters(cw, ws):
	ret = []
	fixedIndexs = xx(ws)
	pw = ws[0]
	for i in fixedIndexs:
		ret.append((cw[i], pw[i]))
	return ret

def sectionsProportions(ws, indices):
	props = {}
	n = 0
	for w in ws:
		section = ""
		for i in indices:
			section += w[i]
		try:
			props[section] += 1.0
		except KeyError:
			props[section] = 1.0
		n += 1

	for key in props.keys():
		props[key] /= n
		
	return props

def predictedReduction(ws1, ws2, mapping):
	if len(mapping) == 0:
		# there is a reduction with [] but that's when the inverse is tested - hence 'POS' reduction
		return (0.0, 0.0)
	#npMapping = np.array(mapping)
	fsts = [fst for (fst, snd) in mapping]
	snds = [snd for (fst, snd) in mapping]
	chCount1 = sectionsProportions(ws1, fsts)
	chCount2 = sectionsProportions(ws2, snds)
	
	matches = [key for key in chCount1.keys() if key in chCount2.keys()]
	r1 = 1.0 - reduce(lambda x, y: x + y, [chCount1[key] for key in matches])
	r2 = 1.0 - reduce(lambda x, y: x + y, [chCount2[key] for key in matches])
	
	t1 = sectionsProportions(ws1, [i for i in range(0, len(ws1[0])) if i not in fsts])
	t2 = sectionsProportions(ws2, [i for i in range(0, len(ws2[0])) if i not in snds])
	
	matches2 = [key for key in t1.keys() if key in t2.keys()]
	try:
		rt1 = reduce(lambda x, y: x + y, [t1[key] for key in matches2])
	except TypeError:
		rt1 = 1.0
	try:
		rt2 = reduce(lambda x, y: x + y, [t2[key] for key in matches2])
	except TypeError:
		rt2 = 1.0
	
	if rt1 < 1.0:
		r1 = max(r1, rt1)
	if rt2 < 1.0:
		r2 = max(r2, rt2)
	return ((r1, r2))

def main():

	data = read_file("wordsEn.txt")
	words = data.lower().split("\r\n")

	patts = {}
	for w in words:
		pat = getPattern(w)
		try:
			patts[pat].append(w)
		except KeyError:
			patts[pat] = [w]

	ciphertext = sys.argv[1].upper()
	ws = uniq(ciphertext.split(" "))
	wsUpdate = dict([(w, patts[getPattern(w)]) for w in ws])
	
	# check plain text is in dictionary
	if len(sys.argv) > 2:
		for key in wsUpdate.keys():
			print (key.lower() + ": " + str(key.lower() in wsUpdate[key.upper()]))
		return	
	
	i = 0
	while i < 2:
		for pair in zSorted(ws, wsUpdate):
			if not (len(wsUpdate[pair[0]]) == 1 and len(wsUpdate[pair[1]]) == 1):
				mapping = x(pair[0], pair[1])
				print ("finding possible words for linked pair: (" + pair[0] + ", " + pair[1] + ")")
				print (mapping)
				print ("Comparing " + readable(len(wsUpdate[pair[0]]) * len(wsUpdate[pair[1]])) + " possible combinations")
				possiblePairs = y(wsUpdate[pair[0]], wsUpdate[pair[1]], mapping)
				print (pair[0] + ": " + readable(len(wsUpdate[pair[0]])) + " -> " +  readable(len(uniq([fst for (fst, snd) in possiblePairs]))))
				wsUpdate[pair[0]] = uniq([fst for (fst, snd) in possiblePairs])
				print (pair[1] + ": " + readable(len(wsUpdate[pair[1]])) + " -> " +  readable(len(uniq([snd for (fst, snd) in possiblePairs]))))
				wsUpdate[pair[1]] = uniq([snd for (fst, snd) in possiblePairs])
		i += 1
	# REPEATING THE PROCESS MAY ELIMINATE MORE WORDS!!!!
	
	mappedLetters = dict([m for key in wsUpdate.keys() for m in mapLetters(key, wsUpdate[key])])
	
	print ("\n-- Results ---------------------------------")
	print (ciphertext)
	plaintext = ""
	for cw in ciphertext.split(" "):
		if len(wsUpdate[cw]) == 1:
			plaintext += wsUpdate[cw][0]
		else:
			for letter in cw:
				try:
					plaintext += mappedLetters[letter]
				except KeyError:
					plaintext += "_"
		plaintext += " "
	print (plaintext)
	
	print ("\nUnknown cipher letters:")
	print (uniq([letter for word in ws for letter in word if letter not in mappedLetters.keys()]))
	print ("\nUnknown cipher words:")
	for res in sorted([(len(wsUpdate[key]), key, sorted(wsUpdate[key])) for key in wsUpdate.keys() if len(wsUpdate[key]) > 1]):
		print (str(res) + "\n")
		

def test():
	data = read_file("wordsEn.txt")
	words = data.lower().split("\n")

	patts = {}
	for w in words:
		pat = getPattern(w)
		try:
			patts[pat].append(w)
		except KeyError:
			patts[pat] = [w]
	
	patts.pop("", None)
			
	print ("In test form")
	
	for tuple in sorted([(len(patts[key]), key) for key in patts.keys()], reverse=True)[:20]:
		#print (tuple[1] + ": " + readable(tuple[0]))
		pass
		
	ciphertext = "this is an example cipher"
	ws = uniq(ciphertext.split(" "))
	wsUpdate = dict([(w, patts[getPattern(w)]) for w in ws])
			
	for pair in zSorted(ws, wsUpdate):
		if not (len(wsUpdate[pair[0]]) == 1 and len(wsUpdate[pair[1]]) == 1):
			mapping = x(pair[0], pair[1])
			print ("finding possible words for linked pair: (" + pair[0] + ", " + pair[1] + ")")
			print (mapping)
			print ("Comparing " + readable(len(wsUpdate[pair[0]]) * len(wsUpdate[pair[1]])) + " possible combinations")
			possiblePairs = np.array(y(wsUpdate[pair[0]], wsUpdate[pair[1]], mapping))
			print (pair[0] + ": " + readable(len(wsUpdate[pair[0]])) + " -> " +  readable(len(uniq(possiblePairs[:,0]))))
			print (pair[1] + ": " + readable(len(wsUpdate[pair[1]])) + " -> " +  readable(len(uniq(possiblePairs[:,1]))))
			print ("Predicted: " + str(predictedReduction(wsUpdate[pair[0]], wsUpdate[pair[1]], mapping)))
			print ("Actual---: " + str((1.0 - float(len(uniq(possiblePairs[:,0])))/float(len(wsUpdate[pair[0]])), 1.0 - float(len(uniq(possiblePairs[:,1])))/float(len(wsUpdate[pair[1]])))))
	
	# mapping = []
	# res = []
	# ws = patts.keys()
	# print (readable(len(ws)))
	
	# res = []
	# for key in patts.keys():
		# fixedIs = xx(patts[key])
		# if len(patts[key]) > 8 and len(fixedIs) > 0:
			# res.append((len(patts[key]), (key, fixedIs)))
	# for r in sorted(res, reverse=True):
		# print (readable(r[0]) + ": " + str(r[1]))
	
	# i = 0
	# x = 0
	# res = []
	# n = len(ws)
	# while i < n:
		# for other in ws[i:]:
			# p = ws[i]
			# possiblePairs = np.array(y(patts[p], patts[other], mapping))
			# try:
				# reduction = 1.0 - float(len(uniq(possiblePairs[:,0])) + len(uniq(possiblePairs[:,1]))) / float(len(patts[p]) + len(patts[other]))
			# except IndexError:
				# reduction = 1.0
				
			# res.append((reduction, len(patts[p]) * len(patts[other]), (p, other)))
			# if len(res) > 1:
				# res = sorted(res, reverse=True)[:-1]	
		
		# print (str(100.0*(n*(i+1)/2) / float((pow(n, 2)/2 + n/2))) + "%")
		# print (res)
		# i += 1

	
		
		
if len(sys.argv) > 1:
	main()
else:
	test()
