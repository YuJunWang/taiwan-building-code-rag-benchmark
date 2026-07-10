from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
try:
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    res = llm.invoke("Hello")
    print(res.content)
except Exception as e:
    print("Error:", e)
