import sys

test_cases = open(sys.argv[1], 'r')
for test in range(1, 28):
    n = int(test)
    colID = ""
    while n > 0:
        n -= 1
        colID = chr(ord('A') + n % 26) + colID
        n /= 26
    print (str(test) + ": " + colID)

test_cases.close()
