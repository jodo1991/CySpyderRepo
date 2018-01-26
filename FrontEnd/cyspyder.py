from tkinter import *
from tkinter.ttk import Frame
from tkinter.ttk import Treeview
from tkinter.ttk import Progressbar, Style
from tkinter import filedialog, messagebox
import json
import webbrowser
import unicodedata
import datetime
import makemenu
import analysis
import requests
from dateutil import parser
from PIL import ImageTk, Image
import os
import textwrap
import time
import threading
import queue
import calltipwindow
import cyhelper


class cyberapi(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("Article Searcher")       #Title of window
        #set the frame dimentions and pack the parent window
        container = Frame(self)
        menu = makemenu.MainMenu(self).createMenu()

        self.updateque = queue.Queue()
        self.analyzer = analysis.Analyzer(self.updateque)
        container.place(relx=.5, rely=.5, relwidth=1, relheight=1, anchor=CENTER)
        #container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.resizable(width=False, height=False)

        #get screen dimensions and center window
        xoffset = int(self.winfo_screenwidth()/2-700/2)
        yoffset = int(self.winfo_screenheight()/2-550/2)
        self.geometry("%dx%d+%d+%d" % (700, 450, xoffset, yoffset))    #set geometry of window
        self.frames = {}
        for F in (SearchFrame, StartFrame):       #The two windows used in program sets the page
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")


        self.show_frame('StartFrame')
    def get_file(self):
        return SearchFrame.content
    def set_file(self, obj):
        SearchFrame.content = obj
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()                     #raise that window frame
        self.title(frame.title)             #rename the window title to the title in def Welcome

    def changeTitle(self, newTitle):
        self.title(newTitle)

class SearchFrame(Frame):
    content = None
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.analysisthread = None
        self.controller = controller  # set the controller
        self.title = "Article Search"  # title of the window

        #title
        path = os.getcwd() + '\\resources\cyspider.jpg'
        self.img = ImageTk.PhotoImage(Image.open(path))
        self.panel = Label(self, image=self.img)
        self.panel.pack()

        # widgets for results page
        # frame for individual analysis
        self.sf = LabelFrame(self, width=550, height=150, background='#383838', bd=6)

        # frame for results analysis
        self.sf2 = LabelFrame(self, width=550, height=150, background='#383838', bd=6)

        # labels for article topics
        self.topicsHead = Label(self, text='Key Article Subjects', font="times 16 underline", background='#282828',
                                foreground='#5DE0DC')
        self.topics = Label(self, text='Click on an article to see more info', wraplength=500, font='times 16',
                            background='#383838', foreground='#5DE0DC', anchor=W, justify=LEFT)
        calltipwindow.createToolTip(self.topicsHead, "These are a few subjects that were mentioned in the article")

        # labels for results analysis
        self.resultTopicHead = Label(self, text='Most Mentioned Phrases in Results', font="times 16 underline",
                                     background='#282828', foreground='#5DE0DC')
        self.resultTopics = Label(self, text='Processing Data (0%)', wraplength=500, font='times 16',
                                  background='#383838', foreground='#5DE0DC', anchor=W, justify=LEFT)
        calltipwindow.createToolTip(self.resultTopicHead,
                                    "These are the most mentioned phrases in the resulting articles.")

        # helper class to improve code readability
        self.helper = cyhelper.SearchHelper(self)

        self.helper.showsearch()

    def search(self, url):
        # queue to share between gui and threads
        q = queue.Queue()
        self.helper.hidefilters()

        if SearchFrame.content is None:
            searchprogress = Progressbar(self, orient="horizontal", style='mongo.Horizontal.TProgressbar', length=700, mode="indeterminate")
            searchprogress.place(relx=.5, rely=.8, anchor=CENTER)
            searchprogress.start()

            proglabel = Label(self, text="Fetching Results...", font="Times 14", bg="#282828", fg="#FFFFFF")
            proglabel.place(relx=.5, rely=.765, anchor=CENTER)

            # get additional info from filters if they exist
            url = self.helper.addurlfilters(url)

            # start thread to get data from url
            thread = GetDataThread(url, q)
            thread.start()

            # wait until thread is done, then get data from queue
            self.updateuntildata(q, searchprogress)
            self.data = q.get(0)

            # get rid of progress bar
            searchprogress.destroy()
            proglabel.destroy()

        else:
            self.data = SearchFrame.content

        # make sure search didn't time out
        if self.data != "ReadTimeout":
            self.master.master.updateque.queue.clear()

            # start thread to analyze data and repeat process
            self.analysisthread = ResultsAnalysisThread(self.data, self.master.master.analyzer, q, self.resultTopics)
            self.analysisthread.start()

            self.resultTopics.config(text="Processing Data...(0%)")
            self.processingloop('percent')
            self.processingloop('dots')

            self.helper.hidesearch()

            style = Style(self)
            style.configure("Treeview", rowheight=30, fieldbackground='#bdbdbd')
            style.configure("Treeview.Heading", background="#707070", rowheight=60, font="Ariel 14 bold")
            self.tree = Treeview(self, columns=('date','title'), selectmode='browse')
            self.tree['show'] = 'headings'

            self.tree.column('date', width=100, anchor=CENTER)
            self.tree.heading('date', text="Date", command = lambda: self.treeview_sort_column(self.tree,'date',False))
            self.tree.column('title', width=900)

            self.tree.heading('title', text="Article Title", anchor=W, command = lambda: self.treeview_sort_column(self.tree,
                                                                                                         'title',False))
            self.tree.heading('title', text="Article Title", anchor=W,
                              command = lambda: self.treeview_sort_column(self.tree,'title',False))

            #self.tree.place(relx=.3, relheight=1, width=1200)
            self.tree.place(x=330, relheight=1, width=760)

            self.treeyscb = Scrollbar(self, orient="vertical", command=self.tree.yview)
            self.treeyscb.place(relx=1, rely=.5, relheight=1, anchor=E)

            self.tree.configure(yscrollcommand=self.treeyscb.set)

            self.treexscb = Scrollbar(self, orient="horizontal", command=self.tree.xview)
            self.treexscb.place(relx=.3, rely=.999, width=755, anchor=SW)


            self.tree.configure(xscrollcommand=self.treexscb.set)
            self.sf.place(relx=0, rely=.055, relwidth=.30, relheight=.4)

            self.topicsHead.place(relx=.01, rely=.024, relwidth=.28, relheight=.03)
            self.topics.place(relx=.01, rely=.065, relwidth=.28)


            # frame for results analysis
            self.sf2.place(relx=0, rely=.51, relwidth=.30, relheight=.4)


            self.resultTopicHead.place(relx=.01, rely=.475, relwidth=.28, relheight=.03)
            self.resultTopics.place(relx=.01, rely=.52, relwidth=.28)


            # New Search Edit Search Save Search
            self.new_search = Button(self, text='New Search', background='#383838', foreground='#5DE0DC',
                                     font="Veranda 14", command=self.NewSearch)
            self.edit_search = Button(self, text='Edit Search', background='#383838', foreground='#5DE0DC',
                                      font="Veranda 14", command=self.EditSearch)
            self.save_search = Button(self, text='Save Search', background='#383838', foreground='#5DE0DC',
                                      font="Veranda 14", command=self.saveMenu)

            if self.data:
                for count,item in enumerate(self.data):
                    # remove BOM images first from body >uffff
                    item['body'] = ''.join(c for c in unicodedata.normalize('NFC', item['body']) if c <= '\uFFFF')
                    tagname = 'even' if count % 2 == 0 else 'odd'
                    self.tree.insert('', 'end',
                                     values=(parser.parse(item['date']).strftime('%m/%d/%y'), item['title'], item['uri'], item['author'], item['body']),
                                     tag=tagname)

                self.tree.tag_configure('even', font='Verdana 14', background="#9fedea")
                self.tree.tag_configure('odd', font='Verdana 14', background="#dedede")
                self.tree.bind('<Double-1>', self.on_click)
                self.tree.bind('<<TreeviewSelect>>', self.on_single_click)

                self.treeview_sort_column(self.tree,'date',True)


            else:
                self.topics.config(text='No Articles Matching Search')
                self.resultTopics.config(text='')

            self.new_search.place(relx=0, rely=.95, relwidth=.1, relheight=.05, anchor=NW)
            if SearchFrame.content is None:
                self.edit_search.place(relx=.1, rely=.95, relwidth=.1, relheight=.05, anchor=NW)
                if len(self.data) > 0:
                    self.save_search.place(relx=.2, rely=.95, relwidth=.1, relheight=.05, anchor=NW)

        else:
            messagebox.showerror("Too Broad", "Search is too broad. Try refining with filters.")
            self.helper.ent_keyword.focus_set()

        SearchFrame.content = None
        pass

    def NewSearch(self):
        self.analysisthread.stopthread()
        self.deletesearch()
        self.helper.resetsearch()
        self.helper.showsearch()


    def EditSearch(self):
        self.analysisthread.stopthread()
        self.deletesearch()
        self.helper.showsearch()

    def saveMenu(self):
        # create main directory and subdir(current date) if not made already
        path = os.getcwd() + "/Sessions/" + str(datetime.date.today())
        if not os.path.exists(path):
            os.makedirs(path)
        # get a filename from the user or default to current time
        currentTime = datetime.datetime.now().strftime("%H_%M_%S")

        filename = filedialog.asksaveasfilename(defaultextension="txt", initialdir=path, initialfile=currentTime)
        if filename:
            self.saveFilename = filename
            with open(filename, 'w') as outfile:
                json.dump(self.data, outfile)
            # with open(filename, 'w') as f:
            #     f.write("Testing Save As/No Current Save")


    #defind clear search
    def deletesearch(self):
        self.tree.destroy()
        self.sf.place_forget()
        self.topicsHead.place_forget()
        self.topics.place_forget()
        self.sf2.place_forget()
        self.resultTopicHead.place_forget()
        self.resultTopics.place_forget()
        self.new_search.destroy()
        self.treexscb.destroy()
        self.treeyscb.destroy()
        try:
            self.edit_search.destroy()
            self.save_search.destroy()
        except AttributeError:
            pass

    #on click gets the articles information and displays it in the Key Article Subjects window
    def on_single_click(self, event):
        self.topicsHead.config(text="Key Article Subjects")
        item = self.tree.item(self.tree.selection()[0], 'values')
        topicStr = '\n\n'.join(['\n    '.join(textwrap.wrap('\u27a2' + phrase[0], width=33)) for phrase in
                                self.master.master.analyzer.getMostCommonNounPhrases(5, [item[4]],
                                                                                     threading.Event(), 'one')])
        self.topics.config(text=topicStr)

    #on d click will open the article for display
    def on_click(self, event):
        try:
            item = self.tree.selection()[0]
        except IndexError:
            return

        self.n = self.tree.item(item, 'values')
        tw = Toplevel(self)
        xoffset = int(self.winfo_screenwidth() / 2 - 1280 / 2)
        yoffset = int(self.winfo_screenheight() / 2 - 800 / 2)
        tw.geometry("%dx%d+%d+%d" % (800, 600, xoffset, yoffset))  # set geometry of window
        tw.title(self.n[1])
        tb = Text(tw, width=90, height=40, font="Times 14", wrap=WORD)

        makemenu.ArticleMenu(tw, tb, self.n)

        tb.insert('end', self.n[4])
        tb.config(state=DISABLED)
        link = Label(tw, text=self.n[2])
        link.configure(foreground='blue', cursor='hand2')
        link.bind('<1>', self.op_link)
        auth = Label(tw, text='Author: ' + self.n[3])
        articledate = Label(tw, text='Date Published: ' + self.n[0])

        # window formatting for tw
        link.place(x=0, y=0, relwidth=1)
        tb.place(y=20, relwidth=1, relheight=1)
        auth.pack(side=LEFT, anchor='sw')
        articledate.pack(side=RIGHT, anchor='se')
    # op_link "double click on the link at the top of the page opens up the url link
    def op_link(self, event):
        webbrowser.open_new(self.n[2])

    def callEnable(self, event, searchtype):
        self.helper.callenable(event, searchtype)

    def updateuntildata(self, q, progress):
        while q.empty():
            time.sleep(.01)
            progress.step(1)
            progress.master.update()

    def processingloop(self, updatetype):
        string = self.resultTopics.cget('text')
        if len(string) and string[0] == 'P':
            if updatetype == 'percent':
                if not self.master.master.updateque.empty():
                    string = "{}({}%)".format(re.search('Processing Data(\.|\s)*', string).group(0), str(self.master.master.updateque.get(0)))
                    self.after(300, lambda: self.processingloop('percent'))
                else:
                    self.after(100, lambda: self.processingloop('percent'))
            elif updatetype == 'dots':
                numdots = len(string.split('.')) % 4
                string = "Processing Data" + numdots * '.' + (3 - numdots) * ' ' + re.search('\(.+\)', string).group(0)
                self.after(300, lambda: self.processingloop('dots'))

        self.resultTopics.config(text=string)

    def treeview_sort_column(self, tv, col, reverse=False):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        if col == 'date':
            l.sort(key=lambda t: "{}/{}/{}".format(t[0].split('/')[2],t[0].split('/')[0],t[0].split('/')[1]), reverse=reverse)
        else:
            l.sort(key=lambda t: t[0], reverse=reverse)

        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        for count, child in enumerate(tv.get_children()):
            tagn = 'even' if count % 2 == 0 else 'odd'
            tv.item(child, tag=tagn)

        tv.heading(col,
                   command=lambda: self.treeview_sort_column(tv, col, not reverse))


class StartFrame(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller  # set the controller
        self.title = "CySpyder"              #ttile of the window
        path = os.getcwd() + '\\resources\spiderweb2.jpg'
        self.img = ImageTk.PhotoImage(Image.open(path))
        self.panel = Label(self, image=self.img)
        self.panel.pack()

        #Progress Bar
        self.s = Style()
        self.s.theme_use('clam')
        self.s.configure("mongo.Horizontal.TProgressbar", foreground='#38494C', background='#5AE9FF')
        self.progress = Progressbar(self, orient="horizontal", style='mongo.Horizontal.TProgressbar',
                                    length=700, mode="determinate")
        self.controller.attributes('-transparentcolor', '#38494C')

        #Menu Frame window
        self.style = Style()
        self.style.configure('My.TFrame', background='#434343')
        self.sf = Frame(self, width=179, height=76, style='My.TFrame')
        self.sf['relief']='sunken'

        #todo to be populated with old searches to be able to reopen.
        self.menutree = Treeview(self)
        self.menutree.column('#0', stretch=True)

        #Menu Labels
        self.wl= Label(self, text='Welcome', width=24, font='ariel 18')
        self.wl.configure(background='#434343', foreground='#06c8e6', relief='groove')
        self.ns = Label(self, text='-New Session-', width=24, height=1, relief='raised', font="ariel 12 bold")
        self.ns.configure(height=2, background='#828282', foreground='#06c8e6')
        self.ns.bind('<1>', self.start)
        self.ns.bind('<Enter>', self.enter)
        self.ns.bind('<Leave>', self.leave)
        self.rs = Label(self, text='Recent Searches', width=28,height=2, bd=3, relief='ridge', font="Ariel 12 bold underline")
        self.rs.configure(background='#434343', foreground='#06c8e6')

        #window placements
        self.sf.place(relx=.625, rely=.5, relwidth=.26, relheight=.22, anchor=CENTER)
        self.wl.place(relx=.624, rely=.449, relwidth=.25, relheight=.1, anchor=CENTER)
        self.ns.place(relx=.626, rely=.555, relwidth=.25, relheight=.10, anchor=CENTER)
        self.rs.place(x=0, relwidth=.25, relheight=.1)
        self.menutree.place(x=0,rely=.045, relwidth=.25, relheight=.92)
        self.progress.place(y=435)

        self.bytes = 0
        self.maxbytes = 0
        self.openMenu()

    def openMenu(self):
        # set initial directory to savedScans folder
        path = os.path.join(os.getcwd(), "Sessions")
        filenames = os.listdir(path)

        for file in filenames:
            filetoprint = file.replace('2017-', '')
            self.menutree.insert('', 'end', text=filetoprint, tags='date')
            self.menutree.tag_configure('date', background='grey', foreground='yellow', font='bold, 11')
            path= os.path.join(os.getcwd(), 'Sessions'+'\\'+file)
            psr = os.listdir(path)
            for f in psr:
                filetoprint = f.replace('.txt', '')
                filetosend = f#.replace(' ', '')
                self.menutree.insert('', 'end', text='  -'+filetoprint, values=(file,filetosend), tags='article')
                self.menutree.tag_configure('article', background='#434343', foreground='#06c8e6', font='bold, 12')
            self.menutree.bind('<<TreeviewSelect>>', self.onmenuclick)

        #fill tree with greay past files
        for i in range(1,20):
            self.menutree.insert('', 'end', text='', tags='clean')
            self.menutree.tag_configure('clean', background='#434343')

    def onmenuclick(self, event):
        item = self.menutree.item(self.menutree.selection()[0], 'values')
        path = 'Sessions'+'\\'+item[0]+'\\'+item[1]
        with open(path, "r") as fin:
            SearchFrame.content = json.load(fin)
        self.start(event='open file')

    def start(self, event):
        self.progress["value"] = 0
        self.maxbytes = 50000
        self.progress["maximum"] = 50000
        self.after(400, self.master.master.analyzer.loadSpacy)
        self.read_bytes(event)

    def read_bytes(self, event):
        # simulate reading 500 bytes; update progress bar
        self.bytes += 1500
        self.progress["value"] = self.bytes
        if self.bytes < self.maxbytes:
            # read more bytes after 100 ms
            self.after(25, lambda e = event: self.read_bytes(e))
        else:
            self.welcomewindowing()
            if event == "open file":
                self.master.master.frames['SearchFrame'].helper.hidesearch()
                self.master.master.frames['SearchFrame'].search('')
    def welcomewindowing(self):
        xoffset = int(self.winfo_screenwidth() / 2 - 1280 / 2)
        yoffset = int(self.winfo_screenheight() / 2 - 800 / 2)
        self.controller.geometry("%dx%d+%d+%d" % (1100, 700, xoffset, yoffset))  # set geometry of window
        self.controller.show_frame('SearchFrame')

    def enter(self, event):
        self.ns.config(bg="#d3d3d3")
    def leave(self, event):
        self.ns.config(bg="#828282")


class GetDataThread(threading.Thread):
    def __init__(self, url, q):
        threading.Thread.__init__(self)
        self.queue = q
        self.url = url
    def run(self):
        try:
            data = requests.get(self.url, timeout=10).json()
            self.queue.put(data)
        except requests.exceptions.ReadTimeout:
            self.queue.put(requests.exceptions.ReadTimeout.__name__)


class ResultsAnalysisThread(threading.Thread):
    def __init__(self, data, analyzer, q, widget):
        threading.Thread.__init__(self)
        self.queue = q
        self.data = data
        self.analyzer = analyzer
        self.widget = widget
        self.stop = threading.Event()
    def run(self):
        results = '\n\n'.join(
            ['\n'.join(textwrap.wrap('\u27a2({}): '.format(phrase[1]) + str(phrase[0]), width=33)) for phrase in
             self.analyzer.getMostCommonNounPhrases(5, [item['body'] for item in self.data], self.stop, 'all')])
        try:
            self.widget.config(text=results)
        except TclError:
            pass
    def stopthread(self):
        self.stop.set()

if __name__ == "__main__":
    app = cyberapi()
    app.mainloop()