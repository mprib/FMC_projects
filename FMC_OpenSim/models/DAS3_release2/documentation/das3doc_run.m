%% How to run the model
%
% The file |das3.mexw64| (or |das3.mexw32| for 32-bit) is a Matlab MEX function that contains the system
% dynamics, and other functions, accessible via a Matlab function
% interface.  The file |model_struct.mat| 
% contains model parameters for the passive joint properties, muscle models,
% muscle path polynomials and GH force vector polynomials. During
% initialization, the MEX function reads in the parameters from struct
% |model|.
%
% To run das3driver, which displays the model movement in real time using
% the OpenSim Visualizer, you have to set up the Opensim-Matlab scripting
% environment. To do this, follow these instructions:
% <http://simtk-confluence.stanford.edu:8080/display/OpenSim/Scripting+with+Matlab>
%
%
%% How to use the model
% The MEX function has several ways in which it can be used.

%% Initialization
%
% This needs to be done first.  
load model_struct;
das3('Initialize',model);

%% Dynamics
%
% This is to evaluate the model dynamics in the implicit form f(x, xdot, u) = 0.
%
% Inputs
%
% * x		(nstates x 1) 	Model state, consists of ndof generalized coordinates (rad), ndof generalized velocities (rad/s), nmus CE lengths (relative to LCEopt), and nmus muscle active states (between 0 and 1).
% * xdot	(nstates x 1) 	State derivatives
% * u		(nmus x 1) 	    Muscle excitations
%
% Optional inputs
%
% * M		(5 x 1)		Moments applied to the thorax-humerus YZY axes and the elbow flexion and supination axes
% * exF   (2 x 1)     Vertical force of amplitude exF(2) applied to the ulna at a distance of exF(1) (meters) from the elbow (to simulate a mobile arm support)
% * handF	(3 x 1) 	Force applied to the centre of mass of the hand (defined in the global frame: +X is laterally, +Y is upwards and +Z is posteriorly)
%
% Outputs
%
% * f		(nstates x 1) Dynamics imbalance
%
% Optional outputs
%
% * dfdx	(nstates x nstates sparse) 	    Jacobian of f with respect to x
% * dfdxdot	(nstates x nstates sparse) 	Jacobian of f with respect to xdot
% * dfdu	(nstates x nmus sparse)	        Jacobian of f with respect to u
% * FGH		(3 x 1)				        3D GH contact force, acting on scapula, expressed in scapula reference frame
% * FSCAP 	(3 x 2)				        3D Contact forces acting on TS and AI, expressed in thorax reference frame
% * qTH		(3 x 1)				        angles between thorax and humerus (YZY sequence)
%
% Notes:
% 
% # FGH is only correct when dynamics are satisfied, i.e. f is zero
% # The three Jacobians must always be requested together, or not at all.
% 

load('equilibrium.mat');
ndof = model.nDofs;
nmus = model.nMus;
nstates = 2*ndof + 2*nmus;
xdot = zeros(nstates,1);
u = zeros(nmus,1);
M = zeros(5,1);
exF = zeros(2,1);
handF = zeros(3,1);

[f, dfdx, dfdxdot, dfdu, FGH, FSCAP, qTH] = das3('Dynamics',x, xdot, u, M, exF, handF);

%% Extract mass of the muscle elements
%
% Output
%
% * MusMass	(nmus x 1)	Mass for all muscle elements (in kg)
%

MusMass = das3('MuscleMass')

%% Extract LCEopt of the muscle elements
%
% Output
%
% * Lceopt	(nmus x 1)	Optimal fiber length parameters for all muscle elements (in meters)
%

LCEopt = das3('LCEopt')

%% Extract SEEslack of the muscle elements
%
% Output 
%
% * SEEslack (nmus x 1)	Slack length of series elastic element for all muscle elements (in meters)
%

SEEslack = das3('SEEslack')

%% Extract dof limits
%
% Output
%
% * limits	(2 x ndof)	Lower and upper limits of the ndof dofs, in radians
%

limits = das3('Limits')

%% Compute stick figure coordinates
%
% Inputs
%
% * x		(nstates x 1) 	        Model state, consists of ndof generalized coordinates (rad), ndof generalized velocities (rad/s), nmus CE lengths (relative to LCEopt), and nmus muscle active states (between 0 and 1).
%
% Outputs
%
% * stick   	(nSegments x 12)	Position(3) and orientation(3x3) of nSegments segments
%
% Notes:
%
% #	Output only depends on the first ndofs elements of x (the joint angles)
%

stick = das3('Visualization', x)

%% Compute scapula contact
%
% Inputs
%
% * x		(nstates x 1) 	Model state, consists of ndof generalized coordinates (rad), ndof generalized velocities (rad/s), nmus CE lengths (relative to LCEopt), and nmus muscle active states (between 0 and 1).
%
% Outputs
%
% * F_contact (2 x 1)	    Thorax surface equation solved for TS and AI
%

F_contact = das3('Scapulacontact', x)

%% Compute joint moments
%
% Inputs
%
% * x		(nstates x 1) 	        Model state, consists of ndof generalized coordinates (rad), ndof generalized velocities (rad/s), nmus CE lengths (relative to LCEopt), and nmus muscle active states (between 0 and 1).
%
% Outputs
%
% * moments (ndof x 1)			Joint moments (N m)
%

moments = das3('Jointmoments', x)

%% Compute muscle forces
%
% Inputs
%
% * x		(nstates x 1) 	        Model state, consists of ndof generalized coordinates (rad), ndof generalized velocities (rad/s), nmus CE lengths (relative to LCEopt), and nmus muscle active states (between 0 and 1).
%
% Outputs
%
% * forces	(nmus x 1)			Muscle forces (N)
%

forces = das3('Muscleforces', x)

%% Compute moment arms
%
% Inputs
%
% * x		(nstates x 1) 	                Model state, consists of ndof generalized coordinates (rad), ndof generalized velocities (rad/s), nmus CE lengths (relative to LCEopt), and nmus muscle active states (between 0 and 1).
%
% Outputs
%
% * momentarms	(nmus x ndof sparse)	Moment arms of nmus muscle elements at ndof joints (meters)
%

momentarms = das3('Momentarms', x)

%% Compute muscle-tendon lengths
%
% Inputs
%
% * x		(nstates x 1) 	Model state, consists of ndof generalized coordinates (rad), ndof generalized velocities (rad/s), nmus CE lengths (relative to LCEopt), and nmus muscle active states (between 0 and 1).
%
% Outputs
%
% * lengths	(nmus x 1)	    Length of nmus muscle elements (meters)
%

lengths = das3('Musclelengths', x)

%% Find muscle name
%
% Inputs
%
% * number	(scalar)    Number of a muscle element, must be in the range 1..nmus
%
% Outputs
%
% * name	(string)	Name of the muscle element, as define on the das3.bio file
%

number = 1;
name = das3('Musclename', number)

%% Find if muscle crosses the glenohumeral joint
%
% Inputs
%
% * number	(scalar) 	        Number of a muscle element, must be in the range 1..nmus
%
% Outputs
%
% * crossGH_flag	(scalar)	1 if the muscle crosses GH, 0 if it doesn't
%

crossGH_flag = das3('crossGH', number)

%%
% <html> 
% <b>Next:</b> <a href="das3doc_model.html">Model reference</a><br>
% <b>Previous:</b> <a href="das3doc_files.html">Simtk project and files included in this release</a><br>
% <b>Home:</b> <a href="../das3doc_main.html">Main</a>
% </html>
%