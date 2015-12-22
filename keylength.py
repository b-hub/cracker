import sys
from string import ascii_lowercase
import random

enFreq = [8167, 1492, 2782, 4253, 12702, 2228, 2015, 6094, 6966, 153, 772, 4025, 2406, 6749, 7507, 1929, 95, 5987, 6327, 9056, 2758, 975, 2361, 0150, 1974, 74]


def read_file(filename):
	eFile = open(filename, 'r')
	content = eFile.read()
	eFile.close()
	return content
	
def factors(n):    
	return set(reduce(list.__add__,([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0)))
	
def repeatingMask(text, repeatingMap):
	for (window, indices) in repeatingMap:
		for index in indices:
			i = 0
			while i < len(window):
				text[index + i] = window[i]
				i += 1
	return "".join(text)
	
def repeatingWindows(text):
	wDic = {}

	windowSize = 3
	while windowSize <= 5:
		currIndex = 0
		while currIndex + windowSize < len(ciphertext):
			window = text[currIndex : currIndex + windowSize]
			try:
				wDic[window].append(currIndex)
			except KeyError:
				wDic[window] = [currIndex]
	
			currIndex += 1
		windowSize += 1
	
	return [(window, wDic[window]) for window in wDic.keys() if len(wDic[window]) > 1]
	
def z(ws):
	i = 0
	res = []
	while i < len(ws):
		for other in ws[i+1:]:
			res.append((ws[i], other))
		i += 1
	return res
	
def orderedFactorCount(repeatingMap, uniqGaps):
	gaps = []
	count = {}
	for (window, indecies) in repeatingMap:
		for (i1, i2) in z(indecies):
			gap = abs(i2 - i1)
			if not uniqGaps or uniqGaps and gap not in gaps:
				for f in factors(abs(i2 - i1)):
					try:
						count[f] += 1
					except KeyError:
						count[f] = 1
				gaps.append(gap)
	return sorted([(count[factor], factor) for factor in count.keys() if factor != 1], reverse=True)
	
def getFreq(text):
	alphabet = list(ascii_lowercase)
	freq = dict(zip(alphabet, [0 for l in alphabet]))
	for letter in [l.lower() for l in text]:
		freq[letter] += 1
	return freq
	
def ic(freq, n):
	return reduce((lambda x, y: x + y), [freq[f] * (freq[f]-1) for f in freq.keys()]) / (n * (n-1.0) / len(freq.keys()))
	
#------------------------------

def keyCharFor(cChar, pChar):
	return chr(ord('a') + abs(ord(cChar.lower()) - ord(pChar.lower())))

def predictKeyChar(givenCipherChar, letterFreqs):
	pK = pC = 1.0/26.0
	
	res = []
	
	for pChar in alphabet:
		kChar = keyCharFor(givenCipherChar, pChar)
		res.append((letterFreqs[pChar], (kChar, pChar)))
	
	return sorted(res, reverse=True)

#------------------------------- 

def encrypt(key, text):
	ciphertext = ""
	i = 0
	while i < len(plaintext):
		kChar = key[i % len(key)]
		shift = ord(kChar) - ord('a')
		eChar = alphabet[(ord(plaintext[i]) - ord('a') + shift) % 26]
		ciphertext += eChar.upper()
		i += 1
	return ciphertext
	
	
alphabet = list(ascii_lowercase)
key = sys.argv[1]

data = read_file("wordsEn.txt")
words = data.lower().split("\r\n")

plaintext = ""
testSize = int(sys.argv[2])
while len(plaintext) < testSize:
	plaintext += words[random.randint(0, len(words)-1)]
	
	
ciphertext = encrypt(key, plaintext)
	
print (plaintext)
print (ciphertext)

wDic = {}
factorCount = {}
prevGaps = []

#ciphertext = "PPQCAXQVEKGYBNKMAZUYBNGBALJONITSZMJYIMVRAGVOHTVRAUCTKSGDDWUOXITLAZUVAVVRAZCVKBQPIWPOU"
plainMask = ['_' for char in plaintext]
cipherMask = ['_' for char in ciphertext]

windowSize = 3
while windowSize <= 5:
	currIndex = 0
	while currIndex + windowSize < len(ciphertext):
		window = ciphertext[currIndex : currIndex + windowSize]
		try:
			for i in wDic[window]:
				gap = currIndex - i
				if gap not in prevGaps:
					#print (window + ": " + str(gap) + ", " + str(factors(gap)))
					for f in factors(gap):
						try:
							factorCount[f] += 1
						except KeyError: 
							factorCount[f] = 1
						prevGaps.append(gap)
					
			wDic[window].append(currIndex)
		except KeyError:
			wDic[window] = [currIndex]
	
		currIndex += 1
	windowSize += 1
	

rKey = [key[i % len(key)] for i in range(0, len(plaintext))]
print ("".join(rKey))
pws = repeatingWindows(plaintext)
cws = repeatingWindows(ciphertext)
pMask = repeatingMask(plainMask, pws)
cMask = repeatingMask(cipherMask, cws)

print (pMask)
print (cMask)
print (pws)
print (cws)

fs = orderedFactorCount(cws, False)
fsU = orderedFactorCount(cws, True)
print (fs[:5])
print (fsU[:5])

print (reduce((lambda x, y: x + y), map(lambda x: (x/100000.0)**2, enFreq)) / (1 / 26.0))
print (ic(getFreq(plaintext), len(plaintext)))

def deltaBarIC(text, keySize):
	cols = [[] for i in range(0, keySize)]
	i = 0
	while i < len(text):
		cols[i % keySize].append(text[i])
		i += 1
	
	deltaBar = reduce((lambda x, y: x + y), [ic(getFreq(col), len(col)) for col in cols]) / float(len(cols))
	return deltaBar

for n in range (1, 5):
	print (str(n) + ": " + str(deltaBarIC(ciphertext, n)))
	

for cChar in ciphertext:
	pKs = predictKeyChar(cChar, dict(zip(alphabet, map((lambda x: x / 100000.0), enFreq))))
	print (cChar + ": " + str(pKs[:5]))

count = {}
for w in words:
	if len(w) > 0:
		fstChar = w[0]
		try:
			count[fstChar] += 1
		except KeyError:
			count[fstChar] = 1

print sorted([(float(count[l]) / len(words), l) for l in count.keys()], reverse=True)[:10] 

c = "TO"
k2w = []
for w in words:
	if len(w) == len(c):
		i = 0
		key = ""
		while i < len(c):
			key += keyCharFor(c[i], w[i])
			i += 1
		k2w.append((w, key))
		
for m in sorted(k2w):
	print m



