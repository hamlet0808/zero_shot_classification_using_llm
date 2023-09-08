import shutil
import os
import openai
import json
import time
import docx
import pytesseract
import string

from pdf2image import convert_from_path
from PyPDF2 import PdfReader

openai.api_key = ""

def getDocxText(filename):
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs[:10]:
        fullText.append(para.text)
    return '\n'.join(fullText)

def get_pdf_paths(root):
    result = []
    for path, dirs, files in os.walk(root):
        for name in files:
            if not name.lower().endswith('.pdf'):
                continue 
            result.append(os.path.join(path, name))
    return result

def get_txt_from_img(path):
    pages = convert_from_path(path, 500)
    for pageNum,imgBlob in enumerate(pages[:1]):
        text = pytesseract.image_to_string(imgBlob,lang='eng')
    return text


# def classify(file_name):

#
#
#     #print(text)
#     system_msg = "Act as an assistant of the lawyer."
#
#     query = """
#             Classify the document above to one of provided classes.
#             VERY IMPORTANT: Your response will be a single Label from the following labels-
#
#             label:
#             """
#
#     #prompt = "Classify the sentiment of the following text: 'This is a positive review.' Options: Positive, Negative, Neutral"
#
#     #print(text)
#     user_msg = text + "\n\n" + query
#     print(user_msg)
#
#     # Your request code here
#     return response["choices"][0]["message"]["content"]

def clean_openai_response(response):
    translator = str.maketrans('', '', string.punctuation)
    cleaned_string = response.translate(translator)
    if cleaned_string.startswith("label"):
        cleaned_string = cleaned_string[len("label"):].strip()
    return cleaned_string

def classify_cat_gpt(file_name, categories):
    name = file_name.split("/")[-1]  # Extract the file name
    parts = name.split(".")  # Split the file name by periods

    if len(parts) > 1:
        extension = "." + parts[-1]

    if extension == '.docx':
        text = getDocxText(file_name)
    elif extension == '.pdf':
        pdf_reader = PdfReader(file_name)
        text = ""
        for page in pdf_reader.pages[:1]:  ### question
            text += page.extract_text()
            if not text:
                text = get_txt_from_img(file_name)
    else:
        return None

    user_message =f"""
    <<content>>
    {text}
    <<content>>
    Given the above content, classify it into one of the following types \n {categories}",\n \
    VERY IMPORTANT: Your response will be a single type from provided categories.\

    Label:
    """
    
    #print(user_message)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", # engine = "deployment_name".
        messages=[
            {"role": "system", "content": "Act as an assistant of the lawyer"},
            {"role": "user", "content":user_message},
        ],
        temperature = 0.0,
        max_tokens = 20
    )
    return response['choices'][0]['message']['content']


if __name__ == "__main__":
    list_of_files = get_pdf_paths('Evio-Full/')
    categories = ['Certificate of Incorporation',
     'Amended & Restated Certificate of Incorporation', 'Bylaws',
     'Board Consent', 'Stockholder Consent', 'Stock Plan', 'Assignment Seperate From Certificate', 'Sales Agreement','Form 1120','Restricted Stock Purchase Agreement Amendment',
     'Restricted Stock Purchase Agreement','Investment Representation Statement','Stock Certificate','Restricted Stock Award Agreement','Investor Report','Compliance Certificate',
     '83(b) election', 'Stock Power', 'Spousal Consent', 'Receipt', 'Stock Option Agreement', 'Stock Option Grant Notice', 'Stock Option Exercise Agreement',
     'Early Exercise Stock Purchase Agreement', 'SAFE (Simple Agreement for Future Equity)', 'Pro Rata Agreement', 'Convertible Note Purchase Agreement','Convertible Promissory Note',
     'Preferred Stock Purchase Agreement', 'Disclosure Schedule', 'Warrant', 'Offer Letter', 'Employee Proprietary Information and Inventions Assignment Agreement',
     'Consultant Proprietary Information and Inventions Assignment Agreement','Separation Agreement', 'Consulting Agreement', 'Consultant Termination Notice', 'Advisor Agreement',
     'Patent', 'Employee Handbook','Form W-9', 'Form W-8BEN', 'Advisor Termination Notice', 'Technology Assignment Agreement', 'Indemnity Agreement',
     'Management Rights Letter', 'Investors’ Rights Agreement', 'Amended and Restated Investors’ Rights Agreement', 'Form I-9','Form W-4',
     'Voting Agreement', 'Amended and Restated Voting Agreement', 'Right of First Refusal and Co-Sale Agreement','Vendor Agreement',"Secretary's Certificate",
     'Amended & Restated Right of First Refusal and Co-Sale Agreement', 'Non-Disclosure Agreement (also known as Confidentiality Agreement)',
     'Master Services Agreement', 'Employer Identification Number', 'Employer Identification Number Application (Form SS-4)','Delaware Annual Franchise Tax Report']

    result_dict = {}
    # path = "CartaSAFE.pdf"
    # doc_type = classify_cat_gpt(path,categories)
    # print(doc_type)

    for doc in list_of_files:
        time.sleep(3)
        # current_path = 'Evio-Full/' + doc
        print(doc)
        doc_type = classify_cat_gpt(doc,categories)
        cleaned_label = clean_openai_response(doc_type.lower())
        print(cleaned_label)
        
        for item in categories:
            cleaned_category = clean_openai_response(item.lower())
            if cleaned_label == cleaned_category:
                result_dict[doc] = item
                break
            else:
                result_dict[doc] = 'Not classified:' + doc_type
        #print(doc)
        print("**********")
    
        with open("res_new_version_test_new_last.json", "w") as outfile:
            json.dump(result_dict, outfile, indent=4)

