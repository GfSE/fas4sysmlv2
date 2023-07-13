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

import sys
import os
from freesketchplugin_wrapper import *
from pathlib import Path
from shutil import copyfile




if Path('com').is_dir()==False:
    # If it is the first time calling this functiona after installation, run some prep:
    # We need to set up an emulated environment to run the Free Sketch Plugin stand-alone
    os.makedirs ('com' + os.sep + 'nomagic'+ os.sep + 'actions')
    os.makedirs ('com' + os.sep + 'nomagic'+ os.sep + 'magicdraw'+ os.sep + 'actions')
    os.makedirs ('com' + os.sep + 'nomagic'+ os.sep + 'magicdraw'+ os.sep + 'core')
    os.makedirs ('com' + os.sep + 'nomagic'+ os.sep + 'magicdraw'+ os.sep + 'ui' + os.sep + 'dialogs')

    copyfile('helper_code' + os.sep + 'ActionsCategory.java', 'com'+ os.sep +'nomagic'+ os.sep +'actions'+ os.sep + 'ActionsCategory.java')
    copyfile('helper_code' + os.sep + 'NMAction.java', 'com'+ os.sep +'nomagic'+ os.sep +'actions'+ os.sep + 'NMAction.java')
    copyfile('helper_code' + os.sep + 'ActionsConfiguratorsManager.java', 'com'+ os.sep +'nomagic'+ os.sep +'magicdraw'+  os.sep +'actions'+ os.sep + 'ActionsConfiguratorsManager.java')
    copyfile('helper_code' + os.sep + 'Application.java', 'com'+ os.sep +'nomagic'+ os.sep + 'magicdraw'+ os.sep +'core'+ os.sep + 'Application.java')
    copyfile('helper_code' + os.sep + 'myInstance.java', 'com'+ os.sep +'nomagic'+ os.sep + 'magicdraw'+os.sep +'core'+ os.sep + 'myInstance.java')
    copyfile('helper_code' + os.sep + 'myProject.java', 'com'+ os.sep +'nomagic'+ os.sep + 'magicdraw'+ os.sep +'core'+ os.sep + 'myProject.java')
    copyfile('helper_code' + os.sep + 'MDDialogParentProvider.java', 'com'+ os.sep +'nomagic'+ os.sep + 'magicdraw'+  os.sep +'ui'+ os.sep + 'dialogs'+ os.sep + 'MDDialogParentProvider.java')



cFolderName = sys.argv[1]
cModelElementName = sys.argv[2]


	


run_freesketchplugin(cFolderName, cModelElementName)
