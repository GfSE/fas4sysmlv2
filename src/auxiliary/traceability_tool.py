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
#   This is the main py file of the traceability for the FAS plugin for SysML v2.
#
#
#   The script is made for writing a logical or physical architecture and 
#   tracing it to the functional architecture

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



import requests 

import platform
import os

cFolderName = os.getcwd();
sys.path.insert(1,cFolderName.strip().replace('auxiliary','core').replace('auxiliary','core'))
from fas4sysmlv2API_helpers import * 


def dictionary_payload_allocationusage(element_id, client, owner, membership, quali_name, target):
    dictionary_payload_allocationusage = {
        "payload": {'@type': 'AllocationUsage',
                    '@id': element_id,
                    'client': [client],
                    'elementId': element_id,
                    'owner': owner,
                    'owningMembership': membership,
                    'owningNamespace': owner,
                    'owningRelationship': membership,
                    'qualifiedName': quali_name,
                    'relatedElement': [client, target],
                    'source': [client],
                    'supplier': [target],
                    'target': [target]
                   },
        "identity": {"@id": element_id}
    }
    return dictionary_payload_allocationusage



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


def target_object_lookup(source_name):
    target_name = '';
    #Hard-coded look-up for one example as a first sample to test on ...
    #This needs to be changed!
    
    if source_name == 'engines':
        target_name = 'liftAndThrustGeneration'

    if source_name == 'engine1':
        target_name = 'liftAndThrustGeneration'

    if source_name == 'engine2':
        target_name = 'liftAndThrustGeneration'

    if source_name == 'engine3':
        target_name = 'liftAndThrustGeneration'

    if source_name == 'engine4':
        target_name = 'liftAndThrustGeneration'

    if source_name == 'engine5':
        target_name = 'liftAndThrustGeneration'

    if source_name == 'engine6':
        target_name = 'liftAndThrustGeneration'

    
    if source_name == 'body':
        target_name = 'ioElectrical'
    
    if source_name == 'battery':
        target_name = 'energyStorageAndDistribution'
    
    return target_name;

def copy_and_trace_elements(source_host, source_id, target_host, target_id, cTraceabilityPackageName):
    rep_t = []

    rep_source = read_full_repository(source_host, source_id)

    rep_target = read_full_repository(target_host, target_id)
        

    
    for i in range(len(rep_source)):
        rep_t.append({"payload": rep_source[i],
                      "identity": {"@id": rep_source[i]['@id']}})
                      
                      
        
    bLink = True    
    if bLink == True:
        source_names = [item.get('name') for item in rep_source if item.get('name') is not None]
        
        # Initialize source_ok and target_ok to None or a default value
        source_ok = None
        target_ok = None
        t = None
        tar = None
        n = None

        # Create package for traceability links
        IdOfPackageForDependencies = str(uuid.uuid4())
        rep_t.append(dictionary_payload_package(IdOfPackageForDependencies,cTraceabilityPackageName))
        
           
            
        for source_name in source_names:
        
            source_ok = '';
            target_ok = '';
            target_name = target_object_lookup(source_name);
        
            for i in range(len(rep_source)):
                if rep_source[i].get('@type') == 'PartUsage' and rep_source[i].get('name') == source_name:
                    #print(rep_source[i].get('name'))
                    t = rep_source[i].get('@id')
                    n = rep_source[i].get('name')
                    source_ok = rep_source[i]

            for i in range(len(rep_target)):
                if rep_target[i].get('@type') == 'PartUsage' and rep_target[i].get('name') == target_name:
                    #print(rep_target[i].get('name'))
                    tar = rep_target[i].get('@id')
                    target_ok = rep_target[i]


            if source_ok != '' and target_ok != '':
                print ('TRACEABILITY LINK: ' + source_name + ' -> ' + target_name)
                ele_id=str(uuid.uuid4())
                owningmembership_element = str(uuid.uuid4())
                rep_t.append(dictionary_payload_owningmembership(owningmembership_element, {'@id': ele_id}, ele_id, {'@id': ele_id}, ele_id, {'@id': ele_id}, '', {'@id':IdOfPackageForDependencies}))
                d_payload_dependency = dictionary_payload_allocationusage(ele_id, {'@id': t}, {'@id': tar}, {'@id': owningmembership_element}, n, {'@id': tar})    
                rep_t.append(d_payload_dependency)
    

        
    commit_body1 = '{"change":' + json.dumps(rep_t) + '}'
    #print(commit_body1)
    response = requests.post(target_host + "/projects/" +target_id+ "/commits", headers={"Content-Type": "application/json"}, data = commit_body1)
    
    if response.status_code != 200:
        print(response.json())
        return False , response.json()
    else:
        return True , response.json()
 

def execute_writing(cMirrorProjectID,cServerName,scr,strModelName):
    cMirrorProject=cMirrorProjectID.get()
    cMirrorServerName=cServerName.get()
    print('Reading Base Architecture from mirror server '+ cMirrorServerName + '...')
    cSysMLBaseArch = readBaseArchitecture(cMirrorProject,cMirrorServerName)
    print(cSysMLBaseArch)
    cTraceabilityPackageName = 'TraceabilityLinks'
    #cSysMLString = (scr.get('1.0', tk.END)+ " ").replace('\\n','\\r\\n').strip()+"\r\n"
    cSysMLString = (scr.get('1.0', tk.END)+ " ").strip()+"\r\n"
    cHost,cProjectID = WriteSysML(cSysMLBaseArch + cSysMLString, strModelName)
    if cServerName.get()!='':
       print('Writing to the mirror server '+ cMirrorServerName + '...')
       bSuccess,sInfo = copy_and_trace_elements(cHost, cProjectID, cMirrorServerName, cMirrorProject,cTraceabilityPackageName)
       if bSuccess:
           print("Successfully wrote to project '" + cMirrorProject + "' - Id: " + cMirrorProject )
       else:
           print("Writing failed to project " + cMirrorProject + " - Id: " + cMirrorProject)

def readBaseArchitecture(cMirrorProjectID,cServerName):
    PackageName = ''
    PartName = ''
    AttributeName = ''
    AttributeType = ''
    ItemName = ''
    ItemType = ''
    Multiplicity = ''
    ItemUsage = ''
    rep = read_full_repository(cServerName, cMirrorProjectID)
    for i in range(len(rep)):
        currentRecord=rep[i]
        if str(currentRecord.get('shortName'))!="None":
           if currentRecord.get('shortName') == 'BA':
               print('Found ' + currentRecord.get('@type'))
               if currentRecord.get('@type') == 'Package':
                   PackageName = currentRecord.get('name')
               if currentRecord.get('@type') == 'PartDefinition':
                   PartName = currentRecord.get('name')
               if currentRecord.get('@type') == 'AttributeUsage':
                   AttributeName = currentRecord.get('name')
               if currentRecord.get('@type') == 'LiteralInteger':
                   Multiplicity = str(currentRecord.get('value'))
               if currentRecord.get('@type') == 'AttributeDefinition':
                   AttributeType = currentRecord.get('qualifiedName').replace('Base','')
               if currentRecord.get('@type') == 'ItemUsage':
                  print('ItemUsage ' + str(len(str(currentRecord.get('featuringType')))))
                  if len(str(currentRecord.get('featuringType')))>2:
                      ItemName = currentRecord.get('name')
                  else:
                      ItemUsage = currentRecord.get('name')
                     
               if currentRecord.get('@type') == 'ItemDefinition':
                  ItemType = currentRecord.get('qualifiedName').replace('RectangularCuboid','Box')
              

        
    
    cSysML='package <BA> ' + PackageName + ' {\r\n'
    cSysML = cSysML + '    abstract part def <BApart> ' + PartName +' {\r\n'
    cSysML = cSysML + '        attribute  <BAattribute> ' + AttributeName + ' : ' + AttributeType +';\r\n'
    cSysML = cSysML + '        item  <BAitem> ' + ItemName + ' : ' + ItemType + ' ['+ Multiplicity +'] :> ' + ItemUsage + ';\r\n'
    cSysML = cSysML + '    }\r\n'
    cSysML = cSysML + '}\r\n'


    return cSysML


def run_traceability_tool(cProjectUUID, cHost, cFolder):
     mainWindow = Tk()
     mainWindow.title("Traceability tool")
     frm = ttk.Frame(mainWindow)
     frm.grid(row=0, column=0, columnspan=3)

     cProjectID = StringVar()
     cProjectID.set(cProjectUUID)
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
     ttk.Label(frm, text="Project UUID").grid(column=0, row=3)
     ttk.Entry(frm, textvariable = cProjectID, width = 50).grid(column=1, row=3)
     bSuccess = True
     ttk.Button(frm, text="Select", command=partial(selectproject,cProjectID,cServerName)).grid(column=2, row=3)
     ttk.Label(frm, text="").grid(column=0, row=4)
     ttk.Label(frm, text="Write Physical Architecture here:").grid(column=0, row=6)
     scr = scrolledtext.ScrolledText(mainWindow, width = 150, height = 35, font = ("Courier", 9))
     scr.grid(column = 0, pady = 10, padx = 10)


     ttk.Button(frm, text="Go", command=partial(execute_writing,cProjectID,cServerName,scr,strModelName)).grid(column=1, row=5)
     ttk.Button(frm, text="Quit", command=mainWindow.destroy).grid(column=3, row=5)
     mainWindow.mainloop()


def main(): 
    cProject= ''
    cHost = ''
    cFolder = ''


    run_traceability_tool(cProject, cHost, cFolder)

if __name__ == "__main__":
    main()
