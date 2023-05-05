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
# The code wraps around the core function to call it from the usecase-activity-editor
#
#
# The input comes via a file written during the fas input generation to transport the project number
#




import sys
import os
import platform
cFolderName = sys.argv[1]
sys.path.insert(1,cFolderName.strip().replace('io/usecase-activity-editor','core').replace('io\\usecase-activity-editor','core'))
from fas4sysmlv2_main import *  


cProjectIdFile = cFolderName.strip() + 'project_id.txt'
FID1=open(cProjectIdFile ,'r');
cID = ''
for tline in FID1:
    cID = tline
FID1.close()

run_fas4sysml(cID)

     




  
