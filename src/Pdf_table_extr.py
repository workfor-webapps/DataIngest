"""This is a module for extraction of Meta_Analysis table data and
    developed for this specific purpose. In order to run this script please follow the steps
    in README.md file 

    :return: Publication info and extracted table data
    :rtype: datasets
"""
import os, io
import sys
import tabula
import PyPDF2
import pandas as pd
import numpy as np
import shutil
import re
import crossref_commons.retrieval
from pdfminer import high_level




def excel_init():
    
    """ This function initializes an excel writer and creates Processed excel file.
        
        :return writer: ExcelWriter object and creates a Processed.xlsx file
        :rtype: ExcelWriter object
        """

    #check if excel file exists
    if os.path.isfile("./Processed.xlsx"): 
        ans = str(input("Warning: Processed.xlsx file in the working directory will be overwritten, would you like to continue? y/n :")).upper()
        
        #if file exist ask if you wnat to overwrite it
        if ans == "N" or ans == "NO":
            print("Terminating the program...")
            sys.exit() 

    #open an excel file
    writer = pd.ExcelWriter('./Processed.xlsx', engine='xlsxwriter')
    return(writer)



def get_title_from_pdf(pdf_file):
    
    """This function uses PyPDF2 library to extract the paper title. This function is 
    developed just in case the publication metadata is not extractable from crossref.

    :param pdf_files: pdf file binary
    :type path_files: binary file content
    :return: paper title
    :rtype: str
    """
    #pdf_in = open(path_files,'rb') #if the file is stored on local drive
    pdf_file = PyPDF2.PdfFileReader(pdf_file)
    if pdf_file.getOutlines() == []: 
        paper_title = pdf_file.getDocumentInfo()["/Title"] 
    else:
        paper_title = pdf_file.getOutlines()[0]["/Title"]
    
    return paper_title



def get_doi(pdf_file):

    """This function finds publication DOI from a PDF's first or second page using regex
    
    :param pdf_file: pdf file content
    :type pdf_file: binary
    :return: DOI
    :rtype: str
    """

    #local_pdf_filename = path_files
    pages = [0,1] # just the first and second pages
    #get the text
    text = high_level.extract_text(pdf_file, "", pages)
    # regular expression
    doi_re = re.compile("/^10.\d{4,9}/[-._;()/:A-Z0-9]+$/i|10.(\d)+/([^(\s\>\"\<)])+")
    #search re in the text
    m = doi_re.search(text)

    if m is None:
        m="DOI not found!"
    else:
        m = m.group(0)
    
    return m



def get_pubData(doi):
    
    """A function to resolve doi from crossref database

    :param doi: DOI of a publication
    :type doi: str
    :return: publication metadata
    :rtype: json
    """

    pub_data = crossref_commons.retrieval.get_publication_as_json(doi)

    return pub_data

#https://gitlab.com/crossref/crossref_commons_py
class PubData:
    """This class stores publication data extracted from crossref call

    :param title: title of the publication
    :type title: str, defaults to none
    :param authors: list of authors
    :type authors: str, defaults to none
    :param jur: Name of the journal
    :type jur: str
    :param pub_year: Published year, defaults to 0
    :type pub_year: int
    :param doi: doi of the publication
    :type: str
    """

    title= ""
    authors = ""
    jur = ""
    pub_year = 0
    status = True

    def __init__(self, doi) -> None:
        """class constractor

        :param doi: doi
        :type doi: str
        """
        try:
            self.data = crossref_commons.retrieval.get_publication_as_json(doi)
        except ValueError: #DOI could not be resulved
            print("DOI does not exist in crossref database")
            self.status = False
        
        if self.status:
            self.title = self.data["title"][0]
            Authors = [[x["given"], x["family"]] for x in self.data['author']]
            Author_str = ""
            for i in range(len(Authors)):
                for j in range(2):
                    Author_str += Authors[i][j] 
                Author_str += ", "
            self.authors = Author_str
            self.jur = self.data['short-container-title'][0]

        
    

#*******************************************************************************************
def extract_tables(fh):

    pdf_in = fh #open(path_files,'rb')
    pdf_file = PyPDF2.PdfFileReader(pdf_in)
    pages = pdf_file.numPages 
    file_p = fh# path_files
    #initialize table-clean
    table_clean = []
    table_pages = []
    #******************************************************************
    #******************** Looping over pages for each PDF file ********
    #loop over pages
    for pg in range(0,pages):
        #************************************************************************************************************
        #***************** NOTE: Tabula starts pages from 1 and PyPDF2 get-page() start indexing pages from 0********
        #************************************************************************************************************


        tables = tabula.read_pdf(file_p, multiple_tables=True, pages=str(pg+1)) # finding tables using tabula
        
        #cleaning tables
        i = 0
        j = len(tables)
        z = 0 # This is in case the numeric columns cannot be fixed by rotation
        while i < j:

            #convert to pandas dataframe
            df = pd.DataFrame(tables[(i)])

            if (df.shape[1]<2) or (df.shape[0]<2): #drop based on the shape - if smaler than 2 in row or column
                i+=1
                continue
            if df.isna().sum().sum() > df.count().sum(): #drop if number of NAN elements are higher than others
                i+=1
                continue
            


            hyphen = [r'^\u002D', r'^\u05BE', r'^\u1806', r'^\u2010', r'^\u2011', r'^\u2012', r'^\u2013', r'^\u2014', r'^\uFE58', r'^\uFE63', r'^\uFF0D']
            #df = df.replace('^–','-', regex=True) # this is added so excel can identify negative values 
            df = df.replace('^0,','0.', regex=True) # this is added so excel can identify negative values
            df = df.replace('^\.','0.', regex=True)
            df = df.replace(',','', regex=True) # this is added so excel can identify negative values
            df = df.replace('\*{1,4}$','',regex=True) # this is added so excel can identify numerical values 
            df = df.replace('–', np.nan) # this is added so excel can identify NAN values
            df = df.replace('-', np.nan) # this is added so excel can identify NAN values
            df = df.replace(regex=hyphen, value="-")
            
            #drop if all/most column types are objects 
            numeric_values = len([df[column][i] for column in df.columns for i in range(0, len(df)) if str(df[column][i]).replace(".","").isnumeric()])
            if (df.count().sum())/3 > numeric_values:
                i+=1
                continue

            #drop columns if all values are NAN
            df = df.dropna(axis=1, how='all')

            nn = 1
            mm = df.columns.size
            for column in df.columns:
                if ("Unnamed"  in column):
                    nn+=1
            if nn>mm/2:
                df = df.rename(columns=df.iloc[0,0:])
                df = df.drop([0])
        

            #Second check if a page is rotated- if columns are numeric it is possibly rotated
            x = [column for column in df.columns if str(column).replace(".","").isnumeric()] #list of numerical columns
            if len(x) > 1 and z < 3:
                pdf_writer = PyPDF2.PdfFileWriter()

                pdf_page = pdf_file.getPage(pg)
                pdf_page.rotateClockwise(90)  # rotate Clockwise()
                if z==1 : pdf_page.scaleBy(0.5)         # scale 
                pdf_writer.addPage(pdf_page)

                pdf_bytes = io.BytesIO()
                pdf_writer.write(pdf_bytes)
                
                tables = tabula.read_pdf(pdf_bytes, multiple_tables=True, pages="all") # finding tables using tabula  

                #shutil.move (os.getcwd() + "/" + file_ext, path_rot + file_ext)
                z+=1
                i = 0
                j = len(tables)
                continue

            #add to table clean
            table_clean.append(df)
            table_pages.append(pg+1)
            i+=1
    #************************************* end of pages loop*********************************************

    #fixing column names 
    for num in range(len(table_clean)):
        rows_with_nan=[]
        #i = 1
        #j = table_clean[num].columns.size
        #for column in table_clean[num].columns:
        #    if ("Unnamed" in column):
        #        i+=1
        #if i>j/2:
        #    table_clean[num] = table_clean[num].rename(columns=table_clean[num].iloc[0,0:])
        #    table_clean[num] = table_clean[num].drop([0])
        
        #re-indexing
        table_clean[num].index = range(len(table_clean[num]))   

        # filter rows with nan and add the row index to next row
        rows_with_nan = [index for index, row in table_clean[num].iterrows() if row.isnull().sum() > 2]

        if rows_with_nan: 
            for k in rows_with_nan:
                table_clean[num].iat[k,0] =  "[ " + str(table_clean[num].iloc[k,0]) + " ]"
        #        table_clean[num] = table_clean[num].drop(rows_with_nan)
    
        
        # if left and bottom of a column is NAN move it to left and drop the column

        if table_clean[num].columns[0] is np.nan and table_clean[num].columns[1] is not np.nan and table_clean[num].iloc[2,1] is np.nan:
            table_clean[num] = table_clean[num].rename(columns={table_clean[num].columns[0]:str(table_clean[num].columns[1]).upper()})
            table_clean[num] = table_clean[num].drop(columns = [str(table_clean[num].columns[1])])

        table_clean[num].columns.str.upper()
        for ind in table_clean[num].index:
            for col in table_clean[num].columns:
                try:
                    temp = table_clean[num][col].iloc[ind]
                    table_clean[num][col].iloc[ind] = float(temp)
                    
                except:
                    print("cannot convert to float in table %d, column %s, index %d", num, col,ind)
        table_clean[num].insert(0,"CONCEPT CATEGORY", pd.Series(["concept"], index =[0]))
    
    return table_clean, table_pages

def write_to_excel(writer, jj, paper_title, table_clean):
        # Saving data to an excel sheet
    workbook = writer.book
    if jj==1:
        #adding cell formatting for summary cells
        sum_format = workbook.add_format({
            'bold': 1,
            'border': 2,
            'align': 'left',
            'valign': 'vcenter',
            'fg_color': '#00FFFF'})

        worksheet_name = "Summary"
        worksheet=workbook.add_worksheet(worksheet_name)
        writer.sheets[worksheet_name] = worksheet
        worksheet.write_string(0, 0,"File name", sum_format)
        worksheet.write_string(0, 1,"Sheet number", sum_format)
        worksheet.write_string(0, 2,"Number of Clean Tables", sum_format)
        worksheet.write_string(0, 3,"Title",sum_format )


    worksheet_name = "Pub_{}".format(jj)

    writer.sheets["Summary"].write_string(jj,0, "_name")
    writer.sheets["Summary"].write_string(jj,1, worksheet_name)
    writer.sheets["Summary"].write_string(jj,2, str(len(table_clean)))
    writer.sheets["Summary"].write_string(jj,3, paper_title)


    
    start_row = 1
    worksheet=workbook.add_worksheet(worksheet_name)
    writer.sheets[worksheet_name] = worksheet
    worksheet.write_string(1, 0,"Table: ")
    # Create a format to use in the merged range.
    merge_format = workbook.add_format({
        'bold': 1,
        'border': 2,
        'align': 'left',
        'valign': 'vcenter',
        'fg_color': '#00FF00'})

    # Merge 5 cells.
    worksheet.merge_range('A1:J1',"Title: " + paper_title , merge_format)

    for ii in range(len(table_clean)):

        #adding cell formatting for table number cells
        Cell_format = workbook.add_format({
            'bold': 1,
            'border': 2,
            'align': 'left',
            'valign': 'vcenter',
            'fg_color': '#FFD7D7'})
        
        worksheet.write_string(start_row, 0,"Table: {} ".format(ii+1), Cell_format)


        if ii==0:

            table_clean[ii].to_excel(writer, sheet_name=worksheet_name, startrow=start_row, startcol=1, index =False)
        else:
            table_clean[ii].to_excel(writer, sheet_name=worksheet_name, startrow=start_row, startcol=1, index = False)
        
        #worksheet.column_dimensions['B'].width = 40
        start_row += table_clean[ii].shape[0]+1
    writer.save()
    return 0

#**************************************************************************************
#***************************** Initializing *******************************************
if __name__ == '__main__':
    # get PDF files directory
    path = os.getcwd() + "/temp/"
    isExist = os.path.exists(path)

    if (not isExist):
        os.mkdir(path)
    #adding google drive api to access files from gdrive

    #check if the PDFs directory is empty
    if (not os.listdir(path)):
        print ("No file to process!")
        sys.exit()

    writer = excel_init()

    #jj = 1 # this is for sheet names in excel writer
    temp_file = path+"B.pdf"

    #time_modified = os.path.getmtime(temp_file)
    doi = get_doi(temp_file)
    
    x = PubData(doi)

    
    
    print(x.data)
    #print("Title= ", x.title)

    #print(paper_title)
    table_clean = extract_tables(temp_file)
    #write_to_excel(writer, jj, paper_title, table_clean)
    #jj += 1
    print(table_clean[0])
