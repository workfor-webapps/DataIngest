"""This is a module for extraction of Meta_Analysis table data and
    developed for this specific purpose. In order to run this script please follow the steps
    in README.md file 
"""
import os, io
import sys
import tabula
import PyPDF2
import pandas as pd
import numpy as np
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
        
        #if file exist ask if you want to overwrite it
        if ans == "N" or ans == "NO":
            print("Terminating the program...")
            sys.exit() 

    #open an excel file
    writer = pd.ExcelWriter('./Processed.xlsx', engine='xlsxwriter')
    return(writer)

#---------------------------------------------------------------------------------------
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


#---------------------------------------------------------------------------------------
def get_doi(pdf_file):

    """This function finds publication DOI from a PDF's first or second page using regex
    
    :param pdf_file: pdf file content
    :type pdf_file: binary
    :return: DOI
    :rtype: str
    """

    pages = [0,1] # just the first and second pages
    text = high_level.extract_text(pdf_file, "", pages)
    doi_re = re.compile("/^10.\d{4,9}/[-._;()/:A-Z0-9]+$/i|10.(\d)+/([^(\s\>\"\<)])+")
    m = doi_re.findall(text)

    if m ==[]:
        doi="DOI not found!"
    else:
        doi = "DOI not found!"
        for item in m:
        #check if doi is valide
            data = PubData(item)
            if data.status:
                doi = item
                break
                
    return doi

def get_citation(doi):

    """Generate citation data from doi

    :param doi: DOI
    :type doi: str
    :return: formated citation
    :rtype: str
    """

    data = PubData(doi)
    citation = data.authors + ";" + data.title + "." + data.jur + "(" + str(data.pub_year) + ")."
    return citation


#---------------------------------------------------------------------------------------
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
    doi = ""
    status = True

    def __init__(self, doi) -> None:
        """class constractor

        :param doi: doi
        :type doi: str
        """
        self.doi = doi
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
            try:
                self.pub_year = self.data["published-online"]["date-parts"][0][0]
            except:
                self.pub_year = "year not found"


        
#---------------------------------------------------------------------------------------
def extract_tables(fh):
    """This function extracts all the relevent table data from a PDF file using Tabula and PyPDF libs.

    :param fh: ByteIO file
    :type fh: ByteIO
    :return: list of all the processed tables and their page numbers in the pdf file 
    :rtype: Dataframe
    """

    pdf_in = fh #open(path_files,'rb')
    pdf_file = PyPDF2.PdfFileReader(pdf_in)
    pages = pdf_file.numPages 
    file_p = fh# path_files
    #initialize table-clean
    table_clean = []
    table_pages = []

    #******************** Looping over pages for each PDF file ********
    for pg in range(0,pages):

    #************************************************************************************************************
    #***************** NOTE: Tabula starts pages from 1 and PyPDF2 get-page() start indexing pages from 0 *******
    #************************************************************************************************************
        Rot = False
        file_p.seek(0)
        tables = tabula.read_pdf(file_p, multiple_tables=True, pages=str(pg+1)) # finding tables using tabula
        
        i = 0
        j = len(tables)
        z = 0 # This is in case the numeric columns cannot be fixed by rotation
        while i < j:

            df = pd.DataFrame(tables[(i)])

            if (df.shape[1]<2) or (df.shape[0]<2): #drop based on the shape - if smaler than 2 in row or column
                i+=1
                continue
            if df.isna().sum().sum() > df.count().sum(): #drop if number of NAN elements are higher than others
                i+=1
                continue
            
            hyphen = [r'^\u002D', r'^\u05BE', r'^\u1806', r'^\u2010', r'^\u2011', r'^\u2012', r'^\u2013', r'^\u2014', r'^\u2015', 
                      r'^\u207B', r'^\u208B', r'^\uFE58', r'^\uFE63', r'^\uFF0D', r'^\u2212', r'\uFF0D']
            df = df.replace(regex=hyphen, value="-")# this is added so excel can identify negative values
            df = df.replace('^0,','0.', regex=True) 
            df = df.replace('^\.','0.', regex=True)
            df = df.replace(',','', regex=True) 
            df = df.replace('\*{1,4}$','',regex=True) 
            df = df.replace('^-\.','-0.', regex=True)
            
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
        

            #check if a page is rotated- if columns are numeric it is possibly rotated
            x = [column for column in df.columns if str(column).replace(".","").isnumeric()] #list of numerical columns
            if len(x) > 1 and z < 3:

                pdf_writer = PyPDF2.PdfFileWriter()
                pdf_page = pdf_file.getPage(pg)
                pdf_page.rotateClockwise(90)  # rotate Clockwise()
                Rot = True #To save a rotated version
                if z==1 : pdf_page.scaleBy(0.5) # scale 
                pdf_writer.addPage(pdf_page)

                pdf_bytes = io.BytesIO()
                pdf_writer.write(pdf_bytes)
                pdf_bytes.seek(0)
                
                tables = tabula.read_pdf(pdf_bytes, multiple_tables=True, pages="all") # finding tables using tabula  

                pdf_bytes.flush()
                #shutil.move (os.getcwd() + "/" + file_ext, path_rot + file_ext)
                z+=1
                i = 0
                j = len(tables)
                continue

            #add to table clean
            table_clean.append(df)
            table_pages.append([pg+1, Rot])
            i+=1
    #************************************* end of pages loop*********************************************

    #fixing column names 
    for num in range(len(table_clean)):
        rows_with_nan=[]
        
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

        
        # for ind in table_clean[num].index:
        #     for col in table_clean[num].columns:
        #         try:
        #             temp = table_clean[num][col].iloc[ind]
        #             table_clean[num][col].iloc[ind] = float(temp)
                    
        #         except:
        #             print("cannot convert to float in table %d, column %s, index %d", num, col,ind)
        

        #spliting columns if values sperated by space
        if not table_clean[num].columns.is_unique:
            unique_names = list(uniquify(list(table_clean[num].columns)))
            table_clean[num].columns = unique_names

        
        table_columns = list(table_clean[num].columns)

        for column in table_columns:
            col = str(column).split(" ", 1)
            if len(col) > 1:
                try:
                    new = table_clean[num][column].astype(str).str.split(" ", n = 1, expand = True)
                    new2 = new.dropna(axis=0, how='any')
                    if "(" in new2.iloc[0,0]:
                        continue
                    if len(new.columns) > 1:
                        #print(new)
                        col0 = col[0]
                        col1 = col[1]

                        if col0 in list(table_clean[num].columns):
                            col0 = col0+"_1"
                        if col1 in list(table_clean[num].columns):
                            col1 = col1+"_1"
                        table_clean[num][col0] = new[0]
                        table_clean[num][col1] = new[1]
                        table_clean[num] = table_clean[num].drop(columns = [column])

                        if not table_clean[num].columns.is_unique:
                            unique_names = list(uniquify(list(table_clean[num].columns)))
                            table_clean[num].columns = unique_names

                except AttributeError:
                    #print(table_clean[num][column])
                    try:
                        
                        new_df = table_clean[num][column]
                        if not new_df.columns.is_unique:
                            unique_names = list(uniquify(list(new_df.columns)))
                            new_df.columns = unique_names
                            

                        #
                        for new_column in new_df.columns:
                            if new_column in list(table_clean[num].columns):
                                new_column1 = new_column + "_1"
                            else:
                                new_column1 = new_column

                            table_clean[num][new_column1] = new_df[new_column]
                        
                        table_clean[num] = table_clean[num].drop(columns = [column])                            
                    
                    except:
                        print("Error: ", new_df)

                except KeyError:
                    print("column= ", column)

        
        table_clean[num].columns.str.upper()
        df = table_clean[num]
        hyphen = [r'^\u002D', r'^\u05BE', r'^\u1806', r'^\u2010', r'^\u2011', r'^\u2012', r'^\u2013', r'^\u2014', r'^\u2015', 
                  r'^\u207B', r'^\u208B', r'^\uFE58', r'^\uFE63', r'^\uFF0D', r'^\u2212', r'\uFF0D']
        df = df.replace(regex=hyphen, value="-")
        df = df.replace('^0,','0.', regex=True) 
        df = df.replace('^\.','0.', regex=True)
        df = df.replace(',','', regex=True) # this is added so excel can identify negative values
        df = df.replace('\*{1,4}$','',regex=True) # this is added so excel can identify numerical values 
        df = df.replace('^-\.','-0.', regex=True)
        df = df.replace(np.nan,'')
        df = df.replace('nan','')
        
        
        df.insert(0,"Concept Theme", pd.Series(["concept"], index =[0]))
        
        df.columns.str.upper()
        #adding the column names to rows
        col_names = [[x for x in df.columns]]
        col_names2 = [x for x in df.columns]
        col_array = np.array(list(col_names))
        df2 = pd.DataFrame(col_array, columns=col_names2)
        
        table_clean[num] = pd.concat([df2,df], axis=0, ignore_index= True, join="outer")
        table_clean[num].columns = [str(x+1) for x in range(len(table_clean[num].columns))]

        
        #convert dataframes to json objects
        #table_clean[num] = table_clean[num].to_json(orient='table')
        table_clean[num] = table_clean[num].to_html(index=False, justify="left", na_rep="",\
                             classes="table table-light table-striped table-hover table-bordered table-responsive-lg", table_id="pdf")
    
    return table_clean, table_pages

#---------------------------------------------------------------------------------------
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

def uniquify(df_columns):
    seen = set()

    for item in df_columns:
        fudge = 1
        newitem = item

        while newitem in seen:
            fudge += 1
            newitem = "{}_{}".format(item, fudge)

        yield newitem
        seen.add(newitem)

#---------------------------------------------------------------------------------------
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
