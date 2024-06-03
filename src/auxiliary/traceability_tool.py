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
    
def determine_source_base_architecture_elements(data,target_elements):
     target_base_arch_elements = []

     for currentRecord in data:
                 recordToAdd = '';
                 sIdToGet=currentRecord.get('@id')
                 sName = currentRecord.get('shortName')
                 if str(currentRecord.get('shortName')) != 'None':
                  if len(sName) > 2:
                    if sName[0:2] == 'BA':
                       if currentRecord.get('@type') == 'AttributeUsage':
                           if str(currentRecord.get('declaredName')) != 'None':
                               recordToAdd = currentRecord
                       else:
                           recordToAdd = currentRecord
                       if recordToAdd != '':
                          target_base_arch_elements.append(recordToAdd)
                            
                          if len(currentRecord.get('ownedMembership')) >0:
                            ownId = currentRecord.get('ownedMembership')[0].get('@id')
                            for currentRecord2 in data:
                                if str(currentRecord2.get('@id'))==ownId:
                                    iCount = 0
                                    for currentRecord3 in target_base_arch_elements:
                                        if currentRecord3.get('@id') == currentRecord2.get('@id'):
                                            iCount = iCount + 1
                                            break
                                    if iCount == 0 and currentRecord2.get('@type')!='FeatureValue':
                                        target_base_arch_elements.append(currentRecord2)  
     for currentRecord in target_base_arch_elements:
            if 'multiplicity' in currentRecord:               
                if str(type(currentRecord.get('multiplicity')))!="<class 'list'>":
                   if str(currentRecord.get('multiplicity'))!='None':
                        #print(currentRecord)
                        if '@id' in currentRecord.get('multiplicity'):
                            ownId = currentRecord.get('multiplicity').get('@id')
                            for currentRecord2 in data:
                                if str(currentRecord2.get('@id'))==ownId:
                                    iCount = 0
                                    for currentRecord3 in target_base_arch_elements:
                                        if currentRecord3.get('@id') == currentRecord2.get('@id'):
                                            iCount = iCount + 1
                                            break
                                    if iCount == 0:
                                        target_base_arch_elements.append(currentRecord2)       
                                    
     for currentRecord in target_base_arch_elements:
            if 'bound' in currentRecord:               
                if str(type(currentRecord.get('bound')))=="<class 'list'>":
                   if len(currentRecord.get('bound'))>0:
                        #print(currentRecord)
                        if '@id' in currentRecord.get('bound')[0]:
                            ownId = currentRecord.get('bound')[0].get('@id')
                            for currentRecord2 in data:
                                if str(currentRecord2.get('@id'))==ownId:
                                    iCount = 0
                                    for currentRecord3 in target_base_arch_elements:
                                        if currentRecord3.get('@id') == currentRecord2.get('@id'):
                                            iCount = iCount + 1
                                            break
                                    if iCount == 0 and currentRecord2.get('@type')!='Redefinition' and currentRecord2.get('@type')!='FeatureValue':
                                        target_base_arch_elements.append(currentRecord2)       
                                    
     for currentRecord in target_base_arch_elements:
            if 'ownedRelationship' in currentRecord:               
                if str(type(currentRecord.get('ownedRelationship')))=="<class 'list'>":
                    #print('list')
                    for r in currentRecord.get('ownedRelationship'):
                        #print(currentReownedRelationshipownedRelationshipcord)
                        if '@id' in r:
                            ownId = r.get('@id')
                            for currentRecord2 in data:
                                if str(currentRecord2.get('@id'))==ownId:
                                    iCount = 0
                                    for currentRecord3 in target_base_arch_elements:
                                        if currentRecord3.get('@id') == currentRecord2.get('@id'):
                                            iCount = iCount + 1
                                            break
                                    if iCount == 0 and currentRecord2.get('@type')!='Redefinition' and currentRecord2.get('@type')!='FeatureValue':
                                        target_base_arch_elements.append(currentRecord2)       
                                    
     for currentRecord in target_base_arch_elements:
            if 'feature' in currentRecord:               
                
                if str(type(currentRecord.get('feature')))=="<class 'list'>":
                        if len(currentRecord.get('feature'))>0:
                           for f in currentRecord.get('feature'):
                            ownId = f.get('@id')
                            for currentRecord2 in data:
                                if str(currentRecord2.get('@id'))==ownId:
                                    iCount = 0
                                    for currentRecord3 in target_base_arch_elements:
                                        if currentRecord3.get('@id') == currentRecord2.get('@id'):
                                            iCount = iCount + 1
                                            break
                                    if iCount == 0 and currentRecord2.get('@type')!='Redefinition' and currentRecord2.get('@type')!='FeatureValue':
                                        if currentRecord2.get('@type')!='ItemUsage':
                                            target_base_arch_elements.append(currentRecord2) 
                                        else:
                                            for t in target_elements:
                                                if 'declaredName' in t:
                                                     if str(t.get('declaredName'))!='None' and str(currentRecord2.get('declaredName'))!='None':
                                                        if t.get('declaredName') == currentRecord2.get('declaredName'):
                                                             target_base_arch_elements.append(currentRecord2) 
                                                                          
                else:
                   if str(currentRecord.get('feature'))!='None':
                        #print(currentRecord)
                        if '@id' in currentRecord.get('feature'):
                            ownId = currentRecord.get('feature').get('@id')
                            for currentRecord2 in data:
                                if str(currentRecord2.get('@id'))==ownId:
                                    iCount = 0
                                    for currentRecord3 in target_base_arch_elements:
                                        if currentRecord3.get('@id') == currentRecord2.get('@id'):
                                            iCount = iCount + 1
                                            break
                                    if iCount == 0 and currentRecord2.get('@type')!='Redefinition' and currentRecord2.get('@type')!='FeatureValue':
                                        target_base_arch_elements.append(currentRecord2)       

     target_base_arch_elements_old = target_base_arch_elements                              
     target_base_arch_elements = []
     bPartDefinitionFound = False
     for currentRecord in target_base_arch_elements_old:
            if currentRecord.get('@type')=='PartDefinition':
                continue
            if currentRecord.get('@type')=='ItemUsage':
                if str(currentRecord.get('declaredName'))=='None':
                   continue
            if currentRecord.get('@type')=='AttributeUsage':
                 sName = currentRecord.get('shortName')
                 if str(currentRecord.get('shortName')) == 'None':
                     continue
                 if len(sName) <2:
                     continue
                 if sName[0:2] != 'BA':
                   continue
            target_base_arch_elements.append(currentRecord)
            if 'owner' in currentRecord:               
                if str(type(currentRecord.get('owner')))!="<class 'list'>":
                   if str(currentRecord.get('owner'))!='None':
                        #print(currentRecord)
                        if '@id' in currentRecord.get('owner'):
                            ownId = currentRecord.get('owner').get('@id')
                            for currentRecord2 in data:
                                if str(currentRecord2.get('@id'))==ownId:
                                    iCount = 0
                                    #print('Owner: ')
                                    #print(currentRecord2)
                                    #for currentRecord3 in target_base_arch_elements:
                                    #    if currentRecord3.get('@id') == currentRecord2.get('@id'):
                                    #        iCount = iCount + 1
                                    #        break
                                    #print( currentRecord2.get('@type'))
                                    if iCount == 0 and currentRecord2.get('@type')=='PartDefinition':
                                       if bPartDefinitionFound == False and str(currentRecord2.get('shortName'))!='None':
                                          if len(currentRecord2.get('shortName'))>1:
                                                sName = currentRecord2.get('shortName')
                                                if sName[0:2] == 'BA':
                                                    bPartDefinitionFound = True
                                                    target_base_arch_elements.append(currentRecord2)       
                                        
                                        
                                       
                                       # Package does not exist when not explicitly publishing the base architecture, it seems 
                                       #packageRecord = currentRecord2.get('owningNamespace')
                                       #if str(packageRecord)!='None':  
                                       #     packageId = packageRecord.get('@id')
                                       #     #print(packageId)
                                       #     for currentRecord4 in data:
                                       #         if currentRecord4.get('@id')==packageId:
                                       #            owningM = currentRecord4.get('owningMembership').get('@id')
                                       #            target_base_arch_elements.append(currentRecord4)  
                                       #            for currentRecord5 in data:
                                       #                 if currentRecord5.get('@id')==owningM:
                                       #                    target_base_arch_elements.append(currentRecord5)  
                                                   
                                    

     for currentRecord in target_base_arch_elements:
            if 'definition' in currentRecord:     
                #print(currentRecord)
                #print(str(type(currentRecord.get('definition'))))
                if str(type(currentRecord.get('definition')))=="<class 'list'>":
                   if len(currentRecord.get('definition'))>0:
                        #print(currentRecord)
                        if '@id' in currentRecord.get('definition')[0]:
                            ownId = currentRecord.get('definition')[0].get('@id')
                            for currentRecord2 in data:
                                if str(currentRecord2.get('@id'))==ownId:
                                    iCount = 0
                                    for currentRecord3 in target_base_arch_elements:
                                        if currentRecord3.get('@id') == currentRecord2.get('@id'):
                                            iCount = iCount + 1
                                            break
                                    if iCount == 0 and currentRecord2.get('@type')!='Redefinition' and currentRecord2.get('@type')!='FeatureValue':
                                        target_base_arch_elements.append(currentRecord2)       

     if True:
        TypeList = []
        for r in target_base_arch_elements:
            TypeList.append(r.get('@type'))
            print(r.get('@id'))
        TypeList.sort()
        for t in TypeList:
            print(t)     
     return target_base_arch_elements

def copy_and_trace_elements(source_host, source_id, target_host, target_id, cTraceabilityPackageName):
    rep_t = []

    rep_source = read_full_repository(source_host, source_id)

    rep_target = read_full_repository(target_host, target_id)
     
    target_base_arch_elements = [] 
    # Find Base Architecture elements in the target repository     
    for i in range(len(rep_target)):
        currentRecord = rep_target[i]
        if str(currentRecord.get('shortName')) != 'None':
          sName = currentRecord.get('shortName')
          if len(sName) > 1:
            if sName[0:2] == 'BA':     
               target_base_arch_elements.append(currentRecord)            

    
    source_base_arch_elements = determine_source_base_architecture_elements(rep_source,target_base_arch_elements)
       
    baSourceIds = []       
    print('Source Base architecture elements:')
    for el in source_base_arch_elements:
       baSourceIds.append(el.get('@id'))       

       print (el)
       print('---------------')
       
       
    print('Target Base architecture elements:')
    for el in target_base_arch_elements:
       print (el)
       print('---------------')
       
    basearch_corresponding_ids_source = [];  
    basearch_corresponding_ids_target = [];  
    print('ANALYZING OBJECTS THAT DEPEND ON BASE ARCHITECTURE')   
    for source_el in rep_source:
       for baseArchId in baSourceIds:
            if baseArchId in basearch_corresponding_ids_source:
                continue
            if baseArchId in json.dumps(source_el):
                print (source_el.get('@type') + ' (' + source_el.get('@id') +')') 
                print('depends on ' + baseArchId) 
                for el in source_base_arch_elements:
                    if el.get('@id') == baseArchId:
                       baseArchType = el.get('@type');
                       print ('  = ' + el.get('@type') + ' (' + el.get('@id') +')') 
                       bNameAvailable = False
                       if 'name' in el:
                           if str(el.get('name'))!='None':
                               print('     BaseArch Name: ' + el.get('name'))
                               bNameAvailable = True
                               for te in target_base_arch_elements:
                                   if str(te.get('name'))!='None':
                                       if el.get('name') == te.get('name'):
                                           basearch_corresponding_ids_source.append(baseArchId)
                                           basearch_corresponding_ids_target.append(te.get('@id'))
                                           print('==> Mapping source:' + baseArchType + ' ('+ baseArchId + ') to target:' + te.get('@type') + ' (' + te.get('@id') +' )')
                       if bNameAvailable==False:
                           if el.get('@type')=='OwningMembership':
                                OwningId = el.get('owningRelatedElement').get('@id')
                                print ('  => owningRelatedElement: ' + OwningId)
                                for el2 in source_base_arch_elements:
                                    if el2.get('@id') == OwningId:
                                       print ('  => owningRelatedElement ' + el2.get('@type') + ' (' + el2.get('@id') +')') 
                                       if 'name' in el2:
                                           if str(el2.get('name'))!='None':
                                               print('     BaseArch Name of owningRelatedElement: ' + el2.get('name'))
                                               bNameAvailable = True
                                               bMapped = False
                                               for te in target_base_arch_elements:
                                                   
                                                   if te.get('@type')=='OwningMembership':
                                                     for te2 in target_base_arch_elements:
                                                         if te2.get('@id')==te.get('owningRelatedElement').get('@id'):
                                                             if str(te2.get('name')) != 'None':
                                                                 teOwningName = te2.get('name')
                                                                 print('Name: '+ el2.get('name') + ' vs. OwningName: ' + teOwningName)
                                                                 if el2.get('name') == teOwningName:
                                                                     basearch_corresponding_ids_source.append(baseArchId)
                                                                     basearch_corresponding_ids_target.append(te.get('@id'))
                                                                     print('==> Mapping source:' + baseArchType + ' ('+ baseArchId + ') to target:' + te.get('@type') + ' (' + te.get('@id') +' )')
                                                                     bMapped = True
                                               if bMapped == False:
                                                   print(ErrorMappingFailed)

                                           else:
                                               if el2.get('@type')=='AttributeDefinition' or  el2.get('@type')=='AttributeUsage' or  el2.get('@type')=='Feature' or  el2.get('@type')=='ItemDefinition' or  el2.get('@type')=='LiteralInteger' or el2.get('@type')=='Multiplicity' or el2.get('@type')=='MultiplicityRange' or el2.get('@type')=='Package' or el2.get('@type')=='PartDefinition' or el2.get('@type')=='ReturnParameterMembership' or el2.get('@type')=='Subsetting':
                                                   print('     BaseArch Name of owningRelatedElement not needed, because type is unique')
                                                   bMapped = False
                                                   for te in target_base_arch_elements:
                                                   
                                                     if te.get('@type')=='OwningMembership':
                                                        for te2 in target_base_arch_elements:
                                                           if te2.get('@id')==te.get('owningRelatedElement').get('@id'):
                                                                 teOwningType = te2.get('@type')
                                                                 print('Type: '+ el2.get('@type') + ' vs. OwningName: ' + teOwningType)
                                                                 if el2.get('@type') == teOwningType:
                                                                     basearch_corresponding_ids_source.append(baseArchId)
                                                                     basearch_corresponding_ids_target.append(te.get('@id'))
                                                                     print('==> Mapping source:' + baseArchType + ' ('+ baseArchId + ') to target:' + te.get('@type') + ' (' + te.get('@id') +' )')
                                                                     bMapped = True
                                               if bMapped == False:
                                                   print(ErrorMappingFailed)
                                                   

                       if bNameAvailable==False:
                           if el.get('@type')=='FeatureMembership':
                                OwningId = el.get('ownedRelatedElement')[0].get('@id')
                                print ('  => ownedRelatedElement: ' + OwningId)
                                for el2 in source_base_arch_elements:
                                    if el2.get('@id') == OwningId:
                                       print ('  => ownedRelatedElement ' + el2.get('@type') + ' (' + el2.get('@id') +')') 
                                       if 'name' in el2:
                                           if str(el2.get('name'))!='None':
                                               print('     BaseArch Name of ownedRelatedElement: ' + el2.get('name'))
                                               bNameAvailable = True
                                               bMapped = False
                                               for te in target_base_arch_elements:
                                                   
                                                   if te.get('@type')=='FeatureMembership':
                                                     for te2 in target_base_arch_elements:
                                                         if te2.get('@id')==te.get('ownedRelatedElement')[0].get('@id'):
                                                             if str(te2.get('name')) != 'None':
                                                                 teOwningName = te2.get('name')
                                                                 print('Name: '+ el2.get('name') + ' vs. OwningName: ' + teOwningName)
                                                                 if el2.get('name') == teOwningName:
                                                                     basearch_corresponding_ids_source.append(baseArchId)
                                                                     basearch_corresponding_ids_target.append(te.get('@id'))
                                                                     print('==> Mapping source:' + baseArchType + ' ('+ baseArchId + ') to target:' + te.get('@type') + ' (' + te.get('@id') +' )')
                                                                     bMapped = True
                                               if bMapped == False:
                                                   print(ErrorMappingFailed)
                                           else:
                                               if el2.get('@type')=='AttributeDefinition' or  el2.get('@type')=='AttributeUsage' or  el2.get('@type')=='Feature' or  el2.get('@type')=='ItemDefinition' or  el2.get('@type')=='LiteralInteger' or el2.get('@type')=='Multiplicity' or el2.get('@type')=='MultiplicityRange' or el2.get('@type')=='Package' or el2.get('@type')=='PartDefinition' or el2.get('@type')=='ReturnParameterMembership' or el2.get('@type')=='Subsetting':
                                                   print('     BaseArch Name of ownedRelatedElement not needed, because type is unique')
                                                   
                                                   bMapped = False
                                                   for te in target_base_arch_elements:
                                                   
                                                     if te.get('@type')=='FeatureMembership':
                                                        for te2 in target_base_arch_elements:
                                                           if te2.get('@id')==te.get('ownedRelatedElement')[0].get('@id'):
                                                                 teOwningType = te2.get('@type')
                                                                 print('Type: '+ el2.get('@type') + ' vs. OwningName: ' + teOwningType)
                                                                 if el2.get('@type') == teOwningType:
                                                                     basearch_corresponding_ids_source.append(baseArchId)
                                                                     basearch_corresponding_ids_target.append(te.get('@id'))
                                                                     print('==> Mapping source:' + baseArchType + ' ('+ baseArchId + ') to target:' + te.get('@type') + ' (' + te.get('@id') +' )')
                                                                     bMapped = True
                                               if bMapped == False:
                                                   print(ErrorMappingFailed)

                                                   

                       if bNameAvailable==False:
                           if el.get('@type')=='AttributeDefinition' or  el.get('@type')=='AttributeUsage' or  el.get('@type')=='Feature' or  el.get('@type')=='ItemDefinition' or  el.get('@type')=='LiteralInteger' or el.get('@type')=='Multiplicity' or el.get('@type')=='MultiplicityRange' or el.get('@type')=='Package' or el.get('@type')=='PartDefinition' or el.get('@type')=='ReturnParameterMembership' or el.get('@type')=='Subsetting':
                                               print('     BaseArch Name not needed because type is unique')
                                               for te in target_base_arch_elements:
                                                       if el.get('@type') == te.get('@type'):
                                                           basearch_corresponding_ids_source.append(baseArchId)
                                                           basearch_corresponding_ids_target.append(te.get('@id'))
                                                           print('==> Mapping source:' + baseArchType + ' ('+ baseArchId + ') to target:' + te.get('@type') + ' (' + te.get('@id') +' )')
                                               
                                               
                                               
                                               
                       if bNameAvailable==False:
                           if el.get('@type')=='FeatureTyping':
                                TypedId = el.get('typedFeature').get('@id')
                                print ('  => typedFeature: ' + TypedId)
                                for el2 in source_base_arch_elements:
                                    if el2.get('@id') == TypedId:
                                       print ('  => typedFeature ' + el2.get('@type') + ' (' + el2.get('@id') +')') 
                                       if 'name' in el2:
                                           if str(el2.get('name'))!='None':
                                               print('     BaseArch Name of typedFeature: ' + el2.get('name'))
                                               bNameAvailable = True
                                               for te in target_base_arch_elements:
                                                       if te.get('@type')=='FeatureTyping':
                                                           targetTypedId = te.get('typedFeature').get('@id')
                                                           for te2 in target_base_arch_elements:
                                                               if te2.get('@id')==targetTypedId:
                                                                   if 'name' in te2:
                                                                       if str(te2.get('name'))!='None':
                                                                           if te2.get('name')==el2.get('name'):                                                                   
                                                                               basearch_corresponding_ids_source.append(baseArchId)
                                                                               basearch_corresponding_ids_target.append(te.get('@id'))
                                                                               print('==> Mapping source:' + baseArchType + ' ('+ baseArchId + ') to target:' + te.get('@type') + ' (' + te.get('@id') +' )')
                         

                                
                print('======================================================')
            
    

       
    for i in range(len(rep_source)):
        if rep_source[i].get('@id') in basearch_corresponding_ids_source:
            print('SKIPPING ' + rep_source[i].get('@type') + ' (' + rep_source[i].get('@id') + '), because it is in the base architecture.')
            continue
            #Skip writing base architecture, because base architecture is already in the repository.
            #Instead, we need to redirect references to base architecture objects to corresponding existing objects in the repository.
            
        rep_source_as_string=json.dumps(rep_source[i])
        for mapIdIndex in range(len(basearch_corresponding_ids_source)):
            sourceIdToFind = basearch_corresponding_ids_source[mapIdIndex]
            targetIdSubstituting = basearch_corresponding_ids_target[mapIdIndex]       
            rep_source_as_string_new=rep_source_as_string.replace(sourceIdToFind, targetIdSubstituting)
            if rep_source_as_string_new!= rep_source_as_string:
                print('IN ' + rep_source[i].get('@type') + ' (' + rep_source[i].get('@id') +') - REPLACED ' + sourceIdToFind + ' WITH ' +   targetIdSubstituting)  
                
            rep_source_as_string=rep_source_as_string_new
            
        rep_source[i]=json.loads(rep_source_as_string)
                         
            
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
