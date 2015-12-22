import sys

#--Functions and vars that depend on eachother----------------------------------------

alphabet = []
# $- is replaced with terminal flags so if the key has $- anywhere in it, it gets decrypted as himBH or something.... >.<
dodgyChars = ['$']
for n in range(32, 127):
	ch = chr(n)
	if ch not in dodgyChars:
		alphabet.append(chr(n))
		
def shiftChar(c1, c2):
	return alphabet[(alphabet.index(c1) - alphabet.index(c2)) % len(alphabet)]

def keyCharFor(cChar, pChar):
	return shiftChar(cChar, pChar)
	
def decrypt(key, cipher):
	plaintext = ""
	i = 0
	while i < len(key):
		plaintext += shiftChar(cipher[i], key[i])
		i += 1
	
	return plaintext
	
#----------------------------------------------



mode = sys.argv[1]

if mode == "d":
	print ("Decryption Mode, to exit press: ctrl + c") 
	ciphertext = raw_input("Enter the ciphertext:")
	print (ciphertext)
	key = raw_input("Now enter the key:")
	print (key)
	print ("Plaintext: " + decrypt(key, ciphertext))
elif mode == "e":
	print ("Encryption Mode, to exit press: ctrl + c") 
	plaintext = raw_input("Enter the plaintext:")
	print (plaintext)
	ciphertext = raw_input("Now enter the ciphertext:")
	print (ciphertext)

	if len(plaintext) <= len(ciphertext):
		i = 0
		key = ""
		while i < len(plaintext):
			key += keyCharFor(ciphertext[i], plaintext[i])
			i += 1

		#print (plaintext)
		startChr = chr(175)
		endChr = chr(174)
		print (startChr + "KEY" + endChr + ", make sure you copy everything between the " + startChr + " and the " + endChr)
		print (startChr + key + endChr)
		#print (ciphertext[:len(key)])
		#print decrypt(key, ciphertext)
		#print enum(key)
	else:
		print ("The length of ciphertext must be >= to plaintext to encrypt all of it")
else:
	print ("Please enter either the character 'e' or 'd' for either encryption or decryption")
	exit(-1)
	
	






