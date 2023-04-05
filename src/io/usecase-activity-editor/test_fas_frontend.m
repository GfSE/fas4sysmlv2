%   Copyright 2022 Gesellschaft fuer Systems Engineering e.V. (GfSE)
%   Licensed under the Apache License, Version 2.0 (the "License");
%   you may not use this file except in compliance with the License.
%   You may obtain a copy of the License at
%        http://www.apache.org/licenses/LICENSE-2.0  
%   Unless required by applicable law or agreed to in writing, software
%   distributed under the License is distributed on an "AS IS" BASIS,
%   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
%   See the License for the specific language governing permissions and
%   limitations under the License.


% This is code for GNU Octave with the "symbolic" toolbox installed 
% Install with "pkg install -forge symbolic" on the Octave prompt
%
% The code wraps around fas_frontend() to test that function.
%
% The input comes via a file written from OpenOffice, with graphical information about the use case activities and their flows.
%
% Based on: Lamm, J.G.: "Eine schlanke Formel für den Kern der FAS-Methode, zur einfachen Werkzeug-
% Umsetzung der Methode", in Koch, W.; Wilke, D.; Dreiseitel, S.; Kaffenberger, R. (Eds.): Tag des Systems Engineering – 
% Paderborn 16.-18. November 2022, Gesellschaft für Systems Engineering e.V. (GfSE Verlag), Bremen, Germany, 2022, pp. 127-131
% 
% English Translation of the above paper: https://github.com/GfSE/fas4sysmlv2/blob/main/doc/tech-docs/fas/FAS-as-a-formula-2022.odt	

function test_fas_frontend(cFileName,cPath)
	pkg load symbolic;
  cOldPath = getenv('PATH');
  if ~isequal(cPath,'')
    setenv('PYTHONPATH',cPath);
	  setenv('PATH',cPath);
  end
  dummy = sym('0'); %Ensure that the symbolic toolbox initialization prompt is displayed before "clc"
	clc
  disp('Computing ...');
	[clActivitiesAndObjectFlows, clFunctionalGroups,cSysMLString] = 	fas_frontend(cFileName,cPath);
  clc;
  cSysMLString=['package FunctionalModel{' sprintf('\r\n') cSysMLString];
  disp('Computing ...');
  cSysMLString = [cSysMLString RunFas(clActivitiesAndObjectFlows, clFunctionalGroups)]; %% Use fas-as-a-formula to test the obtained data 
	cSysMLString=[cSysMLString '}' sprintf('\r\n')];
  cNotebookFile=DumpJupyterNotebook(cSysMLString);
  disp('Done.');
  disp('Visualizing the result ...');
  cHtmlFile = strrep(cNotebookFile,'.ipynb','.html');
  setenv('PATH',cOldPath);
  if isunix
    cSilencer='>/dev/null 2>&1';
    system(['jupyter nbconvert --to html --execute ' cNotebookFile ' --output=' cHtmlFile ' ' cSilencer]);
    [status,output]=system(['firefox ' cHtmlFile ' ' cSilencer]);
    if status > 0
       [status,output] = system(['chrome ' cHtmlFile ' ' cSilencer]);
    end
    if status > 0
       clc;
       disp(cSysMLString)
    end
  else
    cSilencer='>nul 2>&1';
    system(['jupyter nbconvert --to html --execute ' cNotebookFile ' --output=' cHtmlFile ' ' cSilencer]);
    system(cHtmlFile);
  end
endfunction
    
    
 
function cSysMLString=RunFas(clActivitiesAndObjectFlows, clFunctionalGroups) 

    
     %%% Process Activities and Object Flows
     clLinesToParse =  clActivitiesAndObjectFlows;
     clDomainObjects = {};
     clActivities = {};
     mSymbolicMatrixO = [];
  
     for nIndex = 1:length(clLinesToParse)
        sLineToParse = clLinesToParse{nIndex};
        [clDomainObjects,clActivities,mSymbolicMatrixO] = UpdateMatrixWithFlow(clDomainObjects,clActivities,mSymbolicMatrixO, sLineToParse);
     end
     
    O = mSymbolicMatrixO;
    display(O)
    M=length(O);

    
    %%% Process Functional Groupings
     clLinesToParse =  clFunctionalGroups;  
     N = length(clLinesToParse);
     mSymbolicMatrixG = ones(N,M)*sym('0');
     clGroupName = cell(N,1);
     for n = 1:N
        sLineToParse = clLinesToParse{n};
        [sGroupName, clGroup] = parseGroupLine(sLineToParse);
        clGroupName{n,1}=sGroupName;
        for m=1:M
          if GetIndexOfStringInCellArray(clGroup,clActivities{m}) > 0
            mSymbolicMatrixG(n,m) = sym('1');
          endif
        end
     end
     G = mSymbolicMatrixG;
     display(G)
     
     %%% Compute the functional architecture via FAS-as-a-formula
     F = G*O*G';
     disp('---------------------------------');
     disp('Applying FAS-as-a-formula:')
     % Explanation of "FAS-as-a-formula": https://github.com/GfSE/fas4sysmlv2/blob/main/doc/tech-docs/fas/FAS-as-a-formula-2022.odt"
     disp('F = G*O*G''');
     disp('---------------------------------');
     display(F)
     
     %%% FAS method says that names of functional blocks are equal to names of functional groups
     clFunctionalBlockNames = clGroupName;
     
     %%% Print the functional architecture
     cSysMLString = RenderFunctionalArchitecture(F,clFunctionalBlockNames);
     
endfunction     
     
    
function cNotebookFile=DumpJupyterNotebook(cSysMLString)
  cNotebookFile = 'FunctionalModel.ipynb';
  FID1=fopen('test_visuallly.ipynb','r');
  FID2=fopen(cNotebookFile,'w');
  tline = fgetl(FID1);
  while ischar(tline)
    matches = strfind(tline, '"<Paste SysMLv2 code here>"');
    num = length(matches);
    if num > 0
      cCommaBlankAndQuotationMark=[',' sprintf('\r\n') '    "'];
      cCodedSysML=['    "' strrep(cSysMLString,sprintf('\r\n'),['\\n"' cCommaBlankAndQuotationMark])];   
      %Remove final comma, blank and quotation mark 
      cCodedSysML = cCodedSysML(1: (length(cCodedSysML)-length(cCommaBlankAndQuotationMark)));
      fprintf(FID2, [cCodedSysML sprintf('\r\n')]);
    else
      fprintf(FID2,[strrep(strrep(tline,'%','%%'),'\','\\') sprintf('\r\n')]);
    end
    tline = fgetl(FID1);  
  end
  fclose(FID1);
  fclose(FID2);
endfunction
     
     
function cSysMLstring=RenderFunctionalArchitecture(F,clFunctionalBlockNames)

    
    cSysMLstring = '';
    
    cSysMLstring = ['   part FunctionalSystem{' sprintf('\r\n')];

    
    
    clSourcePortNames = cell(length(F),length(F));
    clTargetPortNames = cell(length(F),length(F));
    for nBlock = 1: length(F)  
      cCurrentBlock = clFunctionalBlockNames{nBlock};
      cSysMLstring = [cSysMLstring '      part ' cCurrentBlock '{' sprintf('\r\n')];
        iPortNo = 0;
        for nPortOut = 1: length(F);
          if F(nBlock,nPortOut)!= sym('0') 
              sFlowName = pretty(F(nBlock,nPortOut));
              iNumPorts = max([1,length(strfind(strtrim(sFlowName), '+'))+1]);
              clPortCell = cell(1,iNumPorts);
              for nPort=1:iNumPorts
                iPortNo = iPortNo +1;
                cPortName = ['p'  num2str(iPortNo)];
                cSysMLstring = [cSysMLstring '         port ' cPortName ';' sprintf('\r\n')];
                clPortCell{1,nPort}=cPortName;
              end
              clSourcePortNames{nBlock,nPortOut}=clPortCell;
          end
        end      
        for nPortIn = 1: length(F);
          if F(nPortIn,nBlock)!= sym('0') 
              sFlowName = pretty(F(nPortIn,nBlock));
              iNumPorts = max([1,length(strfind(strtrim(sFlowName), '+'))+1]);
              clPortCell = cell(1,iNumPorts);
              for nPort=1:iNumPorts
                iPortNo = iPortNo +1;
                cPortName = ['p'  num2str(iPortNo)];
                cSysMLstring = [cSysMLstring '         port ' cPortName ';' sprintf('\r\n')];
                clPortCell{1,nPort}=cPortName;
              end
              clTargetPortNames{nPortIn,nBlock}=clPortCell;
          end
        end      
      cSysMLstring = [cSysMLstring '      }' sprintf('\r\n')];
    end
    



    
    %% Connect the blocks with flows
    cItemString = '';
    
    for nBlock1 = 1: length(F)
      for nBlock2 = 1: length(F)
          cFlow=F(nBlock1,nBlock2);
           if nBlock1 ~= nBlock2 && cFlow != sym('0') 
             sFlowName = pretty(cFlow);
              clSourcePorts = clSourcePortNames{nBlock1, nBlock2};
              clTargetPorts = clTargetPortNames{nBlock1, nBlock2};
              for nPort = 1:length(clSourcePorts)
                sCurrentFlowName = SubFlow(sFlowName,nPort);
                cSysMLstring = [cSysMLstring '      flow of ' sCurrentFlowName ' from ' clFunctionalBlockNames{nBlock1} '.' clSourcePorts{1,nPort} ' to ' clFunctionalBlockNames{nBlock2} '.' clTargetPorts{1, nPort} ';' sprintf('\r\n')];
                cItemString = [cItemString '   item def ' sCurrentFlowName ';' sprintf('\r\n')];
              end
           endif
      end
    end
    
    %% Trace Functional Blocks to Functional Groups
    for nBlock = 1: length(F)
        sCurrentName = clFunctionalBlockNames{nBlock};
        cItemString = [cItemString '   dependency from FunctionalSystem::' sCurrentName ' to UseCaseActivities::FunctionalGroups::' sCurrentName ';' sprintf('\r\n')];
    end
    
     
      
   cSysMLstring = [cSysMLstring '   }' sprintf('\r\n') cItemString ];
   


   
endfunction
    
function sCurrentFlowName = SubFlow(sFlowString,nPort)
      sCurrentFlowName = strtrim(sFlowString);
      POS = strfind(sCurrentFlowName,'+');
      if length(POS) > 0
        
        if nPort ==1
          sCurrentFlowName =strtrim(sCurrentFlowName(1:(POS(nPort)-1)));
        elseif nPort > length(POS)
          sCurrentFlowName =strtrim(sCurrentFlowName((POS(nPort-1)+1):(length(sCurrentFlowName))));
        else
          sCurrentFlowName =strtrim(sCurrentFlowName((POS(nPort-1)+1):(POS(nPort)-1)));
        end
      end
 endfunction
 
    
function [clDomainObjects,clActivities,mSymbolicMatrixO] = UpdateMatrixWithFlow(clDomainObjects,clActivities,mSymbolicMatrixO, sLineToParse)
    [sSourceObject,sFlow,sTargetObject] = parseFlowLine(sLineToParse);
     clActivities = UpdateUniqueContentCellArray (clActivities, sSourceObject);
    clActivities = UpdateUniqueContentCellArray (clActivities, sTargetObject);
    clDomainObjects = UpdateUniqueContentCellArray (clDomainObjects, sFlow);
    M = length(clActivities);
    mNewSymbolicMatrixO=ones(M,M)*sym('0');
    for nInitIndex1 = 1: M
        for nInitIndex2 = 1: M
          if nInitIndex1 <= length(mSymbolicMatrixO) && nInitIndex2 <= length(mSymbolicMatrixO)
            mNewSymbolicMatrixO(nInitIndex1,nInitIndex2) = mSymbolicMatrixO(nInitIndex1,nInitIndex2);
          endif
          if GetIndexOfStringInCellArray(clActivities,sSourceObject) == nInitIndex1 && GetIndexOfStringInCellArray(clActivities,sTargetObject) == nInitIndex2 
              mNewSymbolicMatrixO(nInitIndex1,nInitIndex2) = mNewSymbolicMatrixO(nInitIndex1,nInitIndex2) + sym(sFlow);
          end
          
        end
    end
    mSymbolicMatrixO = mNewSymbolicMatrixO;
 endfunction   
    
function   clOut=UpdateUniqueContentCellArray (clIn, sContent)
  iIndex = GetIndexOfStringInCellArray(clIn,sContent);
 
  if iIndex == 0
    iIndex1Factor = 0;
    iIndex2Factor = 0;
    if length(clIn) == size(clIn,1)
      iIndex1Factor = 1;
    else
      iIndex2Factor = 1;
    end
    clOut = cell(size(clIn,1)+iIndex1Factor,size(clIn,2)+iIndex2Factor);
    for nFill = 0:(length(clIn)-1)
        clOut{nFill*iIndex1Factor+1,nFill*iIndex2Factor+1} = clIn{nFill*iIndex1Factor+1,nFill*iIndex2Factor+1};
    end
    clOut{length(clIn)*iIndex1Factor+1,length(clIn)*iIndex2Factor+1}=sContent;
    
  else
    clOut = clIn;
  endif
endfunction
        
function iIndex = GetIndexOfStringInCellArray(clIn,sContent)
 %   iIndex = 0 if not found        
   iIndex = 0;
  for iCount = 1:length(clIn)
     if isequal(clIn{iCount},sContent)
        iIndex = iCount;
        break;
     endif
  end
endfunction 
      
function [sSourceObject,sFlow,sTargetObject] = parseFlowLine (sLine)
    
    sSourceObject ='';
    sFlow = '';
    sTargetObject = '';
    
    iCount=0;
    
    sComposedString = '';
    
    for nIndex = 1:length(sLine)
      if sLine(nIndex)==':' || sLine(nIndex)==';'
          iCount = iCount + 1;
          if iCount == 1
            sSourceObject = sComposedString;
          elseif iCount == 2
            sFlow = sComposedString;
          else
            sTargetObject = sComposedString;
          endif
          
          sComposedString = '';
      else
          if sLine(nIndex) != ' '
            sComposedString = strrep([sComposedString sLine(nIndex)],'.','_');
          endif
          
      endif
    end
    if iCount == 2
      sTargetObject = sComposedString;
    endif
endfunction

function [sGroupName, clGroup] = parseGroupLine (sLine)
    
    
    iCount=0;
    clGroup = {};
    sGroupName = '';
    
    sComposedString = '';
    
    for nIndex = 1:length(sLine)
     if sLine(nIndex)==':' || sLine(nIndex)==';'
          iCount = iCount + 1;
          if iCount == 1
              sGroupName = sComposedString;
          else
              clGroupNew = cell(length(clGroup)+1,1);
              for nFillIndex = 1:length(clGroup)
                  clGroupNew{nFillIndex,1} = clGroup{nFillIndex,1} ;
              end
              clGroupNew{length(clGroupNew),1} = sComposedString ;
            clGroup = clGroupNew;
          endif
         
          sComposedString = '';
      else
          if sLine(nIndex) != ' '
            sComposedString = strrep([sComposedString sLine(nIndex)],'.','_');
          endif
          
      endif
    end
    
    if length(sComposedString)>0
          clGroupNew = cell(length(clGroup)+1,1);
          for nFillIndex = 1:length(clGroup)
            clGroupNew{nFillIndex,1} = clGroup{nFillIndex,1} ;
          end
          clGroupNew{length(clGroupNew),1} = sComposedString ;
          clGroup = clGroupNew;
    end
  endfunction
  
