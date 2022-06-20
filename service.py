from tkinter import *
from tkinter import ttk

from search import Search
from query_refiner import SpellCorrector
import lucene
from synonym import Synonym

class MyApp:
    def __init__(self, parent, source):
        self.myParent = parent

        # Search functionality
        self.search_container = LabelFrame(parent, text="Wikipansion Search App")
        self.search_container.grid(row=0, column=0, sticky=W, padx=5, pady=4)
        self.search_container.config(background="#D5D2D1")

        self.search_entry = Entry(self.search_container, width=40)
        self.search_entry.pack(side=TOP, padx=8, pady=16)
        self.search_entry.bind("<Return>", self.submitclick)
        self.search_entry.focus_set()

        self.search_button = Button(self.search_container, width=15)
        self.search_button["text"] = "Search"
        self.search_button.pack(side=BOTTOM, pady=12)
        self.search_button.bind("<Button-1>", self.submitclick)



        # log details
        self.log_container = Frame(parent)
        self.log_container.grid(row=0, column=1, columnspan=2, padx=10, pady=10)
        self.log_container.config(background="#D5D2D1")

        self.log_detail = Text(self.log_container, wrap="word", height=8,
                               width=70,
                               foreground="black",
                               bg="white")
        self.log_detail.config(background="#D5D2D1", highlightbackground="green", highlightcolor="green")
        self.log_detail.pack(side=RIGHT)

        self.source_button = Button(self.log_container)
        self.source_button["text"] = "Thesaurus"
        self.source_button.pack(side=LEFT, pady=12)
        self.source_button.bind("<Button-2>", self.change_source)

        # result output
        self.output_container = Frame(parent)
        self.output_container.grid(row=1, column=0, columnspan=3, padx=4, pady=4)
        self.output_detail = Text(self.output_container, wrap="word", height=35,
                           width=110,
                           foreground="black",
                           bg="white")
        self.output_detail.config(background="#D5D2D1")

        self.output_detail.pack(side=BOTTOM)
        self.output_detail.delete("1.0", "end-1c")
        #self.expansion_model = Synonym("wordnet")
        self.expansion_model = Synonym(source)
        self.log_detail.insert(END, "Synonym source: " + str(self.expansion_model.get_source()) + "\n")

    def change_source(self, event):
        if self.source_button["text"].lower() == "Thesaurus".lower():
            self.source_button.config(text="WordNet")
            self.expansion_model.set_source("wordnet")

        else:
            self.source_button.config(text="Thesaurus")
            self.expansion_model.set_source("thesaurus")
        print(str(self.expansion_model.get_source()))
        self.log_detail.delete('1.0', END)
        self.log_detail.insert(END, "Synonym source: " + str(self.expansion_model.get_source()) + "\n")

    def wikipansion(self, query):
        corrected_spell = SpellCorrector(query).get_correction()
        return corrected_spell

    def submitclick(self, event):
        textin = self.search_entry.get()
        self.searchEngine(textin)
        #self.myParent.destroy()

    def get_synonym(self, query):
        synonyms = self.expansion_model.synonym_antonym_extractor(query)
        print("possible synonyms:", synonyms)
        return synonyms


    def searchEngine(self, query):
        # clean output box
        self.output_detail.delete('1.0', END)

        corrected_query = self.wikipansion(query)

        self.log_detail.insert(END, "Original query: " + str(corrected_query)  + "\n")
        self.output_detail.insert(END, "The search results are showing for : " + str(corrected_query))

        expand = self.get_synonym(corrected_query)
        expanded_q = "".join([i + ", " for i in expand])
        self.output_detail.insert(END, "\n")
        self.output_detail.insert(END, "The query expansions : " + expanded_q)
        self.log_detail.insert(END, "Expanded query: " + expanded_q + "\n")

        self.output_detail.insert(END, "\n")
        self.output_detail.insert(END, "\n")
        search = Search(corrected_query + " " + "".join([i+" " for i in expand]))

        hits = search.searchModule()
        print(str(len(hits))+ " documents have been retrieved.")
        for hit in hits:
        #     print("----------------------")
        #     print("Score :" + str(hit.score))
            doc = search.searchDoc(hit)
        #     print(" Title :" + str(doc.get("Title")))
        #     print(" ID :" + str(doc.get("ID")))
        #     print(" Text :" + str(doc.get("Context")))
        #     print("----------------------")
            self.output_detail.insert(END, str(doc.get("Title")))
            self.output_detail.insert(END, "\n \t " + str(doc.get("Context")))
            self.output_detail.insert(END, "\n")
            self.output_detail.insert(END, "\n")
            self.output_detail.insert(END, "\n")


root = Tk()
root.geometry("1050x750")
root.config(background="#B4B4B4")
myapp = MyApp(root, "thesaurus")
root.title('Search')
storeDir = "index"
lucene.initVM(vmargs=['-Djava.awt.headless=true'])
root.mainloop()