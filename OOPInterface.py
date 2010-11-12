# OOP interface
import re,os
from appscript import *
oop=app("OmniOutliner Professional")
sa=app("Safari")

def get_oop_contents_xml(originalPath):
	# originalPath=originalPath.replace(" ","\\ ")
	fileType=os.popen("file -b \"%s\""%(originalPath+"/contents.xml")).read()

	if fileType.startswith("gzip"):
		cmd="gunzip -c -S xml -d \"%s/contents.xml\" > \"%s/text.xml\""%(originalPath,originalPath)

		os.system(cmd)
		
		return originalPath+"/text.xml"
	else:
		print "Not gzipped"
		return originalPath+"/contents.xml"

def parse_oop_doc(path):
	f=open(get_oop_contents_xml(path),"r")
	lines=f.read()
	f.close()
	# print lines[:100].decode("utf-8","ignore")
	#get the ref tree
	ref_re=re.compile("<lit>\s?Refs</lit>(.*)</root>",re.DOTALL)
	refs=ref_re.findall(lines)[0]
	# print refs
	#get the ref urls
	refsURL=[]
	ref_re=re.compile("<cell href=\"([^ ]*)\".*?/>")
	for m in ref_re.finditer(refs):
		refsURL.append(m.groups(1)[0])
	return refsURL
	
def add_ref_row(txt):
	doc=oop.documents[1]
	refRow=doc.rows[its.topic=="Refs"].get()[0]
	r=doc.make(at=refRow.rows.end, new=k.row)
	r.topic.set(txt)

def add_safari_tabs_url_to_oop():
	oop.documents[1].save()
	idx=len(parse_front_oop_document())
	tabs=sa.windows[1].tabs()
	refRow=""
	for t in tabs:
		add_ref_row("["+str(idx)+"] "+t.name()+"-"+t.URL())
		idx+=1
		
def open_references():
	oop.documents[1].save()
	docs=parse_front_oop_document()
	for d in docs:
		os.system("open \"%s\""%(d))
	
def parse_front_oop_document():
	oop.documents[1].save()
	p=oop.documents[1].path()

	return parse_oop_doc(p)

# testPath="/Volumes/Gauss/Documents/oo4_example.xml"
# testPath2="/Volumes/Gauss/Library/Application Support/DEVONthink Pro 2/Inbox.dtBase2/Files.noindex/oo3/2/research browser.oo3"

# parse_oop_doc(testPath2)
# parse_front_oop_document()