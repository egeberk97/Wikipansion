from search import Search
from query_refiner import SpellCorrector
import lucene
import streamlit as st


query = st.text_input("PLease enter your search here!")

def wikipansion(query):
    corrected_spell = SpellCorrector(query).get_correction()
    return corrected_spell



if __name__ == '__main__':
    storeDir = "index"
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    #
    # search = Search(wikipansion(query))
    #
    # hits = search.search()
    # st.text(str(len(hits)) + ' documents have been retrieved.')
    # for hit in hits:
    #     st.text("----------------------")
    #     st.text("Score :" + str(hit.score))
    #     doc = search.searchDoc(hit)
    #     st.text(" Title :" + str(doc.get("Title")))
    #     st.text(" ID :" +  str(doc.get("ID")))
    #     st.text(" Text :" + str(doc.get("Context")))
    #     st.text("----------------------")




