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
# The code wraps around the renderer function to call it from the usecase-activity-editor
#
#
# The input comes via a file written during the fas input generation to transport the project number
#




import sys
import os
import platform
cFolderName = sys.argv[1]
from blockdiagram_renderer import *  

cProjectIdFile = cFolderName.strip().replace('io/functional-architecture-browser','io/usecase-activity-editor').replace('io\\functional-architecture-browser','io\\usecase-activity-editor') + 'project_id.txt'
FID1=open(cProjectIdFile ,'r');
cID = ''
cHost = ''
iNum = 0
for tline in FID1:
    iNum = iNum+1
    if iNum == 1:
        cID = tline.strip()
    else:
        cHost = tline.strip()
FID1.close()

run_renderer(cID, cHost)

     




  
