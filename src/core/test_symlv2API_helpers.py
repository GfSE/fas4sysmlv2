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

#   This code performs stress tests on the repository read functions
#   with high model size and hence enforces multi-page HTML responses 
#   to test if those are properly handled

import sys
import os
import platform
import requests 
import json
import uuid
from datetime import datetime
from fas4sysmlv2API_helpers import *
 
def DumpJupyterNotebook(cWorkingFolderAndOutputFile, cWorkingFolderAndInputFile, cSysMLString):
     cNotebookFile = cWorkingFolderAndOutputFile
     FID1=open(cWorkingFolderAndInputFile,'r');
     FID2=open(cNotebookFile,'w');
     for tline in FID1:
         num = tline.find('"<Paste SysMLv2 code here>"')
         if num > -1:
             cCommaBlankAndQuotationMark=',' + '\r\n' + '    "'
             cCodedSysML='    "' + cSysMLString.replace('\r\n','\\n"' + cCommaBlankAndQuotationMark)   
             #Remove final comma, blank and quotation mark 
             cCodedSysML = cCodedSysML[:(len(cCodedSysML)-len(cCommaBlankAndQuotationMark))]
             FID2.write(cCodedSysML )
         else:
             FID2.write(tline)
     FID1.close()
     FID2.close()
     return cNotebookFile 




cServerName=''

print('NumFlowsInput;NumFlowsReadByQuery;NumFlowsReadByFullRead;Len')


for iNumParts in [2, 10, 1000, 5000]:
         if iNumParts == 2:
            # Write a simple example via the SysML reference implementation to obtain the server name that is configured there
            SysMLstring =''

            clParts = []
            clFlows =  []
            clItems = []
            SysMLstring = SysMLstring + 'package PartUsages{'
            for iCount in (range(iNumParts)):
                clParts.append('partUsage' + str(iCount))
            for iCount in (range(iNumParts)):
                cPartUsage = clParts[iCount]
                SysMLstring = SysMLstring + '\r\n    part ' + cPartUsage + '{'
                SysMLstring = SysMLstring + '\r\n    }'
                
                
            SysMLstring = SysMLstring + '\r\n}'
               
            SysMLstring = SysMLstring + '\r\n'

            
                

            cWorkingFolder=''
            cNotebookFile = cWorkingFolder + 'temp_fas_input_writer.ipynb' 
            FID =open(cNotebookFile ,'w');
            FID.write('{\n "cells": [\n  {\n   "cell_type": "markdown",\n   "id": "237f75ac",\n   "metadata": {},\n   "source": [\n    "FAS for SysMLv2: FAS Input to Repository Writer\\n",\n    "=="\n   ]\n  },\n  {\n   "cell_type": "code",\n   "execution_count": null,\n   "id": "f4fe084d",\n   "metadata": {},\n   "outputs": [],\n   "source": [\n    "<Paste SysMLv2 code here>"\n   ]\n  },\n  {\n   "cell_type": "code",\n   "execution_count": null,\n   "id": "7e04e6fc",\n   "metadata": {},\n   "outputs": [],\n   "source": [\n    "%publish PartUsages"\n   ]\n  }\n ],\n "metadata": {\n  "kernelspec": {\n   "display_name": "SysML",\n   "language": "sysml",\n   "name": "sysml"\n  },\n  "language_info": {\n   "codemirror_mode": "sysml",\n   "file_extension": ".sysml",\n   "mimetype": "text/x-sysml",\n   "name": "SysML",\n   "pygments_lexer": "java",\n   "version": "1.0.0"\n  }\n },\n "nbformat": 4,\n "nbformat_minor": 5\n}\n')
            FID.close()

            cOutputFile = cWorkingFolder + 'temp_output.ipynb'
            cResultFile = cWorkingFolder + 'temp_result.ipynb'

            DumpJupyterNotebook(cOutputFile, cNotebookFile, SysMLstring)


            if platform.system()!='Windows':
             cSilencer='2>/dev/null'
             os.system('jupyter nbconvert --to notebook --execute ' + cOutputFile + ' --stdout >' + cResultFile + ' ' + cSilencer)
            else:
             cSilencer='>nul 2>&1';
             os.system('jupyter nbconvert --to notebook --execute ' + cOutputFile + ' --output=' + cResultFile + ' ' + cSilencer)

            status = ''
            FID1=open(cResultFile ,'r');
            bStdout = False
            bData = False
            bResultExpected = False
            for tline in FID1:
                if bResultExpected:
                    cStatus = 'STATUS: ' + tline.replace('\\n','').replace('\\r','').strip()
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
                    #print(cHost)
                    cServerName=cHost
            

            targetProjectID = ''
            if cStatus.find('Saved to Project') < 0:
                print('Error in commit to temporary project')
            else:
                posOpeningParenthesis = cStatus.find('(')
                posClosingParenthesis = cStatus.find(')')
                targetProjectID = cStatus[(posOpeningParenthesis+1):posClosingParenthesis]
                #print('--------- project ID: ' + targetProjectID  +  ' ---------------' ) 
         else:
                timestamp = datetime.now()
                project_name = f"Test Project  - {timestamp}"
                response = requests.post(cServerName + "/projects", headers={"Content-Type": "application/json"}, data=json.dumps({"name":project_name}))
                if response.status_code!=200:
                    print('FAILED to create project')
                targetProjectID=response.json().get('@id')
                #print('--------- project ID: ' + targetProjectID  +  ' ---------------' ) 
                payloadArray = []

                for iPartNo in range(iNumParts):
                    cPackageName = 'MyPackage' + str(iPartNo+1)
                    cPartName = 'MyPart' + str(iPartNo+1)
                    part_element_id = str(uuid.uuid4())
                    package_element_id = str(uuid.uuid4())
                    owningmembership_element_id = str(uuid.uuid4())
                    payloadArray.append(dictionary_payload_package(package_element_id, cPackageName , cPartName))
                    payloadArray.append(dictionary_payload_partusage(part_element_id, cPartName, cPartName))
                    payloadArray.append(dictionary_payload_owningmembership(owningmembership_element_id, {'@id': part_element_id}, part_element_id, {'@id': part_element_id}, part_element_id, {'@id': part_element_id}, '', {'@id': package_element_id}))
                    #print('--------------')
                    #print(payloadArray)
                    #print('--------------')
                    if len(payloadArray) > 1999:
                        #Commit in chunks if payload gets too large
                        commit_body =  '{"change": ' + json.dumps(payloadArray) +'}'
                        payloadArray = []
                        commit_url = f"{cServerName}/projects/{targetProjectID}/commits" 
                        response = requests.post(commit_url, 
                                      headers={"Content-Type": "application/json"}, 
                                      data=commit_body)
                        #print('   ... Status of partial commit: ' + str(response.status_code))

 
                commit_body =  '{"change": ' + json.dumps(payloadArray) +'}'
                commit_url = f"{cServerName}/projects/{targetProjectID}/commits" 

                response = requests.post(commit_url, 
                                      headers={"Content-Type": "application/json"}, 
                                      data=commit_body)

                #print('   ... Status of final commit: ' + str(response.status_code))
                if response.status_code!=200:
                    print('FAILED to commit to project')
                    print (response.json())

         if cServerName == '':
            print('Could not determine server name')
         else:
            bSuccess = True
            if len(targetProjectID) > 0:
                 cErrorMessage = ''
                 cProjectID=targetProjectID
                 
                
                 try:
                     response = requests.get(cServerName + "/projects/" + cProjectID)
                 except  requests.exceptions.ConnectionError:
                     bSuccess = False
                     cErrorMessage = 'Error: Could not connect to server'
                     print(cErrorMessage)

                     
                 if bSuccess and str(response)!='<Response [200]>':
                     bSuccess = False
                     cErrorMessage = 'Error: Could not find project on stated host'
                     print('Error: Could not find project on stated host')

                 



                 if bSuccess:

                     iCounterQuery = 0
                     iCounterFullRead = 0

                     data = run_query_for_elementtyp('OwningMembership', cServerName, cProjectID)
                     #print(data)
                     for response in data:
                         if response.get("@type") == 'OwningMembership':
                             iCounterQuery = iCounterQuery + 1
                     
                     data = read_full_repository(cServerName, cProjectID)
                 
                     for response in data:
                         if response.get("@type") == 'OwningMembership':
                             iCounterFullRead = iCounterFullRead + 1
                     
                     
                     print(str(iNumParts)+';'+str(iCounterQuery)+';'+str(iCounterFullRead)+';'+str(len(str(data))) + ';(project ID: ' + cProjectID  +  ')' ) 
                     if iNumParts != iCounterQuery or iNumParts != iCounterFullRead :
                         print('FAILED')                







