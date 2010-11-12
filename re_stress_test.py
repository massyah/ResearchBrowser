import re
from appscript import *

#a 30 pages article has 
#a 1k pages book has 650000
#a page has at ~ 700 words
nArt=10
#generate the data
dt=app("DEVONThink Pro")

# for s in dt.selection():data.append(s.plain_text()) #5.6 secs, approx 102116 words, ~145 pages
#data=data*50 #~5447300 words, 8253 pages, 275 articles

		
terms_to_search=["polarize","th17","petri net"]
terms_re=re.compile("|".join(terms_to_search),re.IGNORECASE)

m=0
for d in data:m+=len(terms_re.findall(d)) #4 seconds, 8400 matches, mem usage is 21Mb
print "total matches",m 

#test: Get all words starting with bioch, 1 sec for all the words
bioch_re=re.compile("mole\w*",re.IGNORECASE)
words=set()
for d in data:words.update(bioch_re.findall(d))

#test2 simple word search
simple_re=re.compile("STAT3")
m=0
%time for d in data:m+=len(simple_re.findall(d))
print m,"matches" #1050 matches, 0.10 sec

simple_re=re.compile("STAT3",re.IGNORECASE) 
m=0
%time for d in data:m+=len(simple_re.findall(d))
print m,"matches" #1.06 sec

#terms but case wise
terms_to_search=["polarize","th17","petri net"]
terms_re=re.compile("|".join(terms_to_search))
m=0
%time for d in data:m+=len(terms_re.findall(d)) #0.62 seconds, 250 matches, mem usage is 21Mb
print "total matches",m 

#terms but case wise, with lower
terms_to_search=["polarize","th17","petri net"]
terms_re=re.compile("|".join(terms_to_search))
m=0
%time for d in data:m+=len(terms_re.findall(d.lower())) 
print "total matches",m #0.98 seconds, 8400 matches

#terms with lower
terms_to_search=["polarize","th17","petri net","biochemical","species","biocham"]
terms_re=re.compile("|".join(terms_to_search))
m=0
%time for d in data:m+=len(terms_re.findall(d.lower())) 
print "total matches",m #1.39 seconds, 15600 matches

#iteration and multi search?

def msearch():
	m=0
	for d in data:
		dl=d.lower()
		# dl=d
		for t in terms_to_search:
			tre=re.compile(t)
			m+=len(tre.findall(dl))
	return m
	
%time msearch() ,#1.03s, 15600 matches

#if we lower the data separately, we get down to 0.67s 

#with cache

def msearch_cache(force=False):
	global cache
	m=0
	for d in data:
		# dl=d.lower()
		dl=d
		for t in terms_to_search:
			if t not in cache:
				cache[t]=[]
				tre=re.compile(t)
				cache[t].extend([x.span() for x in tre.finditer(dl)])
				m+=len(cache[t])
			elif force:
				tre=re.compile(t)
				cache[t].extend([x.span() for x in tre.finditer(dl)])
				m+=len(cache[t])
			else:
				m+=len(cache[t])
	return m

%time msearch_cache(True) #0.67 without lower, 1.0 s with, 7881200
%time msearch_cache() #0.0s