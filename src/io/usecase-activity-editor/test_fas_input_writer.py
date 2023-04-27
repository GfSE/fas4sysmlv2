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
#   This is test code to test writing FAS input to the repository 
#   via a hard-coded usecase-activity and functiona groups model to write

import os

cFileName = 'FAS-Input.txt'
FID=open(cFileName,'w')
FID.write('Group\nMusicPlayer\n 10200\n 14400\n 12001\n 4201\nGroup\nStorage\n 10600\n 8000\n 12001\n 4401\nGroup\nAccounting\n 12000\n 1000\n 7401\n 5601\nGroup\nIO_Customer\n 1200\n 1400\n 7401\n 18201\nElement\nGetMoney\n 2400\n 3000\n 5001\n 2601\nConnector\n 7400\n 4300\n 13300\n 4300\nmoney\n\n\n 7400\n 4300\n 5901\n 1\nElement\nMonitorPayment\n 13300\n 3000\n 5001\n 2601\nElement\nProvideMusicTrack\n 11400\n 9400\n 8801\n 2401\nConnector\n 15800\n 5600\n 15800\n 9400\n                   clearance\n 15800\n 5600\n 1\n 3801\nElement\nPlayMusicTrack\n 11400\n 15800\n 8801\n 2401\nConnector\n 15800\n 11800\n 15800\n 15800\n                      music_track\n 15800\n 11800\n 1\n 4001\nElement\nProduceSound\n 2400\n 15700\n 5001\n 2601\nConnector\n 11400\n 17000\n 7400\n 17000\naudio_signal\n\n\n 7400\n 17000\n 4001\n 1\n')
FID.close();
os.system('python write_fas_input.py "' + cFileName + '" ""');
os.remove(cFileName);
