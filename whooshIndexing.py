#!/usr/bin/env python
# encoding: utf-8

#spike document how whoosh can be used to get exceprts

from whoosh.index import create_in,open_dir
from whoosh.fields import *
from whoosh.searching import *
from whoosh.qparser import QueryParser,SimpleParser
from whoosh.qparser import MultifieldParser
from whoosh.filedb.filestore import RamStorage
from whoosh import highlight

from Foundation import *
from AppKit import *
from Cocoa import *
from Quartz import *

import unicodedata


from IPython import ColorANSI
tc = ColorANSI.TermColors()

import os

#get the text of a pdf file
#to speed up the test, don't reload it each time
# pdfPath="/Volumes/Gauss/Desktop/2009 Korn.pdf"
# pdfDoc=PDFDocument.new()
# pdfDoc.initWithURL_(NSURL.fileURLWithPath_(pdfPath))
# pdfText=pdfDoc.string()
#correct for hyphenation
pdfText=pdfText.replace("- ","")
#stop at the last "\r"
print type(pdfText),len(pdfText)

st = RamStorage()
schema = Schema(
		id    = ID(stored=True),
		title = TEXT(stored=True),
		body  = TEXT(stored=True))
ix = st.create_index(schema)

bodyText=u"Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. This is at the end you know. Spotme!"
w = ix.writer()
w.add_document(id=u"1", title=u"The man who wasn't there",body=bodyText)
w.add_document(id=u"2", title=u"The dog who barked at midnight",body=bodyText)
w.add_document(id=u"3", title=u"The invisible man")
w.add_document(id=u"4", title=u"The girl with the dragon tattoo")
w.add_document(id=u"5", title=u"The woman who disappeared")
w.add_document(id=u"6",title=u"PDF test",body=pdfText)
w.commit()

# Perform a search
# ----------------

s = ix.searcher()

# Parse the user query
parser = QueryParser("title", schema=ix.schema)
q = parser.parse(u"man")

# Extract the terms the user used in the field we're interested in
# THIS IS HOW YOU GET THE TERMS ARGUMENT TO highlight()
terms = [text for fieldname, text in q.all_terms()
        if fieldname == "title"]

# Get the search results
r = s.search(q)
assert len(r) == 2

# Use the same analyzer as the field uses. To be sure, you can
# do schema[fieldname].format.analyzer. Be careful not to do this
# on non-text field types such as DATETIME.
analyzer = schema["title"].format.analyzer

# Since we want to highlight the full title, not extract fragments,
# we'll use NullFragmenter. See the docs for the highlight module
# for which fragmenters are available.
fragmenter = highlight.NullFragmenter

# This object controls what the highlighted output looks like.
# See the docs for its arguments.
formatter = highlight.HtmlFormatter()

for d in r:
   # The text argument to highlight is the stored text of the title
   text = d["title"]

   print highlight.highlight(text, terms, analyzer,
                             fragmenter, formatter)

#do it on the body now
def colorIpythonFormatter(text,fragments):
	resultFrags=[]
	addedChars=0 #each highligh add 11 chars
	for f in fragments:
		for tok in f.matches:
			text=text[:tok.startchar+addedChars]+tc.Red+text[tok.startchar+addedChars:tok.endchar+addedChars]+tc.Normal+text[tok.endchar+addedChars:]
			addedChars+=11
		resultFrags.append(text[f.startchar+addedChars:f.endchar+15+addedChars])			
	return " [...] ".join(resultFrags)

def colorIpythonFormatter(text,fragments):
	resultFrags=[]
	addedChars=0 #each highligh add 11 chars
	for f in fragments:
		for tok in f.matches:
			text=text[:tok.startchar+addedChars]+tc.Red+text[tok.startchar+addedChars:tok.endchar+addedChars]+tc.Normal+text[tok.endchar+addedChars:]
			addedChars+=11
		resultFrags.append(text[f.startchar+addedChars:f.endchar+15+addedChars])
	return " [...] ".join(resultFrags)

def searchBodyAndHighlight(q):
	parser = SimpleParser("body", schema=ix.schema)
	q = parser.parse(q)
	terms = [text for fieldname, text in q.all_terms()
	        if fieldname == "body"]

	r = s.search(q)
	analyzer = schema["body"].format.analyzer
	print "will tokenize with",q.all_terms
	fragmenter = highlight.ContextFragmenter(q.all_terms,400,80)
	# formatter = highlight.HtmlFormatter()
	formatter = colorIpythonFormatter

	for d in r:
		# The text argument to highlight is the stored text of the title
		text = d["body"]
		res= highlight.highlight(text, terms, analyzer,fragmenter, formatter)
		# print res.encode("latin-1","replace")
		print unicodedata.normalize('NFKC', res).encode("utf-8","replace")
		print "-"*8
	
	
# searchBodyAndHighlight(u"elit spotme consectetur cillum")
searchBodyAndHighlight(u"levels members regulatory reduced")
searchBodyAndHighlight(u"\"TGF β and the proinflammatory pleiotropic cytokine IL-6\"")