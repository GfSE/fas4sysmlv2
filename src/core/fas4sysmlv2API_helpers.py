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
#   This is an include file of the FAS plugin for SysML v2 for helping with the handling of the SysML v2 REST API.
#

import requests
import json
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from functools import partial


def format_servername(cName):
     if len(cName)>0:
         if cName[len(cName)-1] == '/':
            cName = cName[0:(len(cName)-1)]
         
         if cName.find('http') == -1:
            cName = 'http://' + cName
     
     return cName
  
def delete_project(cServerName, cProjectID):
##Deletion does not work for non-empty projects, so we will just set the name to None in that case
     bSuccess = True
     response = requests.delete(cServerName + "/projects/" + cProjectID)
     if response.status_code!=200:
   
         response = requests.get(cServerName + '/projects/' + cProjectID)
         if response.status_code!=200: 
             bSuccess = False
         else:
             default_branch_id = response.json().get('defaultBranch').get('@id')
             project_data = {
                      "@type": "Project",
                      "defaultBranch":{"@id": default_branch_id},
	                  "name": None}

             response = requests.put(cServerName + "/projects/"+cProjectID, 
                                      headers={"Content-Type": "application/json"}, 
                                      data=json.dumps(project_data))
                                      
             if response.status_code!=200: 
                 bSuccess = false

     return bSuccess


def multi_page_http_get (sUrl):
     # Processes pagination in htttp responses and returns the full data from all 
     # pages and the response from getting the last page
     response = requests.get(sUrl)
     data = response.json()

         # Handle next pages of mutlti-page HTML responses (when the payload is very large)
     while response.headers.get('Link','--NOTFOUND--').find('?page[after]')>-1:
         cLink = response.headers.get('Link')
         iPos = cLink.find(',')
         if iPos > -1:
              cLink = cLink[0:iPos]
         cNextPageLink = cLink.replace('<','').replace('; rel="next"','').replace('; rel="prev"','').replace('>','')
         response = requests.get(cNextPageLink)
         if response.status_code == 200:
             data = data + response.json()
         else:
             break
             
     return response, data


def read_full_repository(cServerName, cProjectID):
# This function has been created to demonstrate the handling
# of multiple HTML response pages.
#
# Normally, this function should not be used, but queries 
# for subsets of the repository should be used instead.
     bSuccess = True
     data = []
     try:
         response = requests.get(cServerName + "/projects/" + cProjectID)
     except  requests.exceptions.ConnectionError:
         bSuccess = False
         cErrorMessage = 'Error: Could not connect to server'
         print(cErrorMessage)

         
     if bSuccess and response.status_code!=200:
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


     data = []
     if bSuccess:
         response, data = multi_page_http_get(cServerName + "/projects/" + cProjectID + "/commits/"+sHeadCommit+"/elements")

     return data

def run_query_for_elementtyp(cElementType, cServerName, cProjectID):
    qresponse_json=json.dumps('')
    qinput = {
      '@type':'Query',
      'select': ['name','@id','@type','owner'],
      'where': {
        '@type': 'CompositeConstraint',
        'operator': 'and',
        'constraint': [
            {
                '@type': 'PrimitiveConstraint',
                'inverse': False,
                'operator': '=',
                'property': '@type',
                'value': cElementType
            }
        ]
      }
    }

    payload = json.dumps(qinput)
    qurl = f"{cServerName}/projects/{cProjectID}/query-results"
    qresponse = requests.post(qurl, json=qinput)
    if qresponse.status_code == 200:
        qresponse_json = qresponse.json()

    return qresponse_json
  
def processProjectSelection(listWindow,theCombo,cProjectID):
     selectedProject = theCombo.get()
     posOpeningParenthesis = selectedProject.find('(')
     posClosingParenthesis = selectedProject.find(')')
     cProjectID.set(selectedProject[(posOpeningParenthesis+1):posClosingParenthesis])
     listWindow.destroy()

    
def selectproject(cProjectID, cServerName):
     tdata = []
     cProjectID.set("")
     cProjectID.set("")
     try:
         response, data = multi_page_http_get(format_servername(cServerName.get()) + "/projects")

         for currentRecord in data:
             if str(currentRecord.get('name'))!="None":
	             tdata.append(currentRecord.get("name") + " (" + currentRecord.get("@id") + ")" )
     except  requests.exceptions.ConnectionError:
         cProjectID.set("Cannot connect to server.")
     
     if len(tdata)>0:
         listWindow = Tk()
         listWindow.title("Project Selection")
         frm = ttk.Frame(listWindow)
         frm.grid(row=0, column=0, columnspan=4)
         ttk.Label(frm, text="Select project").grid(column=0, row=0)
         theCombo=ttk.Combobox(frm, values=tdata, width = 100)
         theCombo.grid(column=1, row=1)
         ttk.Button(frm, text="OK", command=partial(processProjectSelection,listWindow,theCombo,cProjectID)).grid(column=3, row=2)
         ttk.Button(frm, text="Cancel", command=listWindow.destroy).grid(column=2, row=2)

         listWindow.mainloop() 

def dictionary_payload_partusage(element_id, name = None, quali_name = None, owner = None, owning = None):
    dictionary_payload_partusage = {
        "payload": {
            '@type': 'PartUsage',
            '@id': element_id,
            'elementId': element_id,
            'name': name,
            'owner': owner,
            'owningMembership': owning,
            'owningNamespace': owner,
            'owningRelationship': owning,
            'qualifiedName': quali_name
        },
        "identity": {"@id": element_id}
    }
    return dictionary_payload_partusage

def dictionary_payload_owningmembership(element_id, member_element, memberId, owned_member_element, owned_member_element_id, target, name, owner):
    dictionary_payload_owningmembership = {
        "payload": {'@type': 'OwningMembership',
                    '@id': element_id,
                    'elementId': element_id,
                    'memberElement': member_element,
                    'memberElementId': memberId,
                    'memberName': name,
                    'membershipOwningNamespace': owner,
                    'ownedMemberElement': owned_member_element ,
                    'ownedMemberElementId': owned_member_element_id,
                    'ownedMemberName': name,
                    'ownedRelatedElement': [owned_member_element],
                    'owningRelatedElement': owner,
                    'relatedElement': [owner, owned_member_element],
                    'source': [owner],
                    'target': [target]
                   },
        "identity": {"@id": element_id}
    }
    return dictionary_payload_owningmembership

def dictionary_payload_package(element_id, name = None, quali_name = None, member = None, membership = None ):
    dictionary_payload_package = {
        "payload": {'@type': 'Package',
                    '@id': element_id,
                    'elementId': element_id,
                    'member': member,
                    'membership': membership,
                    'name': name,
                    'ownedElement': member,
                    'ownedMember': member,
                    'ownedMembership': membership,
                    'ownedRelationship': membership,
                    'qualifiedName': quali_name
                   },
        "identity": {"@id": element_id}
    }
    return dictionary_payload_package

def merge_duplicate_itemdefs(target_payload, rep_source, rep_target):
    # Merges duplicate object in the domain model, which are present both 
    # in the use case analysis model and in the functional architecture model.
    # To be called before commiting the functional architecture model, to clean it before commit.
    
    rep_src = rep_source
    obsolete_ids=[]
    replacement_ids=[]
    skipped_ids=[]
    rep_t=[]
    
    for i in range(len(rep_src)):
         if rep_src[i].get("@type") == "ItemDefinition":
            for o in rep_target:
                if o.get("@type") == "ItemDefinition" and rep_src[i]!={}:
                    if o.get('name')==rep_src[i].get('name'):
                        # Remember Ids of duplicate ItemDef for replacement
                        obsolete_ids.append(rep_src[i].get('@id'))
                        replacement_ids.append(o.get('@id'))
                        rep_src[i]={}
                        
                        
                        
    # We also need to remove potential package memberships it is those 
    # OwningMemberships where 'ownedMemberElementId' is the id of the ItemDef
    for i in range(len(rep_src)):                        
         if rep_src[i]!={}:      
            bAppend = True
            if rep_src[i].get('@type') == 'OwningMembership':
                for obs in obsolete_ids:
                    if rep_src[i].get('ownedMemberElementId') == obs:
                        bAppend = False
                        skipped_ids.append(rep_src[i].get('@id'))
            if bAppend == True:             
                rep_t.append({"payload": rep_src[i],
                      "identity": {"@id": rep_src[i]['@id']}})
        
        
    #Replace all references to duplicates by references to the existing ItemDefs
    rep_t_string = json.dumps(rep_t)
    for irep in range(len(obsolete_ids)):
        rep_t_string = rep_t_string.replace(obsolete_ids[irep],replacement_ids[irep])
        
    #Remove all references to removed OweningMemberships
    for irep in range(len(skipped_ids)):
        rep_t_string = rep_t_string.replace('{"@id": "'+skipped_ids[irep]+'"},','').replace('{"@id": "'+skipped_ids[irep]+'"}','')


    return json.loads(rep_t_string)   



def copy_elements(source_host, source_id, target_host, target_id, bMerge = False):

    rep = read_full_repository(source_host, source_id)

    #If we want to merge or link source and target data then we should read the target repository
    if bMerge==True:
        rep_target = read_full_repository(target_host, target_id)

    
    rep_t = []
    for i in range(len(rep)):
        rep_t.append({"payload": rep[i],
                      "identity": {"@id": rep[i]['@id']}})
                      
                      
    #Merge ItemDefs, if required by setting bMerge == True                      
    if bMerge==True:
        rep_t = merge_duplicate_itemdefs(rep_t, rep, rep_target)
        
    commit_body1 = '{"change":' + json.dumps(rep_t) + '}'
    response = requests.post(target_host + "/projects/" +target_id+ "/commits", headers={"Content-Type": "application/json"}, data = commit_body1)
    
    if response.status_code != 200:
        return False , response.json()
    else:
        return True , response.json()

def link_function(target_host, target_id , source_host, source_id):
    
    rep_source = read_full_repository(source_host, source_id)
    rep_target = read_full_repository(target_host, target_id)
    
    name_values = [item.get('name') for item in rep_target if item.get('name') is not None]
    source_names = name_values
    
    d_list = []
    
    # Initialize source_ok and target_ok to None or a default value
    source_ok = None
    target_ok = None
    t = None
    tar = None
    n = None
    
    for source_name in source_names:
    
        for i in range(len(rep_source)):
            if rep_source[i].get('@type') == 'PartUsage' and rep_source[i].get('name') == source_name:
                t = rep_source[i].get('@id')
                n = rep_source[i].get('name')

                source_ok = rep_source[i]

        for i in range(len(rep_target)):
            if rep_target[i].get('@type') == 'Package' and rep_target[i].get('name') == source_name:
                tar = rep_target[i].get('@id')

                target_ok = rep_target[i]


    

        #Now we create an owningmembership with an ID that we will later use to create the dependency
        ele_id=str(uuid.uuid4())
        owningmembership_element = str(uuid.uuid4())
        d_list.append(dictionary_payload_owningmembership(owningmembership_element, {'@id': ele_id}, ele_id, {'@id': ele_id}, ele_id, {'@id': ele_id}, '', {'@id':tar}))

        # Note that the id of the dependency is now the one that was used further above in the owningmembership
        # and the owningmembership is the one we created ourselves
        d_payload_dependency = dictionary_payload_dependency(ele_id, {'@id': t}, {'@id': tar}, {'@id': owningmembership_element}, n, {'@id': tar})

    
        d_list.append(d_payload_dependency)
        
        
    #we need to add a "payload" with an "identity" to enforce the ID of source_ok
    source_ok = {'payload': source_ok,'identity': {'@id': t} }
    d_list.append(source_ok)
    #The commit code was missing here, so I added it.
    commit_body =  '{"change": ' + json.dumps(d_list) +'}'
    commit_url = f"{target_host}/projects/{target_id}/commits" 

    
    response = requests.post(commit_url, 
                      headers={"Content-Type": "application/json"}, 
                      data=commit_body)
    
    print(response)
    print(response.json())
    
    if response.status_code != 200:
        return False , response.json()
    else:
        return True , response.json()

def dictionary_payload_dependency(element_id, client, owner, membership, quali_name, target):
    dictionary_payload_dependency = {
        "payload": {'@type': 'Dependency',
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
    return dictionary_payload_dependency