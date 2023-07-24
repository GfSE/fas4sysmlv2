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

#   This code deletes all SysML v2 projects on the host that is passed
#   as a first command line parameter. Handle with care!

#   Current work-around: Since it is not clear how to delete projects,
#   just delete the content and set the name to None

import sys
import os
import platform
import requests 
import json



cServerName = sys.argv[1]

response = requests.get(cServerName + "/projects" )
data = response.json()
while response.headers.get('Link','--NOTFOUND--').find('?page[after]')>-1:
            cNextPageLink = response.headers.get('Link').replace('<','').replace('; rel="next"','').replace('; rel="prev"','').replace('page[size]=100>','page[size]=10000>').replace('>','')
            response = requests.get(cNextPageLink)
            if response.status_code == 200:
                data = data + response.json()


 
if response.status_code!=200:
    print('Error retrieving projects from host ' + cServerName)
else:
    print('Deleting projects from host ' + cServerName)    
    for current_record in data:
        project_id = current_record.get('@id')
        print('  -> Deleting project id ' + project_id)
        branch_data = {
             "@type": "Branch",
             "name": None
        }
        response = requests.post(cServerName + "/projects/"+project_id+"/branches", 
                                      headers={"Content-Type": "application/json"}, 
                                      data=json.dumps(branch_data))
        if response.status_code!=200:
            print('    Error creating branch.')
        new_branch_id = response.json().get('@id')

        project_data = {
                      "@type": None,
                      "defaultBranch":{"@id": new_branch_id},
	              "name": None}

        response = requests.put(cServerName + "/projects/"+project_id, 
                                      headers={"Content-Type": "application/json"}, 
                                      data=json.dumps(project_data))
        if response.status_code!=200:
            print('    Error updating project with new branch.')
        response = requests.get(cServerName + "/projects/" + project_id + "/branches")
        data = response.json()
        for currenBranchRecord in data:
            branch_id = currenBranchRecord.get('@id')
  
            response = requests.get(cServerName + "/projects/" + project_id+ "/branches/" + branch_id)
            data = response.json()
            oCommit = data.get('head')

            if str(oCommit) != 'None':
                response = requests.get(cServerName + "/projects/" + project_id + "/commits/" +oCommit.get('@id')+"/elements")
                data = response.json()
                for currentElementRecord in data:      
                    element_id = currentElementRecord.get('@id')

                    commit_body = {
                        "@type": "Commit",
                        "change": [
                        {
                             "@type": "DataVersion",
                             "payload":None,
                             "identity": {
                                  "@id": element_id
                              }
                          }],
                          "previousCommit": {
                           "@id": oCommit.get('@id')
                          }
                    }
                    print('      -> Deleting element id ' + element_id)
                    response = requests.post(cServerName + "/projects/" + project_id + "/commits", 
                                      headers={"Content-Type": "application/json"}, 
                                      data=json.dumps(commit_body))
                    if response.status_code!=200:
                         print('    Error deleting element.')
                         print(response.json())
                         break
            if branch_id!=new_branch_id:
                print('      -> Deleting branch id ' + branch_id)
                response = requests.delete(cServerName + "/projects/" + project_id + "/branches/" + branch_id)
                if response.status_code!=200:
                    print('    Error deleting branch.')
                    print(response.json())
                    break


        response = requests.delete(cServerName + "/projects/" + project_id)
        if response.status_code!=200:
            print('    Error deleting project.')
        else:
            print('Project deleted')

