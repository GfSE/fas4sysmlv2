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

#   This code creates a large model as a test vector for the FAS plugin

import sys
import os
import platform
import requests 
import json
from time import sleep
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



cServerName="http://localhost:9000"
print(cServerName)


iComplexity = 1
iTotalActCounter = 0
cInitialProject = ''
iOffset = 0
iNumActivities = 20
for iNumCommit in range(25):
            if iNumCommit > 0:
                iOffset = iOffset + iNumActivities
            SysMLstring =''
            SysMLstring = SysMLstring + 'package FunctionalModel{\r\n'
            clActivities = []
            clFlows =  []
            clItems = []
            if iComplexity > 0:
                for iCount in (range(iNumActivities-1)):
                    cItem = 'Item' + str(iCount+iOffset )
                    clItems.append(cItem) 
                    SysMLstring = SysMLstring + '  item def ' + cItem + ';\r\n'
                    
            SysMLstring = SysMLstring + '  package UseCaseActivities{'
            for iCount in (range(iNumActivities)):
                clActivities.append('act' + str(iCount+iOffset))
                clFlows.append('flow'  + str(iCount+iOffset))
            SysMLstring = SysMLstring + '\r\n    action ' + 'overallUseCase' + ' {'
            for iCount in (range(iNumActivities)):
                cAct = clActivities[iCount]
                cFlow = clFlows[iCount]
                SysMLstring = SysMLstring + '\r\n        action ' + cAct + '{'
                if iCount > 0:
                    SysMLstring = SysMLstring + '\r\n            in ' + clFlows[iCount-1] + ';'
                if iCount < len(clFlows)-1:
                    SysMLstring = SysMLstring + '\r\n            out ' + clFlows[iCount] + ';'
                SysMLstring = SysMLstring + '\r\n        }'
                
            for iCount in (range(iNumActivities-1)):
                if iComplexity == 0:
                    SysMLstring = SysMLstring + '\r\n        flow from ' + clActivities[iCount].lower() + '.' + clFlows[iCount] + ' to ' + clActivities[iCount+1].lower() + '.' + clFlows[iCount] + ';'
                else:
                    SysMLstring = SysMLstring + '\r\n        flow of ' + clItems[iCount] + ' from ' + clActivities[iCount].lower() + '.' + clFlows[iCount] + ' to ' + clActivities[iCount+1].lower() + '.' + clFlows[iCount] + ';'
                
            SysMLstring = SysMLstring + '\r\n    }'
            SysMLstring = SysMLstring + '\r\n    package FunctionalGroups{'
            iCount = 0
            iGroupCount=1
            while iCount+1 < iNumActivities:
                cAct1 = clActivities[iCount]
                cAct2 = clActivities[iCount+1]
                cGrp = 'Group'+str(iGroupCount+iOffset)
                SysMLstring = SysMLstring + '\r\n        package ' + cGrp + '{'
                SysMLstring = SysMLstring + '\r\n            import overallUseCase::' + cAct1 + ';'
                SysMLstring = SysMLstring + '\r\n            import overallUseCase::' + cAct2 + ';'
                SysMLstring = SysMLstring + '\r\n        }'
                iCount = iCount + 2
                iGroupCount = iGroupCount + 1

            SysMLstring = SysMLstring + '\r\n    }'
            SysMLstring = SysMLstring + '\r\n  }'

            SysMLstring = SysMLstring + '\r\n}'
               
            SysMLstring = SysMLstring + '\r\n'

            
            print(SysMLstring)
                
            print('Starting commit number ' + str(iNumCommit + 1))

            cWorkingFolder=''
            cNotebookFile = cWorkingFolder + 'temp_fas_input_writer.ipynb' 
            FID =open(cNotebookFile ,'w');
            FID.write('{\n "cells": [\n  {\n   "cell_type": "markdown",\n   "id": "237f75ac",\n   "metadata": {},\n   "source": [\n    "FAS for SysMLv2: FAS Input to Repository Writer\\n",\n    "=="\n   ]\n  },\n  {\n   "cell_type": "code",\n   "execution_count": null,\n   "id": "f4fe084d",\n   "metadata": {},\n   "outputs": [],\n   "source": [\n    "<Paste SysMLv2 code here>"\n   ]\n  },\n  {\n   "cell_type": "code",\n   "execution_count": null,\n   "id": "7e04e6fc",\n   "metadata": {},\n   "outputs": [],\n   "source": [\n    "%publish FunctionalModel"\n   ]\n  }\n ],\n "metadata": {\n  "kernelspec": {\n   "display_name": "SysML",\n   "language": "sysml",\n   "name": "sysml"\n  },\n  "language_info": {\n   "codemirror_mode": "sysml",\n   "file_extension": ".sysml",\n   "mimetype": "text/x-sysml",\n   "name": "SysML",\n   "pygments_lexer": "java",\n   "version": "1.0.0"\n  }\n },\n "nbformat": 4,\n "nbformat_minor": 5\n}\n')
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
             #print(tline)
             if bResultExpected:
                 status = 'STATUS: ' + tline.replace('\\n','').replace('\\r','').strip()
                 break
             if tline.find('"name": "stdout",')>-1:
                 bStdout = True
             if tline.find('"data": {')>-1 and bStdout:
                 bData = True
             if tline.find('"text/plain": [')>-1 and bData:
                 bResultExpected = True
            FID1.close()
            #print(status)

            targetProjectID = ''
            if status.find('Saved to Project') < 0:
                print('Error in commit to temporary project')
            else:
                posOpeningParenthesis = status.find('(')
                posClosingParenthesis = status.find(')')
                targetProjectID = status[(posOpeningParenthesis+1):posClosingParenthesis]



            sleep(3)
            bSuccess = True
            if len(targetProjectID) > 0:
                 cErrorMessage = ''
                 cProjectID=targetProjectID
                 
                 #print('Reading Use Case Activitiesfrom project ' + cProjectID + ' on server ' + cServerName + ' ...')
                
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
                     data = response.json()
                     oDefaultBranch = data.get('defaultBranch')
                     sDefaultBranchId=oDefaultBranch.get('@id')
                 
                     if str(type(oDefaultBranch)) == "<class 'NoneType'>":
                         bSuccess = False
                         cErrorMessage = 'Error: No default branch.'
                         print (cErrorMessage)
                 
                 if bSuccess:
                     response = requests.get(cServerName + "/projects/" + cProjectID + "/branches/" + sDefaultBranchId)
                     data = response.json()
                     oHeadCommit = data.get('head')
                     if str(type(oHeadCommit)) == "<class 'NoneType'>":
                         bSuccess = False
                         cErrorMessage = 'Error: No commit found.'
                         print (cErrorMessage)
                     else:
                         sHeadCommit = oHeadCommit.get('@id')


                 if bSuccess:
                     data = read_full_repository(cServerName, cProjectID)
                 

                     iCounter = 0
                     for response in data:

                         if response.get("@type") == 'FlowConnectionUsage':
                             iCounter = iCounter + 1
                     
                     
                     print(str(iComplexity)+';'+str(iNumActivities-1)+';'+str(iCounter)+';'+str(len(str(data))))   
                     if iNumActivities-1 == iCounter and iNumCommit==0:
                         iTotalActCounter = iTotalActCounter + iNumActivities

                     print('Project ID: ' + cProjectID )     

                     if iNumCommit == 0:
                         cInitialProject = cProjectID 
                     else:
                         #Copy back into intial project
                         status, result = copy_elements(cServerName, cProjectID , cServerName, cInitialProject )
                         if status == True:
                             print('Copied into project: ' + cInitialProject )
                             if iNumActivities-1 == iCounter:
                                 iTotalActCounter = iTotalActCounter + iNumActivities
                                 print('Total number of activities in project ' + cInitialProject + ': ' +str(iTotalActCounter))  
                                 sleep(2)
                         else:
                             print('Error copying')







