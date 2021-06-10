import os
import sys
import tabula
import PyPDF2
import pandas as pd
import numpy as np
import shutil
#import xlsxwriter

""" This is a python script for extraction of Meta_Analysis table data and
developed for this specific purpose. In order to run this script please follow this steps: 
1. Creat an environment from the environment.yml file.
2. Creat a directory called PDFs in the current working directory and place all the PDF files in this directory
3.  After run, an excel file containing table data will be created for post-processing """

# get PDF files directory
path = os.getcwd() + "/PDFs/"
isExist = os.path.exists(path)

if (not isExist):
    os.mkdir(path)
    print("PDFs directory is created in your CWD, please copy the pdf files to this directory and run the script again")
    sys.exit()

#check if the PDFs directory is empty
if (not os.listdir(path)):
    print ("The 'PDFs' directory is empty!")
    sys.exit()

#open an excel file
writer = pd.ExcelWriter('./Processed.xlsx', engine='xlsxwriter')
workbook  = writer.book

jj = 1 # this is for sheet names 
#loop over all pdf files
for files in os.listdir(path):
    if files.endswith(".pdf"):
        file_p = path+files # path to files
        #get pdf info and page numbers
        pdf_in = open(file_p,'rb')
        pdf_file = PyPDF2.PdfFileReader(pdf_in)
        pages = pdf_file.numPages 
        
        if pdf_file.getOutlines() == []: 
           paper_title = pdf_file.getDocumentInfo()["/Title"] 
        else:
            paper_title = pdf_file.getOutlines()[0]["/Title"]

        #initialize table-clean
        table_clean = []

        #loop over pages
        for pg in range(0,pages):
            #************************************************************************************************************************
            #***************** NOTE: Tabula starts pages from 1 and PyPDF2 get-page() start indexing pages from 0*********************
            #************************************************************************************************************************

            #check if the page is rotated - first check/attempt to fix rotated pages
            if (pdf_file.getPage(pg).get('/Rotate') != None and (pdf_file.getPage(pg).get('/Rotate')) != 0):
                pdf_writer = PyPDF2.PdfFileWriter()

                pdf_page = pdf_file.getPage(pg)
                pdf_page.rotateClockwise(90)  # rotate Clockwise()
                pdf_writer.addPage(pdf_page)

                #path to rotated directory- gets created if not there
                path_rot = os.getcwd() + "/RotatedPages/"
                isExist = os.path.exists(path)
                if (not isExist): 
                    os.mkdir(path_rot)
                file_ext = 'Rot_{}_P_{}.pdf'.format(files.replace(".pdf",""),str(pg))
                with open(file_ext, 'wb') as pdf_page_rotated:
                    pdf_writer.write(pdf_page_rotated)
                tables = tabula.read_pdf(file_ext, multiple_tables=True, pages="1") # finding tables using tabula    
                shutil.move (os.getcwd() + "/" + file_ext, path_rot + file_ext)
            else:
                tables = tabula.read_pdf(file_p, multiple_tables=True, pages=str(pg+1)) # finding tables using tabula
            
            #cleaning tables
            i = 0
            j = len(tables)
            z = 0 # This is in case the numeric columns cannot be fixed by rotation
            while i < j:
                if (tables[i].shape[1]<2) or (tables[i].shape[0]<2): #drop based on the shape - if smaler than 2 in row or column
                    i+=1
                    continue
                if tables[i].isna().sum().sum() > tables[i].count().sum(): #drop if number of NAN elements are higher than others
                    i+=1
                    continue
                


                #convert to pandas dataframe
                df = pd.DataFrame(tables[(i)])


                #drop if all column types are objects
                for column in df.columns:
                    if (df[column].dtypes != 'object') and (df[column].sum() > df[column].isna().sum()):
                        drop = False
                        break
                    else:
                        drop = True
                if drop:
                    i+=1
                    continue
    
                #drop columns if all values are NAN
                df = df.dropna(axis=1, how='all')

                nn = 1
                mm = tables[i].columns.size
                for column in tables[i].columns:
                    if ("Unnamed"  in column):
                        nn+=1
                if nn>mm/2:
                    tables[i] = tables[i].rename(columns=tables[i].iloc[0,0:])
                    tables[i] = tables[i].drop([0])
            

                #Second check if a page is rotated- if columns are numeric it is possibly rotated
                x = [column for column in tables[i].columns if str(column).replace(".","").isnumeric()] #list of numerical columns
                if len(x) > 1 and z < 3:
                    pdf_writer = PyPDF2.PdfFileWriter()

                    pdf_page = pdf_file.getPage(pg)
                    pdf_page.rotateClockwise(90)  # rotate Clockwise()
                    pdf_writer.addPage(pdf_page)

                    #path to rotated directory- gets created if not there
                    path_rot = os.getcwd() + "/RotatedPages/"
                    isExist = os.path.exists(path)
                    if (not isExist): 
                        os.mkdir(path_rot)
                    file_ext = 'Rot_{}_P_{}.pdf'.format(files.replace(".pdf",""),str(pg))
                    with open(file_ext, 'wb') as pdf_page_rotated:
                        pdf_writer.write(pdf_page_rotated)
                    tables = tabula.read_pdf(file_ext, multiple_tables=True, pages="1") # finding tables using tabula  

                    shutil.move (os.getcwd() + "/" + file_ext, path_rot + file_ext)

                    z+=1
                    i = 0
                    j = len(tables)
                    continue
    
                #add to table clean
                table_clean.append(df)
                i+=1
        #************************************* end of pages loop*********************************************

        #fixing column names 
        for num in range(len(table_clean)):
            rows_with_nan=[]
            i = 1
            j = table_clean[num].columns.size
            for column in table_clean[num].columns:
                if ("Unnamed"  in column):
                    i+=1
            if i>j/2:
                table_clean[num] = table_clean[num].rename(columns=table_clean[num].iloc[0,0:])
                table_clean[num] = table_clean[num].drop([0])
            
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
        
        # Saving data to an excel sheet
        worksheet_name = "Pub_{}".format(jj)
        jj += 1
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
            start_row += table_clean[ii].shape[0]
        pdf_in.close()
writer.save()
        





