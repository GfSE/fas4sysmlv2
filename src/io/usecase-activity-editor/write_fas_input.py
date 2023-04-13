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
# The code wraps around fas_frontend() to store the output of that function 
# in the SysML repository, via the execution of a juypter notebook for SysML.
#
# The input comes via a file written from OpenOffice, with graphical information about the use case activities and their flows.
#
#

from fas_frontend import *
import sys
import os
import platform
 
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

def main():
     cFileName = sys.argv[1]
     cWorkingFolder = sys.argv[2]
     cWorkingFolder = cWorkingFolder.replace('"','').strip()

     clActivitiesAndObjectFlows, clFunctionalGroups, cSysMLString = fas_frontend(cFileName,'')

     print('')
     print('Storing the result in the repository ...')
     cNotebookFile = cWorkingFolder + 'fas_input_writer.ipynb' 
     cOutputFile = cWorkingFolder + 'temp_output.ipynb'
     cResultFile = cWorkingFolder + 'temp_result.ipynb'
     DumpJupyterNotebook(cOutputFile, cNotebookFile, cSysMLString)

     if  platform.system()!='Windows':
         cSilencer='>/dev/null 2>&1'
     else:
         cSilencer='>nul 2>&1';

     os.system('jupyter nbconvert --to notebook --execute ' + cOutputFile + ' --output=' + cResultFile + ' ' + cSilencer)

     FID1=open(cResultFile ,'r');
     bStdout = False
     bData = False
     bResultExpected = False
     for tline in FID1:
         if bResultExpected:
             print('STATUS: ' + tline.replace('\\n','').replace('\\r','').strip())
             break
         if tline.find('"name": "stdout",')>-1:
             bStdout = True
         if tline.find('"data": {')>-1 and bStdout:
             bData = True
         if tline.find('"text/plain": [')>-1 and bData:
             bResultExpected = True
     FID1.close()
     

if __name__ == "__main__":
    main()

  
