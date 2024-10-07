#   Copyright 2022 Gesellschaft fuer Systems Engineering e.V. (GfSE)
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0  
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#   This is the main py file of the base architecture writer for the FAS plugin for SysML v2.
#
#
#   The script is made for writing the base architecture to the repository

import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import scrolledtext

from time import sleep
from functools import partial
import sys
import json
import tempfile
import base64
import webbrowser
import zlib

from datetime import datetime

import requests 

import platform
import os

cFolderName = os.getcwd();
sys.path.insert(1,cFolderName.strip().replace('auxiliary','core').replace('auxiliary','core'))
from fas4sysmlv2API_helpers import * 





def DumpJupyterNotebook(cWorkingFolderAndOutputFile, cWorkingFolderAndInputFile, cSysMLString, cModelName):
     cNotebookFile = cWorkingFolderAndOutputFile
     FID1=open(cWorkingFolderAndInputFile,'r');
     FID2=open(cNotebookFile,'w');
     for tline in FID1:
         num = tline.find('"<Paste SysMLv2 code here>"')
         if num > -1:
             cCommaBlankAndQuotationMark=',' + '\r\n' + '    "'
             cCodedSysML='    "' + cSysMLString.replace('"','\\"').replace('\r\n','\n').replace('\n','\\n"' + cCommaBlankAndQuotationMark)   
             #Remove final comma, blank and quotation mark 
             cCodedSysML = cCodedSysML[:(len(cCodedSysML)-len(cCommaBlankAndQuotationMark))]
             FID2.write(cCodedSysML )
         else:
             FID2.write(tline.replace('publish UseCaseActivities','publish ' + cModelName))
     FID1.close()
     FID2.close()
     return cNotebookFile   

def WriteSysML(cSysMLString, strModelName):
     cModelName = strModelName.get()

     
     cWorkingFolder = cFolderName = os.getcwd()+os.sep;
     print('Storing the result in the repository ...')
     cNotebookFile = cWorkingFolder + 'traceability_input_writer.ipynb' 
     cOutputFile = cWorkingFolder + 'temp_output.ipynb'
     cResultFile = cWorkingFolder + 'temp_result.ipynb'
     cProjectIdFile = cWorkingFolder + 'project_id.txt'
     DumpJupyterNotebook(cOutputFile, cNotebookFile, cSysMLString, cModelName)

     if platform.system()!='Windows':
         cSilencer='2>/dev/null'
         os.system('exec /bin/bash -i -c "jupyter nbconvert --to notebook --execute ' + cOutputFile + ' --stdout >' + cResultFile + ' ' + cSilencer +'"')
     else:
         cSilencer='' #'>nul 2>&1';
         os.system('jupyter nbconvert --to notebook --execute ' + cOutputFile + ' --output=' + cResultFile + ' ' + cSilencer)

     FID1=open(cResultFile ,'r');
     bStdout = False
     bData = False
     bResultExpected = False
     cHost = ''
     cStatus = ''
     for tline in FID1:
         if bResultExpected:
             cStatus = 'STATUS: ' + tline.replace('\\n','').replace('\\r','').strip()
             print(cStatus)
             break
         if tline.find('"name": "stdout",')>-1:
             bStdout = True
         if tline.find('"data": {')>-1 and bStdout:
             bData = True
         if tline.find('"text/plain": [')>-1 and bData:
             bResultExpected = True
         iHostPos = tline.find('API base path:')
         if iHostPos > -1:
             cHost = tline[(iHostPos+15):].replace(',','').replace('"','').replace('\\r','').replace('\\n','').strip()
             print(cHost)

     FID1.close()
     
     posOpeningParenthesis = cStatus.find('(')
     posClosingParenthesis = cStatus.find(')')
     cProjectID = cStatus[(posOpeningParenthesis+1):posClosingParenthesis]

     FID1=open(cProjectIdFile,'w');
     FID1.write(cProjectID+'\r\n'+cHost)
     FID1.close()
     return cHost,cProjectID




def copy_and_tag_elements(source_host, source_id, target_host, target_id, cTraceabilityPackageName):
    rep_t = []

    rep_source = read_full_repository(source_host, source_id)


        

    
    for i in range(len(rep_source)):
        r = rep_source[i]
        cTag = 'BA'
        r['shortName']=cTag
        r['declaredShortName']=cTag
        rep_source[i]= r

        
        rep_t.append({"payload": rep_source[i],
                      "identity": {"@id": rep_source[i]['@id']}})
                      
                      

    

        
    commit_body1 = '{"change":' + json.dumps(rep_t) + '}'
    #print(commit_body1)
    print('commit starts')
    response = requests.post(target_host + "/projects/" +target_id+ "/commits", headers={"Content-Type": "application/json"}, data = commit_body1)
    print('commit ends')
    
    if response.status_code != 200:
        print('NOK')
        print(response.json())
        return False , response.json()
    else:
        print('OK')
        return True , response.json()
 

def execute_writing(cMirrorProjectName,cServerName,scr,strModelName):
    cMirrorProject=cMirrorProjectName.get()
    cMirrorServerName=cServerName.get()
    cMirrorProjectID = ''
    cTraceabilityPackageName = 'TraceabilityLinks'
    #cSysMLString = (scr.get('1.0', tk.END)+ " ").replace('\\n','\\r\\n').strip()+"\r\n"
    cSysMLString = (scr.get('1.0', tk.END)+ " ").strip()+"\r\n"
    cHost,cProjectID = WriteSysML(cSysMLString, strModelName)
    if cServerName.get()!='':
       print('Writing to the mirror server '+ cMirrorServerName + '...')
       print('Creating project ' + cMirrorProject)
       project_body = {
          "@type": "Project",
          "description": "",
          "name": cMirrorProject
       }
       cURL = cMirrorServerName + "/projects"
       print('POST ' + cURL)
       print('data = ')
       print(json.dumps(project_body))
       response = requests.post(cURL , headers={"Content-Type": "application/json"}, data = json.dumps(project_body))
    
       if response.status_code != 200:
            print('NOK')
            print(response)
            print(response.json())
            return False , response.json()
       else:
            cMirrorProjectID=response.json().get('@id')
            print('OK - Project created: ' + cMirrorProjectID)
            
       
       bSuccess,sInfo = copy_and_tag_elements(cHost, cProjectID, cMirrorServerName, cMirrorProjectID,cTraceabilityPackageName)
       if bSuccess:
           print("Successfully wrote to project '" + cMirrorProject + "' - Id: " + cMirrorProjectID )
       else:
           print("Writing failed to project " + cMirrorProject + " - Id: " + cMirrorProjectID)



def run_traceability_tool(cProjectUUID, cHost, cFolder):
     mainWindow = Tk()
     mainWindow.title("Base Architecture tool")
     frm = ttk.Frame(mainWindow)
     frm.grid(row=0, column=0, columnspan=3)

     cProjectName = StringVar()
     timestamp = datetime.now()
     cMirrorProject = f"Interoperability Demo Project - {timestamp}"
     cProjectName.set(cMirrorProject)
     strFolder= StringVar()
     strFolder.set(cFolder)
     cServerName = StringVar()
     cServerName.set(cHost)
     strModelName= StringVar()
     strModelName.set('')
     ttk.Label(frm, text="Model Name").grid(column=0, row=0)
     ttk.Entry(frm, textvariable = strModelName, width = 50).grid(column=1, row=0)
     ttk.Label(frm, text="").grid(column=0, row=1)
     ttk.Label(frm, text="Server").grid(column=0, row=2)
     ttk.Entry(frm, textvariable = cServerName, width = 50).grid(column=1, row=2)
     ttk.Label(frm, text="Project Name").grid(column=0, row=3)
     ttk.Entry(frm, textvariable = cProjectName, width = 50).grid(column=1, row=3)
     bSuccess = True
     ttk.Label(frm, text="").grid(column=0, row=4)
     ttk.Label(frm, text="Write Base Architecture here:").grid(column=0, row=6)
     scr = scrolledtext.ScrolledText(mainWindow, width = 100, height = 20, font = ("Courier", 9))
     scr.grid(column = 0, pady = 10, padx = 10)


     ttk.Button(frm, text="Go", command=partial(execute_writing,cProjectName,cServerName,scr,strModelName)).grid(column=1, row=5)
     ttk.Button(frm, text="Quit", command=mainWindow.destroy).grid(column=3, row=5)
     mainWindow.mainloop()


def main(): 
    cProject= ''
    cHost = ''
    cFolder = ''


    run_traceability_tool(cProject, cHost, cFolder)

if __name__ == "__main__":
    main()
