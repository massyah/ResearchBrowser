#
#	xcPROJECTNAMEASIDENTIFIERxcAppDelegate.py
#	xcPROJECTNAMExc
#
#	Created by xcFULLUSERNAMExc on xcDATExc.
#	Copyright xcORGANIZATIONNAMExc xcYEARxc. All rights reserved.
#

from Foundation import *
from AppKit import *
from Cocoa import *
from appscript import *
import os
import pdb
import re
import whoosh_indexer_001 as wi
import urllib

from OOPInterface import *

dt=app("DEVONThink Pro")

urls=["/Volumes/Gauss/Desktop/temp.pdf",
"http://en.wikipedia.org/wiki/Hello_world_program","http://docs.python.org/library/pdb.html","http://www.google.fr/","http://www.ncbi.nlm.nih.gov/pubmed/20965166","http://www.ncbi.nlm.nih.gov/pubmed/16014617"]
urls_to_web_history={}
path_to_pdf_docs={}

class ResearchBrowserAppDelegate(NSObject):
	webView=objc.IBOutlet()
	urls=objc.ivar("urls")
	currentURL=objc.ivar("currentURL")
	currentPDFDoc=objc.ivar("currentPDFDoc")
	arrayController=objc.IBOutlet()
	dontObserve=objc.ivar("dontObserve")
	pdfView=objc.IBOutlet()
	splitView=objc.IBOutlet()
	currentPDFDocText=objc.ivar("currentPDFDocText")
	searchString=objc.IBOutlet()
	searchResultsView=objc.IBOutlet()
	searchResults=objc.ivar("searchResults")
	searchTerms=objc.ivar("searchTerms")
	
	def awakeFromNib(self):
		self.urls=urls
		self.currentURL=urls[0]
		self.currentResult=None
		#register for arrayController changes
		self.arrayController.addObserver_forKeyPath_options_context_(self, "selection",NSKeyValueObservingOptionNew,None)
		self.webView.preferences().setCacheModel_(2) #WebCacheModelPrimaryWebBrowser
		#load the first pdf doc
		self.loadPage(urls[0]) 
		#print the text to understand the char offsets
		self.currentPDFDocText=self.currentPDFDoc.string()
		print type(self.currentPDFDocText)
		#highlight it
		self.highlight()
		self.addDevonthinkSelection_(self)
		# self.search(u"runx1")
		# self.goToNextResult_(self)
			
	def applicationDidFinishLaunching_(self, sender):
		NSLog("Application did finish launching.")

	def loadPage(self,url):
		#we save the history if needed

		if url.startswith("/") and os.path.splitext(url)[1]==".pdf": #its a pdf file
			if url not in path_to_pdf_docs:
				pdfDoc=PDFDocument.new()
				pdfDoc.initWithURL_(NSURL.fileURLWithPath_(url))
				print "Loaded pdfDoc"
				path_to_pdf_docs[url]=pdfDoc
			self.currentPDFDoc=path_to_pdf_docs[url]
			self.pdfView.setDocument_(self.currentPDFDoc)
			if self.webView.superview()!=None:
				self.webView.retain()
				self.webView.removeFromSuperview()
				self.splitView.addSubview_(self.pdfView)
				self.pdfView.release()
			self.loadFinished(url)
		else:
			currentURL=self.webView.mainFrameURL()
			global urls_to_web_history
			if url in urls_to_web_history:
				wh=urls_to_web_history[url]
				self.webView.goToBackForwardItem_(wh)
			else:
				url=NSURL.URLWithString_(url)
				req=NSURLRequest.requestWithURL_cachePolicy_timeoutInterval_(url, NSURLRequestReturnCacheDataElseLoad,20)
				self.webView.mainFrame().loadRequest_(req)
			if self.pdfView.superview()!=None:
				self.pdfView.retain()
				self.pdfView.removeFromSuperview()
				self.splitView.addSubview_(self.webView)
				self.webView.release()

		
	#pdfView helpers 
	def highlight(self):
		firstPage=self.currentPDFDoc.pageAtIndex_(0)
		print "Should highlight",self.currentPDFDocText[100:130].encode("utf-8")
		print "Should highlight",self.currentPDFDocText[150:250].encode("utf-8")
		highlights=[(100,130),(150,250)]
		sels=[]
		#looking to highlight occurences of "circuit"
		searchRE=re.compile("circuit")
		for m in searchRE.finditer(self.currentPDFDocText):
			highlights.append(m.span())
		for h in highlights:
			pdfsel=self.currentPDFDoc.selectionFromPage_atCharacterIndex_toPage_atCharacterIndex_(firstPage,h[0],firstPage,h[1]-1)
			pdfsel.setColor_(NSColor.orangeColor())
			sels.append(pdfsel)

		#make display annotations
		self.pdfView.setHighlightedSelections_(sels)
		#modify the selection
		# self.pdfView.setCurrentSelection_(pdfsel)
		# self.pdfView.scrollSelectionToVisible_(self)
	@objc.IBAction
	def load_(self,sender):
		self.loadPage(urls[0])

	def search(self,string):
		res,self.searchTerms=wi.search(string)
		resHtml="<hr>".join(["Page %d:%s<BR><BR>%s-%s"%(x[2],x[4].replace("\n","<BR>"),x[0],"<a href=\"open://%s\">open</a>"%x[0]) for x in res])
		self.searchResultsView.mainFrame().loadHTMLString_baseURL_(resHtml,NSURL.URLWithString_(""))
		self.currentResult=None
		self.searchResults=res

		
	@objc.IBAction
	def search_(self,sender):
		self.search(sender.stringValue())
	#WebV delegates
	def webView_didFinishLoadForFrame_(self,sender,frame):
		self.dontObserve=True
		url=sender.mainFrameURL()
		# pdb.set_trace()
		self.currentURL=url
		if url not in self.urls:
			self.willChangeValueForKey_("urls")
			self.urls.append(url)
			self.didChangeValueForKey_("urls")
		currI=self.webView.backForwardList().currentItem()
		urls_to_web_history[currI.URLString()]=currI
		self.arrayController.setSelectedObjects_([url])
		self.dontObserve=False
		self.loadFinished(url)

	#searchresult view links
	def webView_decidePolicyForNavigationAction_request_frame_decisionListener_(self,wv,actionInfo,req,frame,listener):
		if wv==self.searchResultsView:
			listener.ignore()
			print "should do",req.URL().absoluteString()
			#find the doc
			path=urllib.url2pathname(req.URL().absoluteString()[len("open://"):])
			print path,path in urls
			self.arrayController.setSelectedObjects_([path])
		else:
			listener.use()

	def openCurrentResult(self):
		res=self.searchResults[self.currentResult]
		self.loadPage(res[0])

	def loadFinished(self,displayedDoc):
		if self.currentResult==None:
			return
		res=self.searchResults[self.currentResult]
		if displayedDoc!=res[0]:
			# print "displaying another item than from the search,skipping",displayedDoc,res[0]
			return
		#if pdf, navigate to page
		if os.path.splitext(displayedDoc)[1]==".pdf":
			print "pdf load finished"
			doc=path_to_pdf_docs[displayedDoc]
			tgtPage=res[2]-1
			terms_re=re.compile("|".join(self.searchTerms),re.IGNORECASE)
			#we highlights all occurences two pages before and after
			sels=[]
			start=max(res[2]-2,0)
			end=min(res[2]+2,doc.pageCount())
			sels=[]
			for i in range(start,end):
				print "Highlight for page",i
				page=doc.pageAtIndex_(i)
				txt=page.string()
				for m in terms_re.finditer(txt):
					pdfSel=doc.selectionFromPage_atCharacterIndex_toPage_atCharacterIndex_(page,m.span()[0],page,m.span()[1])
					pdfSel.setColor_(NSColor.orangeColor())
					sels.append(pdfSel)
			self.pdfView.setHighlightedSelections_(sels)
			print "should go to page",tgtPage
			self.pdfView.goToPage_(doc.pageAtIndex_(tgtPage))
			
	@objc.IBAction
	def goToNextResult_(self,sender):
		if len(self.searchResults)<1:
			return
		if self.currentResult==None or self.currentResult==len(self.searchResults)-1:
			self.currentResult=0
		else:
			self.currentResult+=1
		self.openCurrentResult()
	@objc.IBAction
	def goToPreviousResult_(self,sender):
		if len(self.searchResults)<1:
			return
		if self.currentResult==None or self.currentResult==0:
			self.currentResult=len(self.searchResults)-1
		else:
			self.currentResult-=1
		self.openCurrentResult()
		
	#overriding creation of new window
	def webView_decidePolicyForNewWindowAction_request_newFrameName_decisionListener_(self,wv,actionInfo,req,frame,listener):
		listener.ignore()
		self.loadPage(req.URL().absoluteString())
	#use dt server to display the beautified dt record
	
	#track selection changes in the table view
	def observeValueForKeyPath_ofObject_change_context_(self,kp,o,change,context):
		if self.dontObserve:
			return
		if o==self.arrayController:
			sel=self.arrayController.selectedObjects()
			if len(sel)==0:
				return
			# pdb.set_trace()
			url=sel[0]
			if url!=self.currentURL:
				self.currentURL=url
				self.loadPage(url)
	#interface
	@objc.IBAction
	def addDevonthinkSelection_(self,sender):
		self.willChangeValueForKey_("urls")
		newDocs=[]
		for s in dt.selection():
			urls.append(s.path())
			wi.add_dt_doc(s)
		self.didChangeValueForKey_("urls")
	@objc.IBAction
	def addOOPRefs(self,sender):
		self.willChangeValueForKey_("urls")
		newDocs=[]
		for s in parse_front_oop_document():
			urls.append(s)
			wi.add_dt_doc(s)
		self.didChangeValueForKey_("urls")