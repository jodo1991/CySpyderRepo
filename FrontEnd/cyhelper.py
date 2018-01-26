from tkinter import Label, StringVar, IntVar, Radiobutton, Entry, Checkbutton, Button
from tkinter import CENTER, E, W
from tkinter.ttk import Combobox
import calltipwindow
from time import strftime


class SearchHelper:

    def __init__(self, searchframe):
        self.frame = searchframe

        # keyword entry
        largefont = ('Veranda', 24)
        self.ent_keyword = Entry(self.frame, width=40, relief='raised', font=largefont, bd=1)
        # todo <Return> and entry is not empty call search()

        self.but_search = Button(self.frame, text='Search', width=15, state='disable', font="Veranda 16",
                                 command=lambda: self.frame.search(
                                     'http://cbrown686-test.apigee.net/cyberapi/articles?q=keywordtitlebody&title='
                                     + self.ent_keyword.get() + '&body=' + self.ent_keyword.get()))

        self.var = IntVar()
        self.var.set(0)
        self.check_filter = Checkbutton(self.frame, text="Advanced Filter", onvalue=1, offvalue=0, variable=self.var,
                                        command=self.filter_op, font="Veranda 16")
        calltipwindow.createToolTip(self.check_filter, "Click here for options to narrow your search")

        calltipwindow.createToolTip(self.ent_keyword, "Enter a word or phrase here to search by.")
        self.ent_keyword.bind('<Escape>', self.clear_text)
        self.ent_keyword.bind('<Key>', lambda event: self.callenable(event, 'DefaultSearch'))

        if self.var.get():
            self.frame.searchButton(None)

        # filter stuff
        self.appearing_label = Label(searchframe, text='Appearing In:', background='#282828',
                                     font=15, foreground='#5DE0DC')
        self.box_value = StringVar()
        self.box = Combobox(searchframe, textvariable=self.box_value)
        calltipwindow.createToolTip(self.appearing_label, "Select where you want us to search "
                                                          "for your provided search phrase.")
        calltipwindow.createToolTip(self.box, "Select where you want us to search "
                                              "for your provided search phrase.")
        self.box['values'] = ('Default', 'Title', 'Body', 'URL')
        self.box.current(0)
        self.box.bind('<<ComboboxSelected>>', self.setbaseurl)

        # author
        self.author_label = Label(searchframe, text='Author:', background='#282828', font="veranda 12", foreground='#5DE0DC')
        self.author_entry = Entry(searchframe, width=22, bd=2, background='#9A9A9A')
        calltipwindow.createToolTip(self.author_label,
                                    "Enter an author's first and/or last name (not case-sensitive).")
        calltipwindow.createToolTip(self.author_entry,
                                    "Enter an author's first and/or last name (not case-sensitive).")

        # subjectivity
        self.fsub_label = Label(searchframe, text='Subjectivity:', background='#282828', font="veranda 12", foreground='#5DE0DC')
        calltipwindow.createToolTip(self.fsub_label, "Choose an option here if you only want to see articles"
                                                     " that are more objectively or subjectively written")
        self.var2 = IntVar()
        self.var2.set(1)
        self.fsub_nv = Radiobutton(searchframe, text="Don't Care", variable=self.var2, value=1, background='#282828',
                                   foreground='#5DE0DC')
        calltipwindow.createToolTip(self.fsub_nv,
                                    "Select this if you want all articles returned regarless of how they are written.")
        self.fsub_gt = Radiobutton(searchframe, text='More Subjective', variable=self.var2, value=2,
                                   background='#282828', foreground='#5DE0DC')
        calltipwindow.createToolTip(self.fsub_gt,
                                    "Select this if you only want articles that are more subjectively written.")
        self.fsub_lt = Radiobutton(searchframe, text='More Objective', variable=self.var2, value=3,
                                   background='#282828', foreground='#5DE0DC')

        calltipwindow.createToolTip(self.fsub_lt,
                                    "Select this if you only want articles that are more objectively written.")
        # date
        self.fD_label = Label(searchframe, text='Date:', background='#282828', font="veranda 12", foreground='#5DE0DC')
        self.fD_format = Label(searchframe, text='00/00/0000', background='#282828', foreground='#BBBBBB')
        self.fD_format.configure(foreground='grey')
        self.fD_beinlab = Label(searchframe, text='From:', background='#282828', foreground='#BBBBBB')
        self.fD_endlab = Label(searchframe, text='To:', background='#282828', foreground='#BBBBBB')
        self.fD_ent = Entry(searchframe, width=10, bd=2, background='#9A9A9A')
        self.fD_ent.insert('end', '01/01/0001')
        self.fD_ent2 = Entry(searchframe, width=10, bd=2, background='#9A9A9A')
        self.fD_ent2.insert('end', strftime('%m/%d/%Y'))

        calltipwindow.createToolTip(self.fD_label, "Narrow your results to articles published in the dates here.")
        calltipwindow.createToolTip(self.fD_format, "Narrow your results to articles published in the dates here.")
        calltipwindow.createToolTip(self.fD_beinlab, "Narrow your results to articles published in the dates here.")
        calltipwindow.createToolTip(self.fD_endlab, "Narrow your results to articles published in the dates here.")
        calltipwindow.createToolTip(self.fD_ent, "Enter Start Date here.")
        calltipwindow.createToolTip(self.fD_ent2, "Enter End Date here.")

        # filter placements
        offset = 100
        self.appearing_label.place(relx=.364, y=380 + offset)

        # appearing pick
        self.box.place(x=510, y=380 + offset)

        # author label
        self.author_label.place(x=400, y=405 + offset)

        # author entry
        self.author_entry.place(x=510, y=405 + offset)

        # subjectivity
        self.fsub_label.place(x=400, y=430 + offset)
        self.fsub_nv.place(x=510, y=430 + offset)
        self.fsub_gt.place(x=510, y=455 + offset)
        self.fsub_lt.place(x=510, y=480 + offset)

        # date
        self.fD_label.place(x=400, y=505 + offset)
        self.fD_format.place(x=445, y=507 + offset)
        self.fD_beinlab.place(x=510, width=45, y=505 + offset)
        self.fD_ent.place(x=555, width=65, y=505 + offset)
        self.fD_endlab.place(x=630, y=505 + offset)
        self.fD_ent2.place(x=660, width=65, y=505 + offset)

        # buttons
        self.but_search.place(relx=.505, rely=.6, anchor=W)

        # ENTRY BOX for keyword
        self.ent_keyword.place(relx=.5, rely=.5, anchor=CENTER)

        # check button
        self.check_filter.place(relx=.495, rely=.6, relheight=.059, anchor=E)

        self.hidefilters()

    #filter options populate uppon check box of Advanced search option
    def filter_op(self):
        if self.var.get() is 1:
            self.showfilters()
        else:
            self.hidefilters()

    def resetsearch(self):
        self.ent_keyword.destroy()
        self.but_search.destroy()
        self.check_filter.destroy()

        self.appearing_label.destroy()
        self.box.destroy()
        self.author_label.destroy()
        self.author_entry.destroy()
        self.fsub_label.destroy()
        self.fsub_nv.destroy()
        self.fsub_gt.destroy()
        self.fsub_lt.destroy()
        self.fD_label.destroy()
        self.fD_format.destroy()
        self.fD_ent.destroy()
        self.fD_beinlab.destroy()
        self.fD_endlab.destroy()
        self.fD_ent2.destroy()
        self.__init__(self.frame)

    def hidefilters(self):
        self.appearing_label.lower()
        self.box.lower()
        self.author_label.lower()
        self.author_entry.lower()
        self.fsub_label.lower()
        self.fsub_nv.lower()
        self.fsub_gt.lower()
        self.fsub_lt.lower()
        self.fD_label.lower()
        self.fD_format.lower()
        self.fD_ent.lower()
        self.fD_beinlab.lower()
        self.fD_endlab.lower()
        self.fD_ent2.lower()

    def showfilters(self):
        self.appearing_label.lift()
        self.box.lift()
        self.author_label.lift()
        self.author_entry.lift()
        self.fsub_label.lift()
        self.fsub_nv.lift()
        self.fsub_gt.lift()
        self.fsub_lt.lift()
        self.fD_label.lift()
        self.fD_format.lift()
        self.fD_ent.lift()
        self.fD_beinlab.lift()
        self.fD_endlab.lift()
        self.fD_ent2.lift()

    def showsearch(self):
        self.ent_keyword.lift()
        self.but_search.lift()
        self.check_filter.lift()

        if self.var.get():
            self.showfilters()

    def hidesearch(self):
        self.ent_keyword.lower()
        self.but_search.lower()
        self.check_filter.lower()

    def setbaseurl(self, event):
        if self.box.current() is 0:
            self.but_search.config(command=lambda: self.frame.search(
                'http://cbrown686-test.apigee.net/cyberapi/articles?q=keywordtitlebody&title='
                + self.ent_keyword.get() + '&body=' + self.ent_keyword.get()))
        elif self.box.current() is 1:
            self.but_search.config(command=lambda: self.frame.search(
                'http://cbrown686-test.apigee.net/cyberapi/articles?q=keywordtitle&title=' + self.ent_keyword.get()))
        elif self.box.current() is 2:
            self.but_search.config(command=lambda: self.frame.search(
                'http://cbrown686-test.apigee.net/cyberapi/articles?q=bodyonly&body=' + self.ent_keyword.get()))
        elif self.box.current() is 3:
            self.but_search.config(command=lambda: self.frame.search(
                'http://cbrown686-test.apigee.net/cyberapi/articles?q=uri&uripath=' + self.ent_keyword.get()))

    def addurlfilters(self, url):
        if self.var.get():
            au = self.author_entry.get()
            au = au.replace(' ', '+')
            # var2 is the state of the radio check button
            if self.var2.get() == 2:
                url = url + '&author=' + au + '&sub=gt&sdate=' + self.fD_ent.get() + '&edate=' + self.fD_ent2.get()
                # print(url)
            elif self.var2.get() == 3:
                url = url + '&author=' + au + '&sub=gt&sdate=' + self.fD_ent.get() + '&edate=' + self.fD_ent2.get()
            else:
                url = url + '&author=' + au + '&sub=&sdate=' + self.fD_ent.get() + '&edate=' + self.fD_ent2.get()
        else:
            url = url + '&author=&sub=&sdate=01/01/0001&edate=' + strftime('%m/%d/%Y')

        return url

    # Hitting escape when editing the ENTRY box will clear it and disable the search button from being able to be used.
    def clear_text(self):
        self.ent_keyword.delete(0, 'end')
        self.but_search.configure(state='disable')

    def callenable(self, event, searchtype):
        self.frame.after(100, lambda: self.enablesearch(event, searchtype))

    # event bind when Return is entered after a title keyword is entered will enable the search button.
    def enablesearch(self, event, searchtype):
        string = ''
        if searchtype == 'DefaultSearch':
            string = self.ent_keyword.get()
        if string.strip() != '':
            self.but_search.configure(state='normal')
        else:
            self.but_search.configure(state='disabled')