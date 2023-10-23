import os
import random
import langchain
import json
import random
import time

from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS #facebook AI similarity search
from langchain.chains import RetrievalQA
from langchain import HuggingFaceHub
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain

from dotenv import load_dotenv
from PyPDF2 import PdfReader

langchain.verbose = True
 
def get_pdf_paths(root):
    
    result = []
    for path, dirs, files in os.walk(root):
        for name in files:
            if not name.lower().endswith('.pdf'):
                continue 

            result.append(os.path.join(path, name))

    return result


def main():
    load_dotenv()
    # st.set_page_config(page_title="Ask your PDF")
    # st.header("Ask Your PDF")
    repo_name = ("test/")
    # pdf = st.file_uploader("Upload your pdf",type="pdf")
    all_pdfs = get_pdf_paths(repo_name)
    
    sample_list = random.choices(all_pdfs, k=30)
    
    result_dict = {}
    
    for pdf in sample_list:
        time.sleep(1)
        try:
            pdf_reader = PdfReader(pdf)
            text = ""
            for page in pdf_reader.pages[:1]:  ### question
                text += page.extract_text()
            
            #print("text:", text)
    
            # spilit ito chunks
            text_splitter = CharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            chunks = text_splitter.split_text(text)

            # create embedding
            #embeddings = HuggingFaceEmbeddings()
            embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')
            
            if len(chunks) > 0:
                knowledge_base = FAISS.from_texts(chunks,embeddings)
            else:
                result_dict[pdf] = "Other"
                continue
                
            
            ### Prompt engineering
            template =  """
                        Extract from the following pieces of context the answer of the question at the end. 
                         
                        Context:
                        {context}
                        Question:
                        {question}
                        VERY IMPORTANT: Your response will be a single Label with maximum 5-10 words.
                        Label:
                        """
            
            QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
            
            ###Possible LLM changing
            model_name = "gpt-3.5-turbo" # gpt-4
            llm = ChatOpenAI(model_name=model_name, temperature=0, max_tokens=20)

            question = "What is the name or label of document?"
            docs = knowledge_base.similarity_search(question, k=2)
            
            chain = load_qa_chain(llm, chain_type="stuff", prompt=QA_CHAIN_PROMPT, verbose=False)
            print("path:", pdf)
            response = chain({"input_documents": docs, "question": question}, return_only_outputs=True)
            
            print('response', response['output_text'])
            result = response['output_text']
            
            if 'information' in result:
                result = 'Other'
                
            result_dict[pdf] = result
            
            with open("res_gpt_label_new_1.json", "w") as outfile:
                json.dump(result_dict, outfile, indent=4)
            
        except Exception as e:
            print(e)
            print(pdf)
        
        # print('path', pdf)

        
    
if __name__ == '__main__':
    main()
