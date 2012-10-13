from Tkinter import *
import tkFileDialog
import sys
import re
import urllib2
import os
import ctypes
from functools import partial
from multiprocessing import *


##########################################################################################


def fetch_urls(name,flag,ulist,active):
    
    active.value=1
    url="http://www.realitylapse.com/videos/"+name+".php"

    ufile = urllib2.urlopen(url)
    html=ufile.read()
    pattern="/downloads/default/+"+name+"/"+name+".+?-lq.mp4"
    result=re.findall(pattern,html)

    for link in result:
       ulist.put("http://www.realitylapse.com"+link)

    flag.value=1
    active.value=0    

    
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


def realityrelapse(urllist,startep,endep,dpath,paused,q,active,fdm):# work function to be hopefully called from the gui
    #print dpath
    #print fdm
    fdm=fdm+r'/fdm.exe'
    #print fdm
    #print os.path.normpath(fdm)
    
    p='"'+os.path.normpath(fdm)+'"'+" -fs"+" "
    #print p
    #str.replace("\\",'/')
    #urllist=fetch_urls(name)
    active.value=1
    startep=int(startep)
    endep=int(endep)
    downloading =0
    current_episode=startep
    filename=urllist[current_episode-1].split('/')[-1:][0] #the reason why python rules. one line gets just the filename from the entire urllist
    #print filename
    while current_episode<=endep:
        
        if (not paused.value):
            #print paused.value
            filename=urllist[current_episode-1].split('/')[-1:][0]
            if filename in no_hidden_list(dpath) :
                #episode done
                current_episode=current_episode+1
                q.put("downloaded "+filename)
                #downloaded=1
                downloading=0
            
            if downloading==0 and filename not in no_hidden_list(dpath) :
                link=fetch_download_link(current_episode,urllist)
                command=p+link 
                os.system(command)
                 
                downloading=1
                q.put("downloading "+filename)
        #else:
           # q.put("Paused")
           #print paused.value
    active.value=0

#############################################################

def main():
    freeze_support()
    listflag = Value('i')
    listflag.value=0
    pause= Value('i')
    pause.value=0
    urllist=[]
    qrl=Queue()
    mess_q=Queue()
    pactive=Value('i')
    p1active=Value('i')
    pactive.value=0
    p1active.value=0
    root=Tk()
    c=StringVar()
    i=0
    c.set(str(i))
    root.wm_title("REalityRElapse")
    RWidth=root.winfo_screenwidth()/2.7
    RHeight=root.winfo_screenheight()/1.7
    root.geometry(("%dx%d")%(RWidth,RHeight))
            
    aname=StringVar()
    directory=StringVar()
    startep=StringVar()
    endep=StringVar()
    aname.set("naruto")

    
    def dir():
        dirname = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select a directory')
        if (len(dirname)>0) :    
            directory.set(dirname)
        return 0
    def setbleach():
        aname.set("bleach")
        #pad.set("3")
        return 0
    def setnaruto():
        aname.set("naruto")
        #pad.set("3")
    def setnarutoS():
        aname.set("naruto-shippuuden")
        #pad.set("3")    
    def setmonster():
        aname.set("monster")
        #pad.set("2")
    L1=Label(root,text ="Anime name" )
    L1.grid(row=0,column=0)
    E1 = Entry(root, bd =5,textvariable=aname,justify=CENTER,width=20)
    E1.grid(row=0,column=1,columnspan=3)
    L2=Label(root,text="Choose download directory")
    L2.grid(row=1,column=0)
    E2 = Entry(root, bd =5,textvariable=directory,justify=CENTER,width=20)
    E2.grid(row=1,column=1,columnspan=3)
    B2 = Button(root, text ="...", command = dir)
    B2.grid(row=1,column=4)
    
    L3=Label(root,text="Range of episodes(inclusive at both ends)")
    L3.grid(row=2,column=0)
    E3 = Entry(root, bd =5,textvariable=startep,justify=CENTER,width=5)
    E3.grid(row=2,column=1,sticky=W,)
    L4=Label(root,text="to",anchor=W,width=2)
    L4.grid(row=2,column=2,sticky=W)
    E4=Entry(root, bd =5,textvariable=endep,justify=CENTER,width=5)
    E4.grid(row=2,column=3,sticky=W)
    
    L6=Label(root,text="PRESETS",anchor=E)
    L6.grid(row=4,column=0)
    
    bleach=Button(root, text ="BLEACH", command = setbleach)
    naruto=Button(root, text ="NARUTO", command = setnaruto)
    narutoS=Button(root, text ="NARUTO SHIPPUDIN", command = setnarutoS)
    monster=Button(root, text ="MONSTER", command = setmonster)
    bleach.grid(row=5,column=0)
    naruto.grid(row=5,column=1)
    narutoS.grid(row=6,column=0)
    monster.grid(row=6,column=1)
    anime=aname.get()

    st="normal"
    #parent_conn,child_conn=Pipe()
    def fetch():
        p = Process(target=fetch_urls,args=(aname.get(),listflag,qrl,pactive))
        p.daemon = True
        fetchbutton.configure(state="disabled")
        mess_q.put("Fetching links")
        p.start()
        
    def validform():
        
        code=0
        
        if len(aname.get())>0 and len(directory.get())>0 and len(startep.get())>0 and len(endep.get())>0 :
            code=1
        
        return code
    def dload():
        
        if(not validform()):
            mess_q.put("CANNOT PROCEED: Incomplete Form!")
            
        if(validform()): 
            #print "valid"
            #warning.configure(text="")
            p1=Process(target=realityrelapse,args=(urllist,startep.get(),endep.get(),directory.get(),pause,mess_q,p1active,fdmdirectory.get()))
            p1.daemon = True
            p1.start()
            fetchbutton.configure(text="Pause",command=pause_download)
    def pause_download():
        pause.value=1
        fetchbutton.configure(text="Resume",command=resume_download)
        mess_q.put("Paused")
        #loglabel.configure(text="MESSAGE LOG (Process Paused)")
    def resume_download():
        pause.value=0
        fetchbutton.configure(text="Pause",command=pause_download)
        mess_q.put("Unpaused")
        #loglabel.configure()
    
    donelist=0    
    def callback(flag,donelist): 
        i=0
        if flag.value==1 and donelist==0:
            frame = Frame(root, bd=2, relief=SUNKEN)
            m=Label(frame,text='Get ep. no for range field for specific files here' )
            m.pack()
            scrollbary = Scrollbar(frame)
            scrollbary.pack(side=RIGHT, fill=Y)
            scrollbarx = Scrollbar(frame, orient=HORIZONTAL)
            scrollbarx.pack(side=BOTTOM,fill=X)
            lb=Listbox(frame, bd=0, yscrollcommand=scrollbary.set ,xscrollcommand=scrollbarx.set ,width=35 , height=15)
            lb.pack()
            lb.insert(END,'ep.no           ep.title')
            scrollbary.config(command=lb.yview)
            scrollbarx.config(command=lb.xview)
            
            while not qrl.empty(): 
                urllist.append(qrl.get())
                l_mess=str(i+1)+'           '+urllist[-1].split('/')[-1]
                lb.insert(END,l_mess)
                i=i+1
            
            frame.grid(row=8,column=0)
            fetchbutton.configure(state="normal",text="DOWNLOAD",command=dload)
            donelist=1
        root.after(200,callback,listflag,donelist)
    root.after(200,callback,listflag,donelist)   
    
    
    #make logbox
    logframe = Frame(root, bd=2, relief=SUNKEN)
    loglabel=Label(logframe,text="MESSAGE LOG")
    loglabel.pack()
    lscrollbary = Scrollbar(logframe)
    lscrollbary.pack(side=RIGHT, fill=Y)
    lscrollbarx = Scrollbar(logframe, orient=HORIZONTAL)
    lscrollbarx.pack(side=BOTTOM,fill=X)
    logbox=Listbox(logframe, bd=0, yscrollcommand=lscrollbary.set ,xscrollcommand=lscrollbarx.set ,width=35 , height=15)
    logbox.pack()
    lscrollbary.config(command=logbox.yview)
    lscrollbarx.config(command=logbox.xview)
    logframe.grid(row=8,column=3,columnspan=4)

    def logging():
        #if pause.value==0: loglabel.configure(text="MESSAGE LOG (Process Paused)")
        #if pause.value==0: loglabel.configure(text="MESSAGE LOG (Process Running)")
        if not mess_q.empty():
            logbox.insert(END,mess_q.get())
        root.after(200,logging)    
    root.after(200,logging)
    def askdir():
        diname = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select a directory')
        if (len(diname)>0) :    
            fdmdirectory.set(diname)
    fdmdirectory=StringVar()
    fdmdirectory.set('C:/Program Files (x86)/Free Download Manager')
    fetchbutton=Button(root,text ="FETCH",command =fetch)
    fetchbutton.grid(row=8,column=1)
    bframe=Frame(root, bd=1, relief=SUNKEN ,width=80)
    fdmpathlabel=Label(bframe,text="Free Download Manager path")
    fdmentry=Entry(bframe, bd =5,textvariable=fdmdirectory,justify=CENTER,width=40)
    fdmbutton=Button(bframe,text="...",command=askdir)
    fdmpathlabel.pack(side=LEFT)
    fdmentry.pack(side=LEFT)
    fdmbutton.pack(side=LEFT)
    bframe.grid(row=9,column=0,columnspan=15)


    root.mainloop()

    
if __name__ == '__main__':
  main()
