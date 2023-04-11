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


# This is python code that has been translated from GNU Octave 
# The SymPy package is needed for symbolic computations

#
# The code wraps around fas_frontend() to test that function.
#
# The input comes via a file written from OpenOffice, with graphical information about the use case activities and their flows.
#
# Based on: Lamm, J.G.: "Eine schlanke Formel fuer den Kern der FAS-Methode, zur einfachen Werkzeug-
# Umsetzung der Methode", in Koch, W.; Wilke, D.; Dreiseitel, S.; Kaffenberger, R. (Eds.): Tag des Systems Engineering - 
# Paderborn 16.-18. November 2022, Gesellschaft fuer Systems Engineering e.V. (GfSE Verlag), Bremen, Germany, 2022, pp. 127-131
# 
# English Translation of the above paper: https://github.com/GfSE/fas4sysmlv2/blob/main/doc/tech-docs/fas/FAS-as-a-formula-2022.odt	


from fas_frontend import *
from sympy import *
import sys
import os
import platform
    
def SymbolicUpdateMatrixWithFlow(clDomainObjects,clActivities,mMatrixO, sLineToParse):
     sSourceObject,sFlow,sTargetObject = parseFlowLine(sLineToParse)
     clActivities = UpdateUniqueContentCellArray (clActivities, sSourceObject)
     clActivities = UpdateUniqueContentCellArray (clActivities, sTargetObject)
     clDomainObjects = UpdateUniqueContentCellArray (clDomainObjects, sFlow)
     M = len(clActivities);
     mNewMatrixO = Matrix([[0 for col in range(M)] for row in range(M)])
     for nInitIndex1 in range(M):
         for nInitIndex2  in range(M):
             mShape=mMatrixO.shape
             if nInitIndex1 < mShape[0] and nInitIndex2 < mShape[0]:
                 mTemp = [[0 for col in range(M)] for row in range(M)]
                 mTemp[nInitIndex1][nInitIndex2] = mMatrixO[nInitIndex1,nInitIndex2]
                 mNewMatrixO = mNewMatrixO + Matrix(mTemp)
             if GetIndexOfStringInCellArray(clActivities,sSourceObject) == nInitIndex1 and GetIndexOfStringInCellArray(clActivities,sTargetObject) == nInitIndex2 :
                 mTemp = [[0 for col in range(M)] for row in range(M)]
                 sFlowSymbolic = symbols(sFlow)
                 mTemp[nInitIndex1][nInitIndex2] = sFlowSymbolic
                 mNewMatrixO = mNewMatrixO + Matrix(mTemp)

    
     return clDomainObjects,clActivities,mNewMatrixO 
 
 
def RenderFunctionalArchitecture(F,clFunctionalBlockNames):
  
     cSysMLstring = '   part FunctionalSystem{' + '\r\n'

    
     clSourcePortNames = [['' for col in range(F.shape[0])] for row in range(F.shape[0])]
     clTargetPortNames = [['' for col in range(F.shape[0])] for row in range(F.shape[0])]
     for nBlock in range(F.shape[0]):
         cCurrentBlock = clFunctionalBlockNames[nBlock]
         cSysMLstring = cSysMLstring + '      part ' + cCurrentBlock + '{' + '\r\n'
         iPortNo = 0
         for nPortOut in range(F.shape[0]):
             if F[nBlock,nPortOut]!= 0: 
                 sFlowName = str(F[nBlock,nPortOut])
                 iNumPorts = max(1,sFlowName.strip().count('+')+1)
                 clPortCell = ['' for col in range(iNumPorts)]
                 for nPort in range(iNumPorts):
                    iPortNo = iPortNo  + 1
                    cPortName = 'p' + str(iPortNo)
                    cSysMLstring = cSysMLstring + '         port ' + cPortName + ';' + '\r\n'
                    clPortCell[nPort]=cPortName
            
                 clSourcePortNames[nBlock][nPortOut]=clPortCell
                 
         for nPortIn in range(F.shape[0]):
             if F[nPortIn, nBlock]!= 0: 
                 sFlowName = str(F[nPortIn,nBlock])
                 iNumPorts = max(1,sFlowName.strip().count('+')+1)
                 clPortCell = ['' for col in range(iNumPorts)]
                 for nPort in range(iNumPorts):
                    iPortNo = iPortNo + 1
                    cPortName = 'p' + str(iPortNo)
                    cSysMLstring = cSysMLstring + '         port ' + cPortName + ';' + '\r\n'
                    clPortCell[nPort]=cPortName
               
             clTargetPortNames[nPortIn][nBlock]=clPortCell
         cSysMLstring = cSysMLstring + '      }' + '\r\n'
   
    
    ## Connect the blocks with flows
     cItemString = ''
    
     for nBlock1 in range(F.shape[0]):
         for nBlock2 in range(F.shape[0]):
             cFlow=F[nBlock1,nBlock2]
             if nBlock1 != nBlock2 and cFlow != 0: 
                 sFlowName = str(cFlow)
                 clSourcePorts = clSourcePortNames[nBlock1][nBlock2]
                 clTargetPorts = clTargetPortNames[nBlock1][nBlock2]
                 for nPort in range(len(clSourcePorts)):
                     sCurrentFlowName = SubFlow(sFlowName,nPort)
                     cSysMLstring = cSysMLstring + '      flow of ' + sCurrentFlowName + ' from ' + clFunctionalBlockNames[nBlock1] + '.' + clSourcePorts[nPort] + ' to ' + clFunctionalBlockNames[nBlock2] + '.' + clTargetPorts[nPort] + ';' + '\r\n'
                     cItemString = cItemString + '   item def ' + sCurrentFlowName + ';' + '\r\n'
           
    
    ## Trace Functional Blocks to Functional Groups
     for nBlock in range(F.shape[0]):
         sCurrentName = clFunctionalBlockNames[nBlock]
         cItemString = cItemString + '   dependency from FunctionalSystem::' + sCurrentName + ' to UseCaseActivities::FunctionalGroups::' + sCurrentName + ';' + '\r\n'
    
      
     cSysMLstring = cSysMLstring + '   }' + '\r\n' + cItemString 
   
     return  cSysMLstring
 
 
def RunFas(clActivitiesAndObjectFlows, clFunctionalGroups):

     cSysMLString=''
    
     ### Process Activities and Object Flows
     clLinesToParse =  clActivitiesAndObjectFlows
     clDomainObjects = []
     clActivities = []
     mSymbolicMatrixO = Matrix([])
  
     for nIndex in range(len(clLinesToParse)):
         sLineToParse = clLinesToParse[nIndex]
         clDomainObjects,clActivities,mSymbolicMatrixO = SymbolicUpdateMatrixWithFlow(clDomainObjects,clActivities,mSymbolicMatrixO, sLineToParse)
     
     
     print('O = (symbolic ' + str(mSymbolicMatrixO.shape[0]) + 'x' + str(mSymbolicMatrixO.shape[1]) + ' matrix)')
     print('')
     pprint(mSymbolicMatrixO)
     print('')
     
     M=mSymbolicMatrixO.shape[0]

    
     ### Process Functional Groupings
     clLinesToParse =  clFunctionalGroups  
     N = len(clLinesToParse)
     mSymbolicMatrixG = Matrix([[0 for col in range(M)] for row in range(N)])

     clGroupName = ['' for col in range(N)]
     for n in range(N):
         sLineToParse = clLinesToParse[n]
         sGroupName, clGroup = parseGroupLine(sLineToParse)
         clGroupName[n]=sGroupName
         for m in range(M):
             if GetIndexOfStringInCellArray(clGroup,clActivities[m]) > -1:
                 mTemp = [[0 for col in range(M)] for row in range(N)]
                 mTemp[n][m] = 1;
                 mSymbolicMatrixG = mSymbolicMatrixG + Matrix(mTemp)
          
   
     print('G = (symbolic ' + str(mSymbolicMatrixG.shape[0]) + 'x' + str(mSymbolicMatrixG.shape[1]) + ' matrix)')
     print('')
     pprint(mSymbolicMatrixG)
     print('')    
    
     
     ### Compute the functional architecture via FAS-as-a-formula
     ### F = G*O*G.T;
     mSymbolicMatrixF=mSymbolicMatrixG*mSymbolicMatrixO*mSymbolicMatrixG.T;
     
     print('---------------------------------')
     print('Applying FAS-as-a-formula:')
     print('')
     # Explanation of "FAS-as-a-formula": https://github.com/GfSE/fas4sysmlv2/blob/main/doc/tech-docs/fas/FAS-as-a-formula-2022.odt"
     GOG,T,F = symbols('GOG, T, F')
     #This is a work-around to print the formula F=G*O*G**T in nice formatting:
     pprint(Eq(F, GOG**T))
     print('')
     print('---------------------------------')
     print('')  
     
     print('F = (symbolic ' + str(mSymbolicMatrixF.shape[0]) + 'x' + str(mSymbolicMatrixF.shape[1]) + ' matrix)')
     print('')
     pprint(mSymbolicMatrixF)
     print('')    
     
     ### FAS method says that names of functional blocks are equal to names of functional groups
     clFunctionalBlockNames = clGroupName
     
     ### Print the functional architecture
     cSysMLString = RenderFunctionalArchitecture(mSymbolicMatrixF,clFunctionalBlockNames)
    
     return cSysMLString    

def DumpJupyterNotebook(cWorkingFolder, cSysMLString):
     cNotebookFile = cWorkingFolder + 'FunctionalModel.ipynb';
     FID1=open(cWorkingFolder + 'test_visuallly.ipynb','r');
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
 
  





init_printing(use_unicode=False)
cFileName = sys.argv[1]
cWorkingFolder = sys.argv[2]

clActivitiesAndObjectFlows, clFunctionalGroups, cSysMLString = fas_frontend(cFileName,cPath)

#Clear screen
if  platform.system()!='Windows':
	print('\033[2J\033[H\033[3J')
else:
	os.system('cls')

print ('Computing ...')
print('')
cSysMLString = 'package FunctionalModel{' + '\r\n' + cSysMLString
## Use fas-as-a-formula to test the obtained data 
cSysMLString = cSysMLString + RunFas(clActivitiesAndObjectFlows, clFunctionalGroups)
cSysMLString = cSysMLString + '}' + '\r\n'
cNotebookFile = DumpJupyterNotebook(cWorkingFolder, cSysMLString)
print('Done.');
print('Visualizing the result ...');
cHtmlFile = cNotebookFile.replace('.ipynb','.html')
if  platform.system()!='Windows':
     cSilencer='>/dev/null 2>&1'
     os.system('jupyter nbconvert --to html --execute ' + cNotebookFile + ' --output=' + cHtmlFile + ' ' + cSilencer);
     status=os.waitstatus_to_exitcode(os.system('firefox ' + cHtmlFile + ' ' + cSilencer))
     if status > 0:
         os.system('chrome ' + cHtmlFile + ' ' + cSilencer)
   
else:
     cSilencer='>nul 2>&1';
     os.system('jupyter nbconvert --to html --execute ' + cNotebookFile + ' --output=' + cHtmlFile + ' ' + cSilencer)
     os.system(cHtmlFile)
 


  
