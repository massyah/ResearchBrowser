import re
import os

#load the system wide dict file
# words=open("/usr/share/dict/words").read().split()
#assume pdfText is present and should be dehyphenated
#some examples from the pdfText
uplimit=15000
# examples=[pdfText[m.span()[0]:m.span()[1]] for m in hyphenation_re.finditer(pdfText,0,uplimit)]

sep="=>"
for e in examples:
	test=e.replace("- ","")
	if len(test)<1:continue
	if test in words:
		print e,sep,test
	elif test[-1:]=="s" and test[:-1] in words : #poor man stemmer
		print e,sep,test
	elif test[-3:]=="ing" and ((test[:-3]+"e" in words) or (test[:-3] in words)):
		print e,sep,test
	elif test[-2:]=="ed" and ((test[:-2]+"e" in words) or (test[:-2] in words)):
		print e,sep,test
	elif test[-2:]=="es" and ((test[:-2]+"e" in words) or (test[:-2] in words)):
		print e,sep,test
	elif test[-3:]=="ies" and test[:-3]+"y" in words:
		print e,sep,test
	else:
		print e,sep,e.replace("- ","-")
