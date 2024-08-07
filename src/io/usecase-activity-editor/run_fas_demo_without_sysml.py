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
# The code wraps around fas_frontend() and around the block diagram renderer to use them for a very basic demo of the FAS method, 
# without a SysML v2 repository in the middle
#
# Call: python run_fas_demo_without_sysml.py <file name of input file from OpenOffice> <folder name of working folder> 
#
# The input comes via a file written from OpenOffice, with graphical information about the use case activities and their flows.
#
# Based on: Lamm, J.G.: "Eine schlanke Formel fuer den Kern der FAS-Methode, zur einfachen Werkzeug-
# Umsetzung der Methode", in Koch, W.; Wilke, D.; Dreiseitel, S.; Kaffenberger, R. (Eds.): Tag des Systems Engineering - 
# Paderborn 16.-18. November 2022, Gesellschaft fuer Systems Engineering e.V. (GfSE Verlag), Bremen, Germany, 2022, pp. 127-131
# 
# English Translation of the above paper: https://github.com/GfSE/fas4sysmlv2/blob/main/doc/tech-docs/fas/FAS-as-a-formula-2022.odt	
#



from fas_frontend import *
from write_fas_input import DumpJupyterNotebook
from sympy import *
import sys
import os
import platform
import hashlib
    
def SymbolicUpdateMatrixWithFlow(clDomainObjects,clActivities,mMatrixO, sLineToParse):
     sSourceObject,sFlow,sTargetObject = parseFlowLine(sLineToParse)
     clDomainObjects = UpdateUniqueContentCellArray (clDomainObjects, sFlow)
     M = len(clActivities);
     mNewMatrixO = mMatrixO
     
     if mNewMatrixO.shape[0] == 0:
         mNewMatrixO = Matrix([[0 for col in range(M)] for row in range(M)])
     for nInitIndex1 in range(M):
         for nInitIndex2  in range(M):
             if GetIndexOfStringInCellArray(clActivities,sSourceObject) == nInitIndex1 and GetIndexOfStringInCellArray(clActivities,sTargetObject) == nInitIndex2 :
                 mTemp = [[0 for col in range(M)] for row in range(M)]
                 sFlowSymbolic = symbols(sFlow)
                 mTemp[nInitIndex1][nInitIndex2] = sFlowSymbolic
                 mNewMatrixO = mNewMatrixO + Matrix(mTemp)

    
     return clDomainObjects,clActivities,mNewMatrixO 
 
 
def RenderFunctionalArchitecture(F,clFunctionalBlockNames):
    
     clFunctionalBlocksAndFlows= []    

  
     cSysMLstring = '   part functionalSystem{' + '\r\n'

    
     clSourcePortNames = [['' for col in range(F.shape[0])] for row in range(F.shape[0])]
     clTargetPortNames = [['' for col in range(F.shape[0])] for row in range(F.shape[0])]
     for nBlock in range(F.shape[0]):
         cCurrentBlock = clFunctionalBlockNames[nBlock]
         cSysMLstring = cSysMLstring + '      part ' + wrapNameInCorrectQuotes(cCurrentBlock) + '{' + '\r\n'
         iPortNo = 0
         for nPortOut in range(F.shape[0]):
             if F[nBlock,nPortOut]!= 0: 
                 if nPortOut != nBlock:
                     sFlowName = str(F[nBlock,nPortOut])
                     iNumPorts = max(1,sFlowName.strip().count('+')+1)
                     clPortCell = ['' for col in range(iNumPorts)]
                     for nPort in range(iNumPorts):
                         iPortNo = iPortNo  + 1
                         cPortName = 'p' + str(iPortNo)
                         cSysMLstring = cSysMLstring + '         port ' + wrapNameInCorrectQuotes(cPortName) + ';' + '\r\n'
                         clPortCell[nPort]=cPortName
            
                         clSourcePortNames[nBlock][nPortOut]=clPortCell
                 
         for nPortIn in range(F.shape[0]):
             if F[nPortIn, nBlock]!= 0: 
                 if nPortIn != nBlock:
                     sFlowName = str(F[nPortIn,nBlock])
                     iNumPorts = max(1,sFlowName.strip().count('+')+1)
                     clPortCell = ['' for col in range(iNumPorts)]
                     for nPort in range(iNumPorts):
                         iPortNo = iPortNo + 1
                         cPortName = 'p' + str(iPortNo)
                         cSysMLstring = cSysMLstring + '         port ' + wrapNameInCorrectQuotes(cPortName) + ';' + '\r\n'
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
                     cSysMLstring = cSysMLstring + '      flow of ' + wrapNameInCorrectQuotes(sCurrentFlowName) + ' from ' + wrapNameInCorrectQuotes(clFunctionalBlockNames[nBlock1]) + '.' + wrapNameInCorrectQuotes(clSourcePorts[nPort]) + ' to ' + wrapNameInCorrectQuotes(clFunctionalBlockNames[nBlock2]) + '.' + wrapNameInCorrectQuotes(clTargetPorts[nPort]) + ';' + '\r\n'
           
                     clFunctionalBlocksAndFlows.append({"source": clFunctionalBlockNames[nBlock1], "flow": sCurrentFlowName, "target":   clFunctionalBlockNames[nBlock2]})
    
    ## Trace Functional Blocks to Functional Groups
     for nBlock in range(F.shape[0]):
         sCurrentName = clFunctionalBlockNames[nBlock]
         cItemString = cItemString + '   dependency from functionalSystem::' + wrapNameInCorrectQuotes(sCurrentName) + ' to FunctionalGroups::' + wrapNameInCorrectQuotes(sCurrentName) + ';' + '\r\n'
    
      
     cSysMLstring = cSysMLstring + '   }' + '\r\n' + cItemString 
   
     return  cSysMLstring, clFunctionalBlocksAndFlows
 
 
def RunFas(clActivitiesAndObjectFlows, clFunctionalGroups, clActivityNamesInSortOrder ):

     cSysMLString=''
     cLatexString = ''
    
     ### Process Activities and Object Flows
     clLinesToParse =  clActivitiesAndObjectFlows
     clDomainObjects = []
     clActivities = clActivityNamesInSortOrder 
     mSymbolicMatrixO = Matrix([])
  
     for nIndex in range(len(clLinesToParse)):
         sLineToParse = clLinesToParse[nIndex]
         clDomainObjects,clActivities,mSymbolicMatrixO = SymbolicUpdateMatrixWithFlow(clDomainObjects,clActivities,mSymbolicMatrixO, sLineToParse)
     
     
     print('O = (symbolic ' + str(mSymbolicMatrixO.shape[0]) + 'x' + str(mSymbolicMatrixO.shape[1]) + ' matrix)')
     print('')
     pprint(mSymbolicMatrixO)
     cLatexString = cLatexString + '\\[\n   ' + 'O=' + latex(mSymbolicMatrixO).replace('[','(').replace(']',')') + '\n\\]\n'
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
     cLatexString = cLatexString + '\\[\n   ' + 'G=' + latex(mSymbolicMatrixG).replace('[','(').replace(']',')') + '\n\\]\n'
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
     cLatexString = cLatexString + '\\[\n   ' + latex(Eq(F, GOG**T)).replace('[','(').replace(']',')') + '\n\\]\n'
     print('')
     print('---------------------------------')
     print('')  
     
     print('F = (symbolic ' + str(mSymbolicMatrixF.shape[0]) + 'x' + str(mSymbolicMatrixF.shape[1]) + ' matrix)')
     print('')
     pprint(mSymbolicMatrixF)
     cLatexString = cLatexString + '\\[\n   ' + 'F=' + latex(mSymbolicMatrixF).replace('[','(').replace(']',')') + '\n\\]\n'
     print('')    
     
     ### FAS method says that names of functional blocks are equal to names of functional groups
     clFunctionalBlockNames = clGroupName
     
     ### Print the functional architecture
     cSysMLString, clFunctionalBlocksAndFlows = RenderFunctionalArchitecture(mSymbolicMatrixF,clFunctionalBlockNames)

     for cDom in clDomainObjects:
         cLatexString = cLatexString.replace(cDom,'\\textrm{' + cDom + '}')
     cLatexPreamble = '\\documentclass[english]{article}\\usepackage[T1]{fontenc}\\usepackage[latin9]{inputenc}\\usepackage{amsmath}\\usepackage{babel}\n\\begin{document}\n'
     
     # Uncomment the following line to get matrices printed as Latex code
     # print(cLatexPreamble + cLatexString + '\\end{document}')

     return cSysMLString, clFunctionalBlocksAndFlows    




if sys.version_info[0] < 3 or sys.version_info[1]<9 and platform.system()!='Windows':
     raise Exception("Python version is insufficient. Python 3.9 or higher is required.")

init_printing(use_unicode=False)
cFileName = sys.argv[1]
cWorkingFolder = sys.argv[2]
cWorkingFolder = cWorkingFolder.replace('"','').strip()

sys.path.insert(1,cWorkingFolder.replace('usecase-activity-editor\\','').replace('usecase-activity-editor/','').replace('io','core'))
sys.path.insert(1,cWorkingFolder.replace('usecase-activity-editor\\','').replace('usecase-activity-editor/','')+'functional-architecture-browser')

from blockdiagram_renderer import *
     
clActivitiesAndObjectFlows, clFunctionalGroups, cSysMLString, clActivityNamesInSortOrder  = fas_frontend(cFileName,'')

#Clear screen
if platform.system()!='Windows':
     print('\033[2J\033[H\033[3J')
else:
     os.system('cls')

print ('Computing ...')
print('')
cSysMLString, clFunctionalBlocksAndFlows = RunFas(clActivitiesAndObjectFlows, clFunctionalGroups, clActivityNamesInSortOrder )
print('   Computing done.');


print('Visualizing the result ...');
mainWindow = Tk()
mainWindow.title("Functional Architecture Renderer")
frm = ttk.Frame(mainWindow)
frm.grid(row=0, column=0, columnspan=1)
ttk.Label(frm, text="Rendering starts ...").grid(column=0, row=0)

strBaseURLParam=StringVar()
cProjectID=StringVar()
cServerName=StringVar()
strBaseURLParam.set('')
cProjectID.set('')
cServerName.set('')
mainWindow.after_idle(partial(render_diagram,cProjectID,cServerName,mainWindow,strBaseURLParam, clFunctionalBlocksAndFlows, True, cWorkingFolder))

mainWindow.mainloop()


print('   Visualizing done.');


  
