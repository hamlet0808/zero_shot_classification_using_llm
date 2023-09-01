import shutil
import os
import openai
import json
import time

from PyPDF2 import PdfReader

openai.api_key = "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"


def get_pdf_paths(root):

    result = []
    for path, dirs, files in os.walk(root):
        for name in files:
            if not name.lower().endswith('.pdf'):
                continue 
            result.append(os.path.join(path, name))

    return result


def classify(file_name):

    pdf_reader = PdfReader(file_name)
    text = ""
    for page in pdf_reader.pages[:1]:  ### question
        text += page.extract_text()

    system_msg = "Act as an assistant of the lawyer."

    query = """
            Extract from the following pieces of context the answer of the question at the end
            What is the name or label of document in terms of law?
            VERY IMPORTANT: Your response will be a single Label with maximum 5-10 words.
            Label:
            """

    user_msg = text + "\n\n" + query
    
    print("zzzz")
    
        # Your request code here
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature = 0.0,
        max_tokens = 20
    )


    return response["choices"][0]["message"]["content"]


# def move_file(current_path, new_folder):
#     if os.path.isfile(current_path) and os.path.isdir(new_folder):
#         file_name = os.path.basename(current_path)
#         new_path = os.path.join(new_folder, file_name)
#         shutil.move(current_path, new_path)
#         print(f"File moved to {new_path}")

if __name__ == "__main__":
    list_of_files = get_pdf_paths('Evio-Full/')
    result_dict = {}
    for doc in list_of_files:
        time.sleep(1)
        # current_path = 'Evio-Full/' + doc
        print(doc)
        doc_type = classify(doc)
        print(doc_type)
        result_dict[doc] = doc_type
        
        #print(doc)
        print("**********")
    
        with open("res_new_version.json", "w") as outfile:
            json.dump(result_dict, outfile, indent=4)

