from tkinter import *
from search import Search
from query_refiner import SpellCorrector
import lucene
from synonym import Synonym

class MyApp:
    def __init__(self, parent):
        self.myParent = parent
        self.myContainer1 = LabelFrame(parent, text="Wikipansion Search App")
        self.myContainer2 = Frame(parent)
        self.myContainer3 = Frame(parent)
        self.myContainer1.grid()
        self.myContainer2.grid()
        self.myContainer3.grid()

        self.label1 = Message(self.myContainer1, text="")

        self.label1.pack()

        self.entryVariable = StringVar()
        self.textbox = Entry(self.myContainer1)
        self.textbox.pack(side=TOP)
        self.textbox.bind("<Return>", self.submitclick)
        self.textbox.focus_set()

        self.label2 = Label(self.myContainer1)
        self.label2["text"] = ""
        self.label2.pack(side=BOTTOM)

        self.label3 = Message(self.myContainer1, text="")
        self.label3.pack()

        self.button1 = Button(self.myContainer2)
        self.button1["text"] = "Search"
        self.button1.pack(side=BOTTOM)
        self.button1.bind("<Button-1>", self.submitclick)
        textbox = self.textbox

        self.Output = Text(self.myContainer3, height=50,
                      width=250,
                      foreground= "black",
                      bg="white")

        self.Output.pack(side=BOTTOM)
        self.Output.delete("1.0", "end-1c")
        self.expansion_model = Synonym("wordnet")


    def wikipansion(self, query):
        corrected_spell = SpellCorrector(query).get_correction()
        return corrected_spell

    def submitclick(self, event):
        textin = self.textbox.get()
        self.searchEngine(textin)

        #self.myParent.destroy()


    def get_synonym(self, query):
        synonyms = self.expansion_model.synonym_antonym_extractor(query)
        print("possible synonyms:", synonyms)
        return synonyms


    def searchEngine(self, query):

        self.Output.delete('1.0', END)
        corrected_query = self.wikipansion(query)
        search = Search(corrected_query)
        self.Output.insert(END, "The search results are showing for : "+ str(corrected_query))

        expand = self.get_synonym(query)
        self.Output.insert(END, "\n")
        self.Output.insert(END, "Possible expansions : " + str(expand))

        self.Output.insert(END, "\n")
        self.Output.insert(END, "\n")
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
            self.Output.insert(END, str(doc.get("Title")))
            self.Output.insert(END, "\n \t " + str(doc.get("Context")))
            self.Output.insert(END, "\n")
            self.Output.insert(END, "\n")
            self.Output.insert(END, "\n")


root = Tk()
root.geometry("1200x600")
myapp = MyApp(root)
root.title('Search')
storeDir = "index"
lucene.initVM(vmargs=['-Djava.awt.headless=true'])
root.mainloop()