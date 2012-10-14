    #REalityRElapse  A sequential anime downloader
    #Copyright (C) 2012  Aritra Das

    #This program is free software: you can redistribute it and/or modify
    #it under the terms of the GNU General Public License as published by
    #the Free Software Foundation, either version 3 of the License, or
    #(at your option) any later version.

    #This program is distributed in the hope that it will be useful,
    #but WITHOUT ANY WARRANTY; without even the implied warranty of
    #MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #GNU General Public License for more details.

    #You should have received a copy of the GNU General Public License
    #along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
    #Author Name: Aritra Das    Email:dodo.dodder@gmail.com
import sys
import re
import urllib2
import os
import ctypes
import string


def fetch_urls(name):
    url="http://www.realitylapse.com/videos/"+name+".php"
    ufile = urllib2.urlopen(url)
    html=ufile.read()
    pattern="/downloads/default/+"+name+"/"+name+".+?-lq.mp4"
    result=re.findall(pattern,html)
    urllist=[]
    for link in result:
        urllist.append("http://www.realitylapse.com"+link)
    return urllist


def fetch_download_link(episode,linklist):
    url=linklist[episode-1]
    ufile = urllib2.urlopen(url)
    html=ufile.read()
    link=re.search('href="(\S+)">The',html)
    return link.group(1)
    
def has_hidden_attribute(filepath): 
# os.listdir includes hidden files, 
#and fdm CLI is crap so only way to detect download completion is to see when the downloading file is unhidden . 
    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(unicode(filepath))
        assert attrs != -1
        result = bool(attrs & 2)
    except (AttributeError, AssertionError):
        result = False
    return result
	
def no_hidden_list(path): # function to check whether completed downloaded file is present in download path signaling download completion and proceedcing to next dload. 
	list=os.listdir(path)
	outlist=[]
	for file in list:
		if not has_hidden_attribute(path+'\\'+file):
			outlist.append(file)
	return outlist

def realitylapse(name,startep,endep,dpath):# work function to be hopefully called from the gui
    print dpath
    urllist=fetch_urls(name)
    startep=int(startep)
    endep=int(endep)
    downloading =0
    downloaded=0
    current_episode=startep
     #the reason why python rules. one line gets just the filename from the entire url
    #print filename
    while current_episode<=endep:
        
        #filename=link.split('/')[-1:][0]
        filename=urllist[current_episode-1].split('/')[-1:][0]
        if filename in no_hidden_list(dpath) :
            #episode done
            current_episode=current_episode+1
            print "downloaded", filename
            #downloaded=1
            downloading=0
            
        
        
        
        
        if downloading==0 and filename not in no_hidden_list(dpath) :
            link=fetch_download_link(current_episode,urllist)
            #command='c:\\progra~2\\freedo~1\\fdm.exe -fs'+' "'+link+'"'
            freepath=r'C:\Program Files (x86)\Free Download Manager\fdm.exe'
            command='"'+freepath+'"'+ ' -fs'+' '+link
            print command
            os.system(command)
             
            downloading=1
            print "downloading",filename
        
        
        
            
def main():#driver function
    realitylapse('bleach','1','4','D:\\bleach')
    return 0
    
if __name__ == '__main__':
  main()
