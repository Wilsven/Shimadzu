from bs4 import BeautifulSoup
import requests
import json
import pandas as pd
import base64
import io

import os
import pickle
import uuid
import re

import streamlit as st

##### Web Scraping
# Information to scrape
# CAS Number, Compound name, Synonym, Theoretical MW, Formula, SMILES, Structure, InChIKey

compound_cid = '2244' # user input, CID number

parent_url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/'
url = ''.join([parent_url, compound_cid, '/JSON'])

response = requests.get(url) # 200 means OK
json_file = response.json()


##### Get Information
# Define function to get information

def create_library(input_list): 
    
    # To store information
    data = {
        'CAS #': [], 
        'Compound Name': [],
        'Synonym': [],
        'Theory MW': [],
        'Formula': [],
        'Class': [],
        'Comment': [],
        'Column': [],
        'RT': [],
        'Chromatogram Comment': [],
        'Adduct Ion': [],
        'Adduct m/z': [],
        'Precursor Ion': [],
        'SP ID of Precursor Ion': [],
        'MS Stage': [],
        'Spectrum Comment': [],
        'Ionization': [],
        'Mass Range': [],
        'Collision Energy': [],
        'Collision Gas Vol.': [],
        'Polarity': [],
        'Instrument': [],
        'Data Folder': [],
        'Data Filename': [],
        'Acquired By': [],
        'Acquired': [],
        'Sample Info': [],
        'SMILES': [],
        'Structure': [],
        'InChIKey': []
    }
    
    library = pd.DataFrame(data)
    
    cas_list = []
    name_list = []
    iupac_list = []
    inchi_key_list = []
    smiles_list = []
    molecular_formula_list = []
    theoretical_mw_list = []
    
    for compound_cid in input_list:
    
        parent_url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/'
        url = ''.join([parent_url, compound_cid, '/JSON'])

        # Get response
        response = requests.get(url)
        
        # Get json
        json_file = response.json()

        # Get information for library
        try:
            cas = json_file['Record']['Section'][2]['Section'][3]['Section'][0]['Information'][0]['Value']['StringWithMarkup'][0]['String']
        except:
            cas = None
        
        try:
            name = json_file['Record']['RecordTitle']
        except:
            name = None
            
        try:
            iupac = json_file['Record']['Section'][2]['Section'][1]['Section'][0]['Information'][0]['Value']['StringWithMarkup'][0]['String']
        except:
            iupac = None
        
        try:
            inchi_key = json_file['Record']['Section'][2]['Section'][1]['Section'][2]['Information'][0]['Value']['StringWithMarkup'][0]['String']
        except:
            inchi_key = None
        
        try:
            smiles = json_file['Record']['Section'][2]['Section'][1]['Section'][3]['Information'][0]['Value']['StringWithMarkup'][0]['String']
        except:
            smiles = None
        
        try:
            molecular_formula = json_file['Record']['Section'][2]['Section'][2]['Information'][0]['Value']['StringWithMarkup'][0]['String']
        except:
            molecular_formula = None
        
        try:
            theoretical_mw = json_file['Record']['Section'][3]['Section'][0]['Section'][0]['Information'][0]['Value']['StringWithMarkup'][0]['String']
        except:
            molecular_formula = None
    
        cas_list.append(cas)
        name_list.append(name)
        iupac_list.append(iupac)
        theoretical_mw_list.append(theoretical_mw)
        molecular_formula_list.append(molecular_formula)
        smiles_list.append(smiles)
        inchi_key_list.append(inchi_key)
        
    library['CAS #'] = cas_list
    library['Compound Name'] = name_list
    library['Synonym'] = iupac_list
    library['Theory MW'] = theoretical_mw_list
    library['Formula'] = molecular_formula_list
    library['SMILES'] = smiles_list
    library['InChIKey'] = inchi_key_list
    
    return library

##### Streamlit Interface

st.header('Upload')
input_list = st.file_uploader('Upload text file with CID Numbers.',
                              type=['txt'])

if not input_list:
    st.text('You have not uploaded a file. Please upload a file. :)')
    
if input_list is not None:

    # Output upload details
    st.success("File successfully uploaded!")
    st.write('---')
    file_details = {'filename': input_list.name,
                    'filetype': input_list.type,
                    'filesize': input_list.size}
    st.write(file_details)
    st.write('---')
    
    input_list = pd.read_csv(input_list, header=None, names=['CID Number']).astype(str)['CID Number'].to_list()
    
    library = create_library(input_list)
    
    st.write(library)
    
    ##### Download button 
    
    def download_button(object_to_download, download_filename, button_text, pickle_it=False):
        """
        Generates a link to download the given object_to_download.
        Params:
        ------
        object_to_download:  The object to be downloaded.
        download_filename (str): filename and extension of file. e.g. mydata.csv,
        some_txt_output.txt download_link_text (str): Text to display for download
        link.
        button_text (str): Text to display on download button (e.g. 'click here to download file')
        pickle_it (bool): If True, pickle file.
        Returns:
        -------
        (str): the anchor tag to download object_to_download
        Examples:
        --------
        download_link(your_df, 'YOUR_DF.csv', 'Click to download data!')
        download_link(your_str, 'YOUR_STRING.txt', 'Click to download text!')
        """
        if pickle_it:
            try:
                object_to_download = pickle.dumps(object_to_download)
            except pickle.PicklingError as e:
                st.write(e)
                return None

        else:
            if isinstance(object_to_download, bytes):
                pass

            elif isinstance(object_to_download, pd.DataFrame):
                # object_to_download = object_to_download.to_csv(index=False)
                towrite = io.BytesIO()
                object_to_download = object_to_download.to_excel(towrite, encoding='utf-8', index=False, header=True)
                towrite.seek(0)

            # Try JSON encode for everything else
            else:
                object_to_download = json.dumps(object_to_download)

        try:
            # some strings <-> bytes conversions necessary here
            b64 = base64.b64encode(object_to_download.encode()).decode()

        except AttributeError as e:
            b64 = base64.b64encode(towrite.read()).decode()

        button_uuid = str(uuid.uuid4()).replace('-', '')
        button_id = re.sub('\d+', '', button_uuid)

        custom_css = f""" 
            <style>
                #{button_id} {{
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    background-color: rgb(255, 255, 255);
                    color: rgb(38, 39, 48);
                    padding: .25rem .75rem;
                    position: relative;
                    text-decoration: none;
                    border-radius: 4px;
                    border-width: 1px;
                    border-style: solid;
                    border-color: rgb(230, 234, 241);
                    border-image: initial;
                }} 
                #{button_id}:hover {{
                    border-color: rgb(246, 51, 102);
                    color: rgb(246, 51, 102);
                }}
                #{button_id}:active {{
                    box-shadow: none;
                    background-color: rgb(246, 51, 102);
                    color: white;
                    }}
            </style> """

        dl_link = custom_css + f'<a download="{download_filename}" id="{button_id}" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}">{button_text}</a><br></br>'

        return dl_link

    filename = 'library.xlsx'
    download_button_str = download_button(library, filename, f'Download Library as Excel File', pickle_it=False)
    st.markdown(download_button_str, unsafe_allow_html=True)