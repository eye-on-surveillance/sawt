import os
import re
import pandas as pd
from docx import Document

def extract_ordinances(text):
    sections = re.split(r"\d+\w*\. ORDINANCES ON FIRST READING", text)
    
    ordinances_list = []
    for section in sections[1:]:  
        ordinances = re.split(r"\d+\w*\.", section)
        
        for ordinance in ordinances[1:]:  
            lines = ordinance.split('\n')
            
            title = lines[0].strip()
            
            if 'Brief:' in lines and 'Annotation:' in lines:
                brief_index = lines.index('Brief:') + 1
                annotation_index = lines.index('Annotation:')
                brief = ' '.join(lines[brief_index:annotation_index]).strip()
                ordinances_list.append({"title": title, "brief": brief})
            
    return ordinances_list


def process_docx_files(directory_path):
    all_ordinances = []
    for filename in os.listdir(directory_path):
        if filename.endswith('.docx') and not filename.startswith('~$'):
            doc_path = os.path.join(directory_path, filename)
            doc = Document(doc_path)
            text = ' '.join([paragraph.text for paragraph in doc.paragraphs])
            ordinances = extract_ordinances(text)
            for ordinance in ordinances:
                ordinance["filename"] = filename
                all_ordinances.append(ordinance)
    df = pd.DataFrame(all_ordinances)
    return df 
    