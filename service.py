import tkinter
from tkinter import *
from datetime import datetime

from search import Search
from query_refiner import SpellCorrector
import lucene
from synonym import Synonym

class MyApp:
    def __init__(self, parent, source):
        self.myParent = parent

        # Search functionality
        self.search_container = LabelFrame(parent, text="Wikipansion Search App",foreground="black",font=('Helvetica', 18, 'bold'))
        self.search_container.grid(row=0, column=0, sticky=W, padx=5, pady=4)
        self.search_container.config(background="#D5D2D1")

        self.search_entry = Entry(self.search_container, width=40, background="white",foreground="black")
        self.search_entry.pack(side=TOP, padx=8, pady=20)
        self.search_entry.bind("<Return>", self.submitclick)
        self.search_entry.focus_set()

        self.search_button = Button(self.search_container, width=15, background="#D5D2D1")
        self.search_button["text"] = "Search"
        self.search_button.pack(side=BOTTOM, pady=12)
        self.search_button.bind("<Button-1>", self.submitclick)

        # log details
        self.log_container = Frame(parent)
        self.log_container.grid(row=0, column=1, columnspan=2, padx=10, pady=10)
        self.log_container.config(background="#D5D2D1")

        self.log_detail = Text(self.log_container, wrap="word", height=10,
                               width=70,
                               foreground="black",
                               bg="white")
        self.log_detail.config(background="#D5D2D1", highlightbackground="green", highlightcolor="green")
        self.log_detail.pack(side=RIGHT)

        '''
        self.source_button = Button(self.log_container)
        self.source_button["text"] = "Thesaurus"
        self.source_button.pack(side=LEFT, pady=12)
        self.source_button.bind("<Button-2>", self.change_source)
        '''

        # result output
        self.output_container = Frame(parent)
        self.output_container.grid(row=1, column=0, columnspan=3, padx=4, pady=4,sticky=W)
        self.output_detail = Text(self.output_container, wrap="word", height=40,
                           width=120,
                           foreground="black",
                           bg="white")
        self.output_detail.config(background="#D5D2D1")

        self.output_detail.pack(side=BOTTOM)
        self.output_detail.delete("1.0", "end-1c")
        #self.expansion_model = Synonym("wordnet")
        self.expansion_model = Synonym(source)
        self.log_detail.insert(END, "Synonym source: " + str(self.expansion_model.get_source()) + "\n")

        self.source = tkinter.StringVar()
        self.source.set("thesaurus")
        R1 = Radiobutton(self.log_container, text="Thesaurus", variable=self.source, value="thesaurus",
                         background="#D5D2D1", foreground="black", command=self.change_source)
        R1.pack(anchor=W)

        R2 = Radiobutton(self.log_container, text="WordNet", variable=self.source, value="wordnet",
                         background="#D5D2D1", foreground="black", command=self.change_source)
        R2.pack(anchor=W)

        R3 = Radiobutton(self.log_container, text="No expansion", variable=self.source, value="None",
                         background="#D5D2D1", foreground="black", command=self.change_source)
        R3.pack(anchor=W)


    def change_source(self):
        self.expansion_model.set_source(self.source.get())
        #self.log_detail.delete('1.0', END)
        self.log_detail.insert(END, "Synonym source: " + str(self.expansion_model.get_source()) + "\n")

    def wikipansion(self, query):
        corrected_spell = SpellCorrector(query).get_correction()
        return corrected_spell

    def submitclick(self, event):
        # clean output box
        self.output_detail.delete('1.0', END)
        textin = self.search_entry.get()
        if textin == "":
            self.output_detail.insert(END, "Query can not be empty")
        else:
            start_time = datetime.now()
            self.searchEngine(textin)
            end_time = datetime.now()
            delta_time = end_time-start_time
            msec = delta_time.seconds * 1000 + delta_time.microseconds / 1000
            self.output_detail.insert("1.0", "Top 5 articles are retrieved in {:.3f}".format(msec) + " milliseconds\n")
        #self.myParent.destroy()

    def get_synonym(self, query):
        synonyms = self.expansion_model.synonym_antonym_extractor(query)
        print("possible synonyms:", synonyms)
        return synonyms


    def searchEngine(self, query):
        self.output_detail.tag_configure("bold", font="Helvetica 12 bold")
        self.log_detail.insert(END, "Original Query: " + str(query) + "\n")
        corrected_query = self.wikipansion(query)

        self.log_detail.insert(END, "Corrected Query: " + str(corrected_query) + "\n")
        self.output_detail.insert(END, "The search results are showing for : " + str(corrected_query))

        expand = self.get_synonym(corrected_query)
        expanded_q = "".join([i + ", " for i in expand])
        self.output_detail.insert(END, "\n")
        #self.output_detail.insert(END, "The query expansions : " + expanded_q)
        self.log_detail.insert(END, "Expanded query: " + expanded_q + "\n")
        self.log_detail.insert(END, 70*"=" + "\n")

        self.output_detail.insert(END, "\n")
        self.output_detail.insert(END, "\n")
        search = Search(corrected_query + " " + "".join([i+" " for i in expand]))

        hits = search.searchModule()
        print(str(len(hits)) + " documents have been retrieved.")
        for hit in hits:
        #     print("----------------------")
        #     print("Score :" + str(hit.score))
            doc = search.searchDoc(hit)
        #     print(" Title :" + str(doc.get("Title")))
        #     print(" ID :" + str(doc.get("ID")))
        #     print(" Text :" + str(doc.get("Context")))
        #     print("----------------------")
            self.output_detail.insert(END, str(doc.get("Title")).upper(), "bold")
            self.output_detail.insert(END, "\n   " + str(doc.get("Context")))
            self.output_detail.insert(END, "\n")
            self.output_detail.insert(END, "\n")
            self.output_detail.insert(END, 120*"=" + "\n")


root = Tk()
root.geometry("1050x800")
root.config(background="#B4B4B4")
myapp = MyApp(root, "thesaurus")
root.title('Search')
storeDir = "index"
lucene.initVM(vmargs=['-Djava.awt.headless=true'])
root.mainloop()