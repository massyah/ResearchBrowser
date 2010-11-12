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
import dehyphenate_001 as de
from appscript import *
dt=app("DEVONThink Pro")

import unicodedata
import os,math
# from IPython import ColorANSI
# tc = ColorANSI.TermColors()
# from IPython.Debugger import Tracer; debug_here = Tracer()

st = RamStorage()
schema = Schema(
		id    = ID(stored=True),
		title = TEXT(stored=True),
		path= TEXT(stored=True),
		body  = TEXT(stored=True))
ix = st.create_index(schema)
page_seps={}

def add_document(uid,path,title,bodyText):
	w = ix.writer()
	w.add_document(id=uid, path=path,title=title,body=bodyText)
	w.commit()
	print "added",len(bodyText),"chars doc"

def colorIpythonFormatter(pageSeps,text,fragments):
	resultFrags=[]
	addedChars=0 #each highligh add 11 chars
	for f in fragments:
		for tok in f.matches:
			text=text[:tok.startchar+addedChars]+tc.Red+text[tok.startchar+addedChars:tok.endchar+addedChars]+tc.Normal+text[tok.endchar+addedChars:]
			addedChars+=11
		i=0
		while pageSeps[i]<f.startchar and i<len(pageSeps):
			i+=1 
		pageRef="Page %d:"%(i+1)
		print "Got pageRef",pageRef
		resultFrags.append(pageRef+text[f.startchar+addedChars:f.endchar+15+addedChars])
	return resultFrags

def htmlFormatter(pageSeps,text,fragments):
	resultFrags=[]
	addedChars=0 #each highligh add 11 chars
	for f in fragments:
		for tok in f.matches:
			text=text[:tok.startchar+addedChars]+"<B>"+text[tok.startchar+addedChars:tok.endchar+addedChars]+"</B>"+text[tok.endchar+addedChars:]
			addedChars+=7
		i=0
		while pageSeps[i]<f.startchar:
			i+=1 
		pageRef="Page %d:"%(i+1)
		resultFrags.append(pageRef+text[f.startchar+addedChars:f.endchar+addedChars]+"<br>")
	return resultFrags

def search(q):
	s = ix.searcher()
	parser = SimpleParser("body", schema=ix.schema)
	q = parser.parse(q)
	terms = [text for fieldname, text in q.all_terms()
	        if fieldname == "body"]

	r = s.search(q)
	analyzer = schema["body"].format.analyzer
	# fragmenter = highlight.ContextFragmenter(q.all_terms,500,40)
	fragmenter=highlight.SentenceFragmenter()
	
	#just extract sentences for the first one
	search_results=[]
	for d in r:
		# The text argument to highlight is the stored text of the title
		text = d["body"]
		path=d["path"]
		for ex in highlight_extracts(path,text,terms):
			search_results.append((path,ex[0],ex[1],ex[2],ex[3]))
	search_results.sort(key=lambda x:x[1],reverse=True)
	return search_results[:20],terms

hits=[]
hitScore=[]
def highlight_and_register_hit(m):
	global hits
	hits.append((m.span()[0],m.group(0)))
	return "<B>"+m.group(0)+"</B>"

def highlight_extracts(path,docText,terms):
	global hits,hitScore
	hits=[]
	search_re=re.compile("|".join(terms),re.IGNORECASE)
	highlited=search_re.sub(highlight_and_register_hit,docText)
	#we score the hits
	hitScore=[]
	for i in range(len(hits)):
		score=0
		#max span is 300
		differentKw=set()
		j=i
		while j<len(hits) and hits[j][0]-hits[i][0]<=300:
			score+=1
			differentKw.add(hits[j][1].lower())
			j+=1
		# print differentKw,score*math.exp(len(differentKw))
		hitScore.append((hits[i][0],score*math.exp(len(differentKw))))
	#get the 10 best hits
	hitScore.sort(key=lambda x:x[1],reverse=True)
	best=hitScore[:10]
	#merge neighbors hits
	best.sort(key=lambda x:x[0])
	merged=[]
	i=0
	while i<len(best):
		j=i+1
		while j<len(best) and (best[j][0]-best[j-1][0]<=300):
			j+=1
		merged.append((best[i][1],best[i][0],best[j-1][0]+300))
		i=j
	merged.sort(key=lambda x:x[0],reverse=True)
	res=[]
	if path in page_seps:
		pageSeps=page_seps[path]
	else:
		pageSeps=None
	for h in merged:
		start=max(0,h[1]-60)
		excerpt=docText[start:h[2]+300]
		excerpt=search_re.sub(lambda x:"<B>"+x.group(0)+"</B>",excerpt)
		i=0
		if pageSeps:
			while i<len(pageSeps) and pageSeps[i]<h[1]:
				i+=1 
			if i!=len(pageSeps):
				i+=1
		res.append((h[0],i,h[1],excerpt))
	return res


def get_page_seps(text):
	seps=[]
	idx=0
	while idx!=-1:
		idx=text.find("\n",idx+1)
		seps.append(idx)
	return seps

def add_pdf_doc(title,pdfPath):
	global page_seps
	pdfDoc=PDFDocument.new()
	pdfDoc.initWithURL_(NSURL.fileURLWithPath_(pdfPath))
	pdfText=de.dehyphenate(pdfDoc.string())
	#we update the page sep mapping based on linefeed chars
	page_seps[pdfPath]=get_page_seps(pdfText)
	add_document(u"1",pdfPath,title,pdfText)
	

def add_dt_doc(d):
	ext=os.path.splitext(d.path())[1]
	if ext in [".pdf"]:
		add_pdf_doc(d.name(),d.path())
	else:
		add_document(u"1",d.path(),d.name(),d.plain_text())
	print "Indexed ",d.name().encode("utf-8")

docs=[
"/Volumes/Gauss/Desktop/1471-2105-7-56.pdf",
"/Volumes/Gauss/Desktop/2007 levine miRNA regulation model.pdf",
"/Volumes/Gauss/Desktop/2009 Korn.pdf",
"/Volumes/Gauss/Desktop/364216174X.pdf",
"/Volumes/Gauss/Desktop/3642037216.pdf",
"/Volumes/Gauss/Desktop/ams_bx_20101014 klm.pdf",
"/Volumes/Gauss/Desktop/Marija Hayssam.pdf",
"/Volumes/Gauss/Desktop/sdarticle-1.pdf",
"/Volumes/Gauss/Desktop/sdarticle.pdf",
]
# for d in docs:
# 	add_pdf_doc(u"a title",unicode(d))
# dt_doc=dt.selection()[0]
# add_dt_doc(dt_doc)
# search(u"rorgt")

