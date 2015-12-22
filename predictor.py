import sys
import random

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
	
def precision(x, dp):
	mul = pow(10,dp)
	return int(x * mul) / float(mul)

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
	
	results = []
	while len(results) < 100:
	
		pair = (words[random.randint(0, len(words)-1)], words[random.randint(0, len(words)-1)])
		wsUpdate = dict([(w, patts[getPattern(w)]) for w in pair])

		if not (len(wsUpdate[pair[0]]) == 1 and len(wsUpdate[pair[1]]) == 1):
			mapping = x(pair[0], pair[1])
			print ("finding possible words for linked pair: (" + pair[0] + ", " + pair[1] + ")")
			print (mapping)
			possibleWords0 = wsUpdate[pair[0]]
			possibleWords1 = wsUpdate[pair[1]]
			combinations = len(possibleWords0) * len(possibleWords1)
			if combinations < 500000:
				print ("Comparing " + readable(combinations) + " possible combinations")
				possiblePairs = y(possibleWords0, possibleWords1, mapping)
				initialSize0 = len(possibleWords0)
				reducedSize0 = len(uniq([fst for (fst, snd) in possiblePairs]))
				initialSize1 = len(possibleWords1)
				reducedSize1 = len(uniq([snd for (fst, snd) in possiblePairs]))
				print (pair[0] + ": " + readable(initialSize0) + " -> " +  readable(reducedSize0))
				print (pair[1] + ": " + readable(initialSize1) + " -> " +  readable(reducedSize1))
				predicted = predictedReduction(possibleWords0, possibleWords1, mapping)
				actual = ((initialSize0 - reducedSize0)/float(initialSize0), (initialSize1 - reducedSize1)/float(initialSize1))
				print ("Predicted: " + str(predicted))
				print ("Actual---: " + str(actual))
				reductions0 = int((actual[0] - predicted[0])*len(possibleWords0))
				reductions1 = int((actual[1] - predicted[1])*len(possibleWords1))
				diff0 = initialSize0 - reducedSize0
				error0 = 0
				if diff0 != 0:
					error0 = reductions0 / float(diff0)
				error1 = 0
				diff1 = initialSize1 - reducedSize1
				if diff1 != 0:
					error1 = reductions1 / float(diff1)
				results.append((reductions0 + reductions1, (precision(error0*100, 1), precision(error1*100, 1)), (diff0, diff1), mapping))
	
	for res in sorted(results):
		print (res)
main()

