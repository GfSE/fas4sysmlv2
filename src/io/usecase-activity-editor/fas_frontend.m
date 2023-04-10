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


% This is code for GNU Octave 
%
% The code in this file has been translated into python: fas_frontend.py
% It is still in use for "test_" functions. 
% This file will be removed, once the "test_" functions are translated to python. 
%
% The input comes via a file written from OpenOffice, with graphical information about the use case activities and their flows.

function [clActivitiesAndObjectFlows, clFunctionalGroups, cSysMLString] = fas_frontend(cFileName,cPath)
	[clActivitiesAndObjectFlows, clFunctionalGroups] = 	ParseActivityModel(cFileName);
	cSysMLString = ProcessFasCards(clActivitiesAndObjectFlows, clFunctionalGroups); 
  disp(cSysMLString);
endfunction
        
function cSysMLString = ProcessFasCards(clActivitiesAndObjectFlows, clFunctionalGroups) 
     %%% Process Activities and Object Flows
     cSysMLString='';
     cLF = sprintf('\r\n');
     clLinesToParse =  clActivitiesAndObjectFlows;
     clDomainObjects = {};
     clActivities = {};
     mMatrixO = [];
  
     for nIndex = 1:length(clLinesToParse)
        sLineToParse = clLinesToParse{nIndex};
        [clDomainObjects,clActivities,mMatrixO] = UpdateMatrixWithFlow(clDomainObjects,clActivities,mMatrixO, sLineToParse);
     end
    
     %%% Process Functional Groupings
     clLinesToParse =  clFunctionalGroups;  
     N=length(clLinesToParse);
     M=length(mMatrixO);
     mMatrixG = zeros(N,M);

     clGroupName = cell(N,1);
     for n = 1:N
        sLineToParse = clLinesToParse{n};
        [sGroupName, clGroup] = parseGroupLine(sLineToParse);
        clGroupName{n,1}=sGroupName;
        for m=1:M
          if GetIndexOfStringInCellArray(clGroup,clActivities{m}) > 0
            mMatrixG(n,m) = 1;
          endif
        end
     end
      
     cSysMLString=[cSysMLString '   package UseCaseActivities{' cLF];
     cSysMLString = [cSysMLString RenderActivityDefinitionsInSysML(mMatrixO, clActivities)];
     cSysMLString = [cSysMLString RenderFlowsInSysML(mMatrixO, clActivities)];
     cSysMLString = [cSysMLString '      package FunctionalGroups{' cLF];
     cSysMLString = [cSysMLString RenderFunctionalGroupsInSysML(clGroupName ,clActivities, mMatrixG)];
     cSysMLString=[cSysMLString '      }' cLF];
     cSysMLString=[cSysMLString '   }' cLF];
endfunction

function cSysMLString=RenderFunctionalGroupsInSysML(clGroupName,clActivities, mMatrixG);
     cSysMLString='';
     cLF = sprintf('\r\n');
     N=size(mMatrixG,1);
     M=size(mMatrixG,2);
     for n = 1:N
        cSysMLString=[cSysMLString '         package ' clGroupName{n} '{' cLF];
        for m=1:M
          if mMatrixG(n,m) > 0
            cSysMLString=[cSysMLString '            import ' clActivities{m} ';' cLF];
          endif
        end
        cSysMLString=[cSysMLString '         }' cLF];

     end
endfunction

function cSysMLString=RenderActivityDefinitionsInSysML(O,clActivities)
     cSysMLString='';
     cLF = sprintf('\r\n');

    for nText = 1:length(clActivities)      
      cSysMLString=[cSysMLString '      action def ' clActivities{nText} ' {' cLF];
      for nIn=1:length(clActivities)
          if ~isequal(O{nIn,nText},'')
               sFlowString=strtrim(O{nIn,nText});
               for nParam = 1:(length(strfind(sFlowString,'+'))+1)
                 sCurrentFlowName = SubFlow(sFlowString,nParam);
                 sInput = sCurrentFlowName;
                 cSysMLString=[cSysMLString '         in ' sInput ';' cLF];
               end
          endif
      end
      for nOut=1:length(clActivities)
          if ~isequal(O{nText,nOut}, '')
               sFlowString=strtrim(O{nText,nOut});
               for nParam = 1:(length(strfind(sFlowString,'+'))+1)
                 sCurrentFlowName = SubFlow(sFlowString,nParam);
                 sOutput = sCurrentFlowName; 
                 cSysMLString = [cSysMLString '         out ' sOutput ';' cLF];
               end
          endif
      end
      cSysMLString=[cSysMLString '      }' cLF];
    end
endfunction
   
function cSysMLString=RenderFlowsInSysML(O,clActivities) 
    cSysMLString='';
    cLF = sprintf('\r\n');
     
    clOutput =cell(length(clActivities)*length(clActivities)*3+10,1);
    cSysMLString=[cSysMLString '      action def OverallUseCase {' cLF];
    
    for nText = 1:length(clActivities)      
      cSysMLString=[cSysMLString '         action a' num2str(nText) ':' clActivities{nText} ';' cLF];
    end
  
    for n1=1:length(clActivities) 
      for n2=1:length(clActivities)
          if ~isequal(O{n1,n2},'')
               sFlowString=strtrim(O{n1,n2});
               for nParam = 1:(length(strfind(sFlowString,'+'))+1)
                 sInput = SubFlow(sFlowString,nParam);
                 sResult = sInput;
                 cSysMLString=[cSysMLString '         flow from a' num2str(n1) '.' sResult ' to a'  num2str(n2) '.' sInput ';' cLF];
               end
          endif
      end
    end  

    cSysMLString=[cSysMLString '      }' cLF];
    
endfunction

function [clDomainObjects,clActivities,mMatrixO] = UpdateMatrixWithFlow(clDomainObjects,clActivities,mMatrixO, sLineToParse)
    [sSourceObject,sFlow,sTargetObject] = parseFlowLine(sLineToParse);
     clActivities = UpdateUniqueContentCellArray (clActivities, sSourceObject);
    clActivities = UpdateUniqueContentCellArray (clActivities, sTargetObject);
    clDomainObjects = UpdateUniqueContentCellArray (clDomainObjects, sFlow);
    M = length(clActivities);
    mNewMatrixO=cell(M,M);
    for n1 = 1:M
        for n2=1:M
            mNewMatrixO{n1,n2}='';
        end
    end
    for nInitIndex1 = 1: M
        for nInitIndex2 = 1: M
          if nInitIndex1 <= length(mMatrixO) && nInitIndex2 <= length(mMatrixO)
            mNewMatrixO{nInitIndex1,nInitIndex2} = mMatrixO{nInitIndex1,nInitIndex2};
          endif
          if GetIndexOfStringInCellArray(clActivities,sSourceObject) == nInitIndex1 && GetIndexOfStringInCellArray(clActivities,sTargetObject) == nInitIndex2 
			  if isequal (mNewMatrixO{nInitIndex1,nInitIndex2},'')
				mNewMatrixO{nInitIndex1,nInitIndex2} =  [sFlow];
			  else
				mNewMatrixO{nInitIndex1,nInitIndex2} =  [mNewMatrixO{nInitIndex1,nInitIndex2} ' + ' sFlow];
			  end
          end
          
        end
    end
    mMatrixO = mNewMatrixO;
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
  
 


function [clActivitiesAndObjectFlows, clFunctionalGroups] = ParseActivityModel (cFileName)
    [clGroupNames, clGroupPositionVectors clActivityNames, clActivityPositionVectors,clConnectorNames,clConnectorPositionVectors]= ParseopenOfficeExportFile(cFileName);
    rTolerancePixels = 50;
    clActivitiesAndObjectFlows = CreateActivitiesAndObjectFlows(clActivityNames, clActivityPositionVectors,clConnectorNames,clConnectorPositionVectors, rTolerancePixels);
    clFunctionalGroups = CreateFunctionalGroups(clActivityNames, clActivityPositionVectors, clGroupNames,  clGroupPositionVectors);
endfunction  
    
function clFunctionalGroups = CreateFunctionalGroups(clActivityNames, clActivityPositionVectors, clGroupNames,  clGroupPositionVectors)
       clFunctionalGroups = {};
       for nGroup = 1:length(clGroupPositionVectors)
         vGrp = clGroupPositionVectors{1,nGroup};
         cGroupingString = [clGroupNames{1,nGroup} ];
         for nActivity = 1:length(clActivityPositionVectors)
           vAct = clActivityPositionVectors{1,nActivity};
           if vAct(1) > vGrp(1) && vAct(2)> vGrp(2) && vAct(3) < vGrp(3) && vAct(4)<vGrp(4)
             cGroupingString = [cGroupingString ':' clActivityNames{1,nActivity}];
           end
         end
         clFunctionalGroups = My_GrowCellArray(clFunctionalGroups, cGroupingString);
       end  
endfunction
 
function clActivitiesAndObjectFlows = CreateActivitiesAndObjectFlows(clActivityNames, clActivityPositionVectors,clConnectorNames,clConnectorPositionVectors,rTolerancePixels)
       clActivitiesAndObjectFlows = {};
       for nActivity = 1:length(clActivityPositionVectors)
         vActPositions = clActivityPositionVectors{1,nActivity};
         for nConnector = 1:length(clConnectorPositionVectors)
           vConnPositions = clConnectorPositionVectors{1,nConnector};
           if isConnected (vConnPositions(1:2), vActPositions, rTolerancePixels)
              for nActivity2= 1:length(clActivityPositionVectors)
                if isConnected (vConnPositions(3:4), clActivityPositionVectors{1,nActivity2}, rTolerancePixels)
                  clActivitiesAndObjectFlows = My_GrowCellArray(clActivitiesAndObjectFlows,[clActivityNames{1,nActivity} ':' clConnectorNames{1,nConnector} ':' clActivityNames{1,nActivity2} ]);
                end
              end
           end
         end
       end
endfunction
       
       
function bret = isConnected (vConnectorXY, vActivityPositions, rTolerancePixels)
      bret = false;
            
      if vConnectorXY(1) > vActivityPositions(1) - rTolerancePixels && vConnectorXY(1) < vActivityPositions(3) + rTolerancePixels
        % Top line of activity rectangle
        if vConnectorXY(2) > vActivityPositions(2) - rTolerancePixels && vConnectorXY(2) < vActivityPositions(2) + rTolerancePixels
          bret = true;
        end
        % Bottom line of activity rectangle
        if vConnectorXY(2) > vActivityPositions(4) - rTolerancePixels && vConnectorXY(2) < vActivityPositions(4) + rTolerancePixels
          bret = true;
        end
      end
      if vConnectorXY(2) > vActivityPositions(2) - rTolerancePixels && vConnectorXY(2) < vActivityPositions(4) + rTolerancePixels
        % Left line of activity rectangle
        if vConnectorXY(1) > vActivityPositions(1) - rTolerancePixels && vConnectorXY(1) < vActivityPositions(1) + rTolerancePixels
          bret = true;
        end
        % Right line of activity rectangle
        if vConnectorXY(1) > vActivityPositions(3) - rTolerancePixels && vConnectorXY(1) < vActivityPositions(3) + rTolerancePixels
          bret = true;
        end
      end
endfunction

function [clGroupNames, clGroupPositionVectors clActivityNames, clActivityPositionVectors,clConnectorNames,clConnectorPositionVectors]= ParseopenOfficeExportFile(cFileName)
      FID1 = fopen(cFileName,'r');
      if FID1
        %FID OK
      else
        error(['File not found: ' cFileName]);
      end
      clGroupNames={}; 
      clGroupPositionVectors={};
      clActivityNames={}; 
      clActivityPositionVectors={};
      clConnectorNames={};
      clConnectorPositionVectors={};
      sLine = fgets(FID1);
      iLine = 1;
      try
         while sLine ~= -1
            sLine=strtrim(sLine);
            if isequal(sLine, 'Group')
              sName = Readname(FID1);
              iLine = iLine + 1;
              vPositionsXY = ReadPositions(FID1,4);
              iLine = iLine + 4;
              clGroupNames =  My_GrowCellArray(clGroupNames, sName);
              clGroupPositionVectors =  My_GrowCellArray(clGroupPositionVectors, vPositionsXY);            
            elseif isequal(sLine, 'Element')
              sName = Readname(FID1);
              iLine = iLine + 1;
              vPositionsXY = ReadPositions(FID1,4);
              iLine = iLine + 4;
              clActivityNames =  My_GrowCellArray(clActivityNames, sName);
              clActivityPositionVectors =  My_GrowCellArray(clActivityPositionVectors, vPositionsXY);
            elseif isequal(sLine, 'Connector')
              vStartPositionXY = ReadPositions(FID1,2);
              vEndPositionXY = ReadPositions(FID1,2);
              iLine = iLine + 4;
              sName = Readname(FID1);
              iLine = iLine + 1;
              vPositionsXY = ReadPositions(FID1,4);
              iLine = iLine + 4;
              clConnectorNames =  My_GrowCellArray(clConnectorNames, sName);
              clConnectorPositionVectors =  My_GrowCellArray(clConnectorPositionVectors, [vStartPositionXY, vEndPositionXY]);
            else 
              error(['Not expected in Line ' num2str(iLine) ': ' sLine]);
              sLine = fgets(FID1);
              iLine = iLine + 1;
            end
            sLine = fgets(FID1);
         end
      catch(theError)
         fclose(FID1);
         error(lasterr);
      end
      fclose(FID1);
endfunction      
      
function vPositionsXY = ReadPositions(FID,numpos)
      
      vPositionsXY=ones(1,numpos)*NaN; %[x1,y1,x2,y2]
      n= 1;
      while n<=numpos
        sLine = fgets(FID);
        if sLine == -1
          error('File Reading stopped in the middle of a chunk');
        endif
        if length(strtrim(sLine)) == 0
          n=n-1;
        else  
          try
          vPositionsXY(n) = str2num(sLine);
          catch (theError)
            disp('err')
          end
          if n>2
            vPositionsXY(n) = vPositionsXY(n) + vPositionsXY(n-2);
          endif
        endif
        n=n+1;
      end
endfunction
      
function sName = Readname(FID)
      sName = '';
      while length(sName)==0
        sName='';
        sLine = fgets(FID);
        if sLine == -1
          error('File Reading stopped in the middle of a chunk');
        endif
        sName = strtrim(sLine);
      end
endfunction
        
function clNew = My_GrowCellArray(clOld, newEntry)
  clNew = cell(1,length(clOld)+1);
  for nCopy = 1:length(clOld)
    clNew{1,nCopy}=clOld{1,nCopy};
  end
  clNew{1,length(clNew)}=newEntry;
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
