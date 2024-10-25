import tkinter as tk
from tkinter import scrolledtext

from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
import json


def generatore(lista__frasi):
    for s in lista__frasi:
        yield s


#Instantiation
llm = ChatOllama(
    model="llama3.2",
    temperature=0,
    )

#Chaining
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that provides emotion analysis for social network comments."
            "In output, just give one word for the emotion you infer from the sentence.",
        ),
        ("human", "{input}"),
    ]
)

chain = prompt | llm

def chat():
    x = text_area.get("1.0", tk.END).strip().splitlines()       
    msg = []
    inp = []
    for n in generatore(x):             
        result = chain.invoke({"input": n,})
        msg.append(result.content)
        inp.append(n)
        dictionary = dict(zip(inp, msg))
        for comment, emotion in dictionary.items():
            result_area.insert(tk.END, f"Comment: {comment} -> Emotion: {emotion}\n")



root = tk.Tk()
root.title("Emotion Analysis Tool")

# Area di input per i commenti
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
text_area.pack(padx=10, pady=10)

# Bottone per analizzare i commenti
analyze_button = tk.Button(root, text="Analyze Comments", command=chat)
analyze_button.pack(pady=5)

# Area di output per i risultati
result_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
result_area.pack(padx=10, pady=10)

# Avvio della GUI
root.mainloop()
