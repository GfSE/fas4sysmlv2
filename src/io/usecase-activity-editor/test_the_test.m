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
%
%   This is test code to test the test code for the usecase-activity-editor

function test_the_test
  cFileName = 'FAS-Input.txt';
  FID=fopen(cFileName,'w');
  fprintf(FID,'Group\r\nMusicPlayer\r\n 10200\r\n 14400\r\n 12001\r\n 4201\r\nGroup\r\nStorage\r\n 10600\r\n 8000\r\n 12001\r\n 4401\r\nGroup\r\nAccounting\r\n 12000\r\n 1000\r\n 7401\r\n 5601\r\nGroup\r\nIO_Customer\r\n 1200\r\n 1400\r\n 7401\r\n 18201\r\nElement\r\nGetMoney\r\n 2400\r\n 3000\r\n 5001\r\n 2601\r\nConnector\r\n 7400\r\n 4300\r\n 13300\r\n 4300\r\nmoney\r\n\r\n\r\n 7400\r\n 4300\r\n 5901\r\n 1\r\nElement\r\nMonitorPayment\r\n 13300\r\n 3000\r\n 5001\r\n 2601\r\nElement\r\nProvideMusicTrack\r\n 11400\r\n 9400\r\n 8801\r\n 2401\r\nConnector\r\n 15800\r\n 5600\r\n 15800\r\n 9400\r\n                   clearance\r\n 15800\r\n 5600\r\n 1\r\n 3801\r\nElement\r\nPlayMusicTrack\r\n 11400\r\n 15800\r\n 8801\r\n 2401\r\nConnector\r\n 15800\r\n 11800\r\n 15800\r\n 15800\r\n                      music_track\r\n 15800\r\n 11800\r\n 1\r\n 4001\r\nElement\r\nProduceSound\r\n 2400\r\n 15700\r\n 5001\r\n 2601\r\nConnector\r\n 11400\r\n 17000\r\n 7400\r\n 17000\r\naudio_signal\r\n\r\n\r\n 7400\r\n 17000\r\n 4001\r\n 1\r\n');
  fclose(FID);
  test_fas_frontend(cFileName,'');
  delete(cFileName);
endfunction
