function varargout = das3driver(varargin)
% DAS3DRIVER MATLAB code for das3driver.fig
%      DAS3DRIVER, by itself, creates a new DAS3DRIVER or raises the existing
%      singleton*.
%
%      H = DAS3DRIVER returns the handle to a new DAS3DRIVER or the handle to
%      the existing singleton*.
%
%      DAS3DRIVER('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in DAS3DRIVER.M with the given input arguments.
%
%      DAS3DRIVER('Property','Value',...) creates a new DAS3DRIVER or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before das3driver_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to das3driver_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES
%
% Dimitra Blana & Ton van den Bogert

% Edit the above text to modify the response to help das3driver

% Last Modified by GUIDE v2.5 25-Oct-2015 10:25:43

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @das3driver_OpeningFcn, ...
                   'gui_OutputFcn',  @das3driver_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before das3driver is made visible.
function das3driver_OpeningFcn(hObject, ~, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to das3driver (see VARARGIN)

% Choose default command line output for das3driver
handles.output = hObject;

set(handles.reset,'String','Start');
set(handles.reset,'BackgroundColor',[153 255 153]/255);
set(handles.text_scap,'String','0');
set(handles.text_cuff,'String','0');
set(handles.text_abd,'String','0');
set(handles.text_add,'String','0');
set(handles.text_shfl,'String','0');
set(handles.text_elfl,'String','0');
set(handles.text_elex,'String','0');
set(handles.text_pron,'String','0');
set(handles.text_sup,'String','0');

% define the muscle groups
handles.muscles = {[1:11 20 22 25:36];...
    [55:60 61:63 68:71 72:82];...
    42:47;...
    90:95;...
    [48:51 102:103];...
    [83:85 109:115 116:118];...
    [86:89 104:108 129:133 134:138];...
    [119:120 126:128];...
    121:125};

% handles.muscles = { ...
%      name								  first element	 last element
%     'trapezius scap. part'                       1       11  ; ...
%     'trapezius clav. part'                       12      13  ; ...
%     'levator scapulae'                           14      15  ; ...
%     'pectoralis minor'                           16      19  ; ...
%     'rhomboideus'                                20      24  ; ...
%     'serratus anterior'                          25      36  ; ...
%     'deltoideus, posterior'                      37      41  ; ...
%     'deltoideus, middle'                         42      47  ; ...
%     'deltoideus, anterior'                       48      51  ; ...
%     'coracobrachialis'                           52      54  ; ...
%     'infraspinatus'                              55      60  ; ...
%     'teres minor'                                61      63  ; ...
%     'teres major'                                64      67  ; ...
%     'supraspinatus'                              68      71  ; ...
%     'subscapularis'                              72      82  ; ...
%     'biceps, caput longum'                       83      83  ; ...
%     'biceps, caput breve'                        84      85  ; ...
%     'triceps, caput longum'                      86      89  ; ...
%     'latissimus dorsi'                           90      95  ; ...
%     'pect. major, thor. part'                    96     101  ; ...
%     'pect. major, clav. part'                   102     103  ; ...
%     'triceps, medial part'                      104     108  ; ...
%     'brachialis'                                109     115  ; ...
%     'brachioradialis'                           116     118  ; ...
%     'pronator teres, hum-rad'                   119     119  ; ...
%     'pronator teres, uln-rad'                   120     120  ; ...
%     'supinator, uln-rad'                        121     125  ; ...
%     'pronator quadratus'                        126     128  ; ...
%     'triceps, lateral part'                     129     133  ; ...
%     'anconeus'                                  134     138 };

handles.steptime = 0.003;				

% load model parameters
modelparams = load('model_struct'); 
model = modelparams.model;

handles.ndof = model.nDofs;
handles.nmus = model.nMus;
handles.nstates = 2*handles.ndof + 2*handles.nmus;

% Initialize the stim levels
handles.stim = zeros(handles.nmus,1);

handles.xdot = zeros(handles.nstates,1);
handles.step_u = handles.stim;

% Initialize the das3 model
das3('Initialize',model);

% Opensim visualization:
% First, import the classes from the jar file so that these can be called
% directly
import org.opensim.modeling.*

% Load OpenSim model
Mod = Model('../OpenSim_model/das3.osim');

% Set up the visualizer to show the model and simulation
Mod.setUseVisualizer(true);

% initialize the system to get the initial state
handles.state = Mod.initSystem;

% get access to Visualizer
handles.ModVis = Mod.updVisualizer;

% get the coordinates structure
handles.CoordSet = Mod.getCoordinateSet();

% get the muscles
handles.MuscleSet = Mod.getMuscles();

% load initial state x
x0 = load('equilibrium.mat');
handles.x0 = x0.x;
handles.x = handles.x0;

% set dof values
for idof = 1:handles.ndof
    currentDof = handles.CoordSet.get(idof-1);    
    currentDof.setValue(handles.state,handles.x(idof),1);
end

% set muscle activation values
for imus = 1:handles.nmus
    currentMus = handles.MuscleSet.get(imus-1);    
    currentMus.setActivation(handles.state,handles.stim(imus));
end

handles.ModVis.show(handles.state);
pause(1);

% initialize timer     
handles.das3timer = timer(...
    'ExecutionMode', 'fixedDelay', ...   
    'Period', 0.3, ...                
    'TimerFcn', {@das3update,hObject},...
    'BusyMode','drop'); 

guidata(hObject, handles);

% UIWAIT makes das3driver wait for user response (see UIRESUME)
uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = das3driver_OutputFcn(~, ~, ~) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
%varargout{1} = handles.output;
varargout{1} = 0;


function das3update(~, ~, hObject)

try
handles = guidata(hObject);

for i=1:10    
    % Advance simulation by a step
    [handles.x, handles.xdot, handles.step_u] = das3step(handles.x, handles.stim, handles.steptime, handles.xdot, handles.step_u);
end

% set muscle activation values
for imus = 1:handles.nmus
    currentMus = handles.MuscleSet.get(imus-1);
    currentMus.setActivation(handles.state,handles.stim(imus));
end

% set dof values
for idof = 1:handles.ndof
    currentDof = handles.CoordSet.get(idof-1);
    currentDof.setValue(handles.state,handles.x(idof),1);
end

handles.ModVis.show(handles.state);

% Update handles structure
guidata(hObject, handles);

catch
end


% --- Executes on slider movement.
function scap_Callback(hObject, ~, handles)
% hObject    handle to scap (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider

handles.stim(handles.muscles{1}) = get(hObject,'Value');
set(handles.text_scap,'String',num2str(get(hObject,'Value')));

% Update handles structure
guidata(hObject, handles);


% --- Executes during object creation, after setting all properties.
function scap_CreateFcn(hObject, ~, ~)
% hObject    handle to scap (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end


% --- Executes on slider movement.
function cuff_Callback(hObject, ~, handles)
% hObject    handle to cuff (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider
handles.stim(handles.muscles{2}) = get(hObject,'Value');
set(handles.text_cuff,'String',num2str(get(hObject,'Value')));
% Update handles structure
guidata(hObject, handles);


% --- Executes during object creation, after setting all properties.
function cuff_CreateFcn(hObject, ~, ~)
% hObject    handle to cuff (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end


% --- Executes on slider movement.
function abd_Callback(hObject, ~, handles)
% hObject    handle to abd (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider
handles.stim(handles.muscles{3}) = get(hObject,'Value');
set(handles.text_abd,'String',num2str(get(hObject,'Value')));
% Update handles structure
guidata(hObject, handles);


% --- Executes during object creation, after setting all properties.
function abd_CreateFcn(hObject, ~, ~)
% hObject    handle to abd (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end


% --- Executes on slider movement.
function add_Callback(hObject, ~, handles)
% hObject    handle to add (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider
handles.stim(handles.muscles{4}) = get(hObject,'Value');
set(handles.text_add,'String',num2str(get(hObject,'Value')));
% Update handles structure
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function add_CreateFcn(hObject, ~, ~)
% hObject    handle to add (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end


% --- Executes on slider movement.
function sh_flex_Callback(hObject, ~, handles)
% hObject    handle to sh_flex (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider
handles.stim(handles.muscles{5}) = get(hObject,'Value');
set(handles.text_shfl,'String',num2str(get(hObject,'Value')));
% Update handles structure
guidata(hObject, handles);


% --- Executes during object creation, after setting all properties.
function sh_flex_CreateFcn(hObject, ~, ~)
% hObject    handle to sh_flex (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end


% --- Executes on slider movement.
function el_flex_Callback(hObject, ~, handles)
% hObject    handle to el_flex (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider
handles.stim(handles.muscles{6}) = get(hObject,'Value');
set(handles.text_elfl,'String',num2str(get(hObject,'Value')));
% Update handles structure
guidata(hObject, handles);


% --- Executes during object creation, after setting all properties.
function el_flex_CreateFcn(hObject, ~, ~)
% hObject    handle to el_flex (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end


% --- Executes on slider movement.
function extensors_Callback(hObject, ~, handles)
% hObject    handle to extensors (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider
handles.stim(handles.muscles{7}) = get(hObject,'Value');
set(handles.text_elex,'String',num2str(get(hObject,'Value')));
% Update handles structure
guidata(hObject, handles);


% --- Executes during object creation, after setting all properties.
function extensors_CreateFcn(hObject, ~, ~)
% hObject    handle to extensors (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end


% --- Executes on slider movement.
function pron_Callback(hObject, ~, handles)
% hObject    handle to pron (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider
handles.stim(handles.muscles{8}) = get(hObject,'Value');
set(handles.text_pron,'String',num2str(get(hObject,'Value')));
% Update handles structure
guidata(hObject, handles);


% --- Executes during object creation, after setting all properties.
function pron_CreateFcn(hObject, ~, ~)
% hObject    handle to pron (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end


% --- Executes on slider movement.
function supin_Callback(hObject, ~, handles)
% hObject    handle to supin (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider
handles.stim(handles.muscles{9}) = get(hObject,'Value');
set(handles.text_sup,'String',num2str(get(hObject,'Value')));
% Update handles structure
guidata(hObject, handles);


% --- Executes during object creation, after setting all properties.
function supin_CreateFcn(hObject, ~, ~)
% hObject    handle to supin (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end

% --- Executes on button press in reset.
function reset_Callback(hObject, ~, handles)
% hObject    handle to reset (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if strcmp(get(handles.das3timer, 'Running'), 'off')
    start(handles.das3timer);
    set(handles.reset,'String','Reset');
    set(handles.reset,'BackgroundColor',[255 102 102]/255);
end

handles.stim = zeros(handles.nmus,1);
handles.x = handles.x0;

set(handles.scap,'Value',0);
set(handles.cuff,'Value',0);
set(handles.abd,'Value',0);
set(handles.add,'Value',0);
set(handles.sh_flex,'Value',0);
set(handles.el_flex,'Value',0);
set(handles.extensors,'Value',0);
set(handles.pron,'Value',0);
set(handles.supin,'Value',0);
set(handles.text_scap,'String','0');
set(handles.text_cuff,'String','0');
set(handles.text_abd,'String','0');
set(handles.text_add,'String','0');
set(handles.text_shfl,'String','0');
set(handles.text_elfl,'String','0');
set(handles.text_elex,'String','0');
set(handles.text_pron,'String','0');
set(handles.text_sup,'String','0');

% Update handles structure
guidata(hObject, handles);


% --- Executes on button press in quit.
function quit_Callback(~, ~, handles)
% hObject    handle to quit (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if strcmp(get(handles.das3timer, 'Running'), 'on')
    stop(handles.das3timer);
end
delete(gcf)
delete(handles.das3timer);
