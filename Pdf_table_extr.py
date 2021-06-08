import os
import sys
import tabula
import PyPDF2
import pandas as pd
import numpy as np

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

#loop over all pdf files
for files in os.listdir(path):
    if files.endswith(".pdf"):
        
        #get pdf info and page numbers
        pdf_file = PyPDF2.PdfFileReader(open(files,'rb'))
        pages = pdf_file.numPages 
        paper_title = pdf_file.getOutlines()[0]["/Title"]

        #initialize table-clean
        table_clean = []

        #loop over pages
        for pg in range(1,pages):
            

            #check if the page is rotated - first check/attempt
            if (pdf_file.getPage(pg).get('/Rotate') != None and (pdf_file.getPage(pg).get('/Rotate')) != 0):
                pdf_writer = PyPDF2.PdfFileWriter()

                pdf_page = pdf_file.getPage(pg)
                pdf_page.rotateClockwise(90)  # rotate Clockwise()
                pdf_writer.addPage(pdf_page)

                #path to rotated directory- gets created if not there
                path_rot = os.getcwd() + "/RotatedPages/"
                if (not os.listdir(path_rot)): os.mkdir(path_rot)
                with open(path_rot +'Rot_{}_P_-{}.pdf'.format(files,pg), 'wb') as pdf_page_rotated:
                    pdf_writer.write(pdf_page_rotated)
                    tables = tabula.read_pdf(pdf_page_rotated, multiple_tables=True, pages='pg') # finding tables using tabula    
            else:
                tables = tabula.read_pdf(files, multiple_tables=True, pages='pg') # finding tables using tabula





