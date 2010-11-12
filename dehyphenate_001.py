#!/usr/bin/env python
# encoding: utf-8

import re
import os


hyphenation_re=re.compile("\w+-\s\w+")
termsWithHyphens=["IL-","TGF-β","STAT-","JAK-","IFN-","IRF\d*-","JAK\d","TRAF-"]
termsWithHyphens_re=re.compile("\w+|".join(termsWithHyphens)+"\w+")

def dehyphenated_version(match):
	w=match.group(0)
	test=w.replace("- ","-")
	if termsWithHyphens_re.match(test):
		res=test
	else:
		res=w.replace("- ","")
	return res
	
def dehyphenate(pdfText):
	return hyphenation_re.sub(dehyphenated_version,pdfText)
