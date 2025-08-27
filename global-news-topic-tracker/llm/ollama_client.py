
from langchain_community.llms import Ollama
from langchain.chains import load_summarize_chain
from langchain_community.document_loaders import WebBaseLoader

def get_summary(url):
    loader = WebBaseLoader(url)
    docs = loader.load()

    llm = Ollama(model="mistral", temperature=0)
    chain = load_summarize_chain(llm, chain_type="stuff")

    summary = chain.run(docs)
    return summary
