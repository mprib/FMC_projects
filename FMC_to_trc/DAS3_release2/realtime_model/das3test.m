function [out1] = das3test(command, arg1)
% This program runs various tests on the das3 model
% Dimitra Blana & Ton van den Bogert

clear global	% to ensure that das3step is properly initialized
tic;			% set the timer

if (nargin < 1)
    error('das3test needs command string as first input');
end

% Some model related variables
modelparams = load('model_struct'); 
model = modelparams.model;

ndof = model.nDofs;
nmus = model.nMus;
nstates = 2*ndof + 2*nmus;

% Define indices to the state variables within the state vector x
iq = 1:ndof;
iqdot = max(iq) + (1:ndof);
iLce = max(iqdot) + (1:nmus);

% Find DOF names
dofnames = cell(ndof,1);
for idof=1:ndof
    dofnames{idof} = model.dofs{idof}.osim_name;
end

% Find muscle names
musclenames = cell(nmus,1);
for imus=1:nmus
    musclenames{imus} = model.muscles{imus}.osim_name;
end

% Initialize the model
das3('Initialize',model);

% Construct a state that should be close to static equilibrium
xneutral= zeros(nstates,1);
% Joint angles such that the arm hangs down
xneutral(1:ndof) = [-0.38 0.19 0.23 0.64 -0.38 -0.29 0.42 0.30 0.27 0.39 1.49];
xneutral(iLce) = 1.0;
lengths = das3('Musclelengths',xneutral);
LCEopt = das3('LCEopt');
SEEslack = das3('SEEslack');
xneutral(iLce) = (lengths - SEEslack)./LCEopt;

% These are the range of motion limits (useful to know for some of the tests)
xlims = das3('Limits')';

% ======================= Do the stickfigure test
if strcmp(command, 'vis')
    disp('Visualization test...');
    figure(1);clf;
    das3stick(xneutral,model);
    snapnow;
    % Move the joints sequentially
    for i=1:ndof
        disp(['Hit ENTER to move ' dofnames{i}]); 
        pause;  
        xneutral(i) = xneutral(i) + 0.5;
        das3stick(xneutral,model);
        snapnow;
    end    
end

% ======================= Do the speed test
if strcmp(command, 'speed')
    disp('Speed test...');
    tic
    Neval = 100;
    for i=1:Neval
        x = rand(nstates,1);
        xdot = rand(nstates,1);
        u = rand(nmus,1);
        M = rand(5,1);
        exF = rand(2,1);
        handF = rand(3,1);
        [f, ~, dfdxdot, dfdu, ~, ~, ~] = das3('Dynamics',x,xdot,u,M,exF,handF);
    end
    fprintf('Computation time for each model evaluation: %6.2f ms\n',1000*toc/Neval);
    
    % Do another speed test, only with the muscle dynamics, and no multibody dynamics
    tic
    for i=1:Neval
        x = rand(nstates,1);
        das3('Jointmoments',x);
    end
    fprintf('Computation time with muscle dynamics and no multibody dynamics:      %6.2f ms\n',1000*toc/Neval);
end

% ======================= Do the moment arms test
if strcmp(command, 'moment arms')
    disp('Moment arm test...');
    x = zeros(nstates,1);
    % Put angles not exactly at midpoint, because some joint angles are zero there which causes problems (which?)
    x(1:ndof) = (xlims(:,1)+xlims(:,2))/2 + 0.001;
    make_osimm('momarm_position',dofnames,x(1:ndof));
    MA = das3('Momentarms', x);
    figure(1);clf;
    spy(MA');
    axis('fill');
    xlabel('muscle element');
    ylabel('DOF number');
    
    % For each DOF, report the largest positive and negative moment arms
    fprintf('DOF   Largest positive moment arm          Largest negative moment arm\n')
    fprintf('----  -----------------------------        -----------------------------------\n');
    MA = full(MA);
    for i = 1:ndof
        [dmin, imin] = min(MA(:,i));
        [dmax, imax] = max(MA(:,i));
        name_min = musclenames{imin};
        name_max = musclenames{imax};
        if dmin==0 && dmax==0
            fprintf('%-15s\n',dofnames{i});			% there are no muscles spanning this joint
        else
            fprintf('%-15s  %6.1f mm (%-16s)         %6.1f mm (%-16s)\n',dofnames{i},1000*dmax,name_max,1000*dmin,name_min);
        end
    end
    % Write the moment arm matrix (in mm) on a CSV file
    fid = fopen('momentarms.csv','w');
    if (fid < 0)
        error('Could not write to file momentarms.csv');
    end
    for i=1:ndof
        fprintf(fid,',%s',dofnames{i});
    end
    fprintf(fid,'\n');
    for i = 1:nmus
        fprintf(fid,'%s',musclenames{i});
        for j=1:ndof
            if (MA(i,j) ~= 0)
                fprintf(fid,',%6.3f',1000*MA(i,j));
            else
                fprintf(fid,',');
            end
        end
        fprintf(fid,'\n');
    end
    fclose(fid);
end

% ======================= Do the equilibrium test
if strcmp(command, 'equilibrium')
    disp('Equilibrium test...');
    
    % No muscle excitations or speed
    u = zeros(nmus,1);
    xdot = zeros(nstates,1);
    
    % Settings for the Levenberg-Marquardt (LM) solver
    neval = 0;
    options.xtol = 1e-10;
    options.ftol = 1e-10;
    options.lambda = 10;
    options.maxiterations = 50000;
    
    % Initial guess for equilibrium state
    if exist('equilibrium.mat','file')
        load('equilibrium.mat');
    else
        x = xneutral;
    end
    
    % Solve the equilibrium with the LM solver
    tic;
    figure(1);clf;
    [x, normf, info, niter] = lmopt(@resfun, x, options);
        
    disp(['Norm of f was: ',num2str(normf,'%10.4e')]);
    disp('This must be close to zero, otherwise it is not an equilibrium');
    das3stick(x,model);
 
    if (info ~= 0)
        disp('Warning: equilibrium not found');
        disp('dbquit if you do not want this result saved.');
        keyboard
    end

    % Save the result
    make_osimm('eq_position',dofnames,x(1:ndof));
    save('equilibrium.mat','x');
    disp('Equilibrium state was stored on equilibrium.mat');
    disp('Equilibrium posture was stored on eq_position.sto');
    
    disp(' ');
    disp('-------------Equilibrium state-------------');
    disp(' ');
	fprintf('DOF               angle(deg)   ang.vel(deg/s)   moment(Nm)  \n');
	fprintf('--------------- -------------- -------------- --------------\n');
    moments = das3('Jointmoments',x);
	for i=1:ndof
		fprintf('%-15s %9.3f      %9.3f      %9.3f\n',dofnames{i}, 180/pi*x(i), 180/pi*x(ndof+i), moments(i));
	end

    disp(' ');
    disp('---------Muscle variables at equilibrium---------');
    disp(' ');
	fprintf('Muscle           Lce/Lceopt  Active state   Force(N)  \n');
	fprintf('--------------- ------------ ------------ ------------\n');
    forces = das3('Muscleforces',x);
 	for i=1:nmus
		fprintf('%-15s %9.3f    %9.3f    %9.3f\n',musclenames{i}, x(2*ndof+i), x(2*ndof+nmus+i), forces(i));
	end

    disp(' ');
    disp('-----------Other variables---------------');
    disp(' ');
    
    [f, dfdx, dfdxdot, dfdu, Fgh, Fscap] = das3('Dynamics', x, zeros(nstates,1), zeros(nmus,1));
    disp('Force in glenohumeral joint:')
    disp(Fgh');
    
    % Calculate GH stability value
    aphi=tand(38.55);
    atheta=tand(44.37);
    Rgt = glenoid_scap;
        
    Fgh0 = Rgt*Fgh;  % take glenoid orientation into account
    if norm(Fgh0), Fgh0 = Fgh0/norm(Fgh0); end
    % Decompose into polar angles
    thetar = asin(-Fgh0(2));

    if ~(sqrt(Fgh0(1)^2+Fgh0(3)^2)), phir = 0.0;
    else phir=asin(Fgh0(3)/sqrt(Fgh0(1)^2+Fgh0(3)^2));
    end
    FGHstab = (thetar/atheta)^2 + (phir/aphi)^2 - 1; % <=0
    
    disp('Glenohumeral stability value:');
    disp(FGHstab);
        
    disp('Contact force in Trigonum Spinae of the scapula:');
    disp(Fscap(:,1)');
    disp('Contact force in Inferior Angle of the scapula:');
    disp(Fscap(:,2)');
    F_contact = das3('Scapulacontact', x);
    disp('Thorax surface equation solved for Trigonum Spinae of the scapula:');
    disp(F_contact(1));
    disp('Thorax surface equation solved for Inferior Angle of the scapula:');
    disp(F_contact(2));
        
    disp(' ');
    disp('----------------Stability analysis----------------');
    disp(' ');
    eigenvalues = eig(full(-inv(dfdxdot)*dfdx));
    figure(2);clf;semilogx(eigenvalues,'o');title('Eigenvalues of equilibrium state');
    xlabel('Real');
    ylabel('Imaginary');
    disp('Eigenvalues with largest real part (s^-1):');
    disp('(must all be negative for stability)');
    realparts = sort(real(eigenvalues),'descend');
    disp(realparts(1:5)');
    disp('');
    disp('Smallest time constants (s):');
    timeconst = sort(1./abs(eigenvalues));
    disp(num2str(timeconst(1:5)','%12.4e'));
    maximag = floor(max(abs((imag(eigenvalues)))));
    disp(' ');
    disp('The imaginary parts, representing (damped) oscillatory behavior,');
    fprintf('have a maximum of ~%d, which is equivalent to a frequency (f=omega/2pi) of  %3.1f Hz.\n',maximag,maximag/(2*pi));
    
    save('eq_test_results.mat','x','moments','forces','Fgh','FGHstab','Fscap','F_contact','eigenvalues');

end

    function [f,J] = resfun(x)
        % Returns f and df/dx for equilibrium solver
        neval = neval + 1;
        [f, J, dfdxdot, dfdu] = das3('Dynamics',x,xdot,u);
        
        % Produce output once every second
        printinterval = 0;					% time interval (s) between outputs on screen, use zero to report every iteration
        if (toc >= printinterval)
            tic;
            fprintf('Equilibrium eval # %d: Norm of f: %12.5e\n', neval, norm(f));
        end
    end


% ======================= Do the isometric muscle tests
if (strcmp(command, 'isometric') 	|| strcmp(command, 'all') )
    
    Lceopt = das3('LCEopt');
    dof_limits = das3('Limits')*180/pi;
    
    % load equilbrium state x
    load('equilibrium.mat');
    
    [dof1,ok] = listdlg('PromptString',{'Select a DOF for which to calculate';'isometric strength curves:';' '},...
        'SelectionMode','single',...
        'ListString',dofnames,'ListSize',[300 300]);
    if ~ok, return; end
    
    [dof2,ok] = listdlg('PromptString',{'Select a secondary DOF for the';[dofnames{dof1} ' curves :'];' '},...
        'SelectionMode','single',...
        'ListString',dofnames,'ListSize',[300 300]);
    if ~ok, return; end
    
    dof1_range = dof_limits(2,dof1)-dof_limits(1,dof1);
    values1 = dof_limits(1,dof1):dof1_range/9:dof_limits(2,dof1);  % 10 steps
    
    dof2_range = dof_limits(2,dof2)-dof_limits(1,dof2);
    values2 = dof_limits(1,dof2):floor(dof2_range/4):dof_limits(2,dof2);  % 5 steps
    
    disp(['Calculating ' dofnames{dof1} ' isometric strength curves, at '...
        num2str(floor(dof2_range/4)) '-degree intervals in ' dofnames{dof2} ' angle...']);
    
    isometric_curves(x,Lceopt,dofnames,dof1,values1,dof2,values2);
end

% ======================= Do the one-muscle moment test
if (strcmp(command, 'isometric1') || strcmp(command, 'all') )
    
    Lceopt = das3('LCEopt');
    dof_limits = das3('Limits')*180/pi;
    
    % Load equilbrium state x
    load('equilibrium.mat');
    
    [dof1,ok] = listdlg('PromptString',{'Select a DOF for which to calculate';'isometric strength curves:';' '},...
        'SelectionMode','single',...
        'ListString',dofnames,'ListSize',[300 300]);
    if ~ok, return; end
    
    dof1_range = dof_limits(2,dof1)-dof_limits(1,dof1);
    values1 = dof_limits(1,dof1):dof1_range/9:dof_limits(2,dof1);  % 10 steps
    
    disp(['Calculating ' dofnames{dof1} ' isometric strength curves for one muscle at a time...']);
    isometric_curves_one_mus(x,Lceopt,dofnames,dof1,values1);
end

% ======================= Do the isokinetic muscle tests
if (strcmp(command, 'isokinetic') 	|| strcmp(command, 'all') )
    Lceopt = das3('LCEopt');
    
    % Load equilbrium state x
    load('equilibrium.mat');
    
    % Muscle moment arms in this position
    momentarms = full(das3('Momentarms', x));
    
    % Moment-angular velocity curves
    [dof1,ok] = listdlg('PromptString',{'Select a DOF for which to calculate';'isokinetic strength curves:';' '},...
        'SelectionMode','single',...
        'ListString',dofnames,'ListSize',[300 300]);
    if ~ok, return; end
    
    disp(['Calculating isokinetic strength curves for ' dofnames{dof1} '...']);
    isokinetic_curves(x,momentarms,Lceopt,dofnames,dof1,-1000:100:1000);
end

% ======================= Do the ODE15s simulation test
if strcmp(command, 'ode15s')
    
    disp('Running simulation with ODE15s...');
    neval = 0;
    nodefun = 0;
    printinterval = 2.0;
    load('equilibrium.mat');
    times = 0:0.005:0.5;
    xdot = zeros(nstates,1);              
    xdotinitialguess = zeros(nstates,1);
    [tout, xout] = ode15s(@odefun, times, x);
    fprintf('Number of integration steps:    %d\n', nodefun);
    fprintf('Number of function evaluations: %d\n', neval);
    
    % Export result to mat file and opensim motion file
    save('ode15s_simulation','tout','xout');
    make_osimm('ode15s_simulation', dofnames, xout(:,1:ndof), tout);
    disp('Simulation result has been saved in ode15s_simulation.mat');
    disp('Simulated motion has been saved in ode15s_simulation.sto');

    % Plots on screen
    plotangles(tout,xout);

end

% ====================== Simulate arm movement ==============
% This is done with our own implicit algorithm, which will be used for real time simulation
if strcmp(command, 'simulate')
    disp('Simulating arm movements...');
    
    % set simulation parameters
    t = 0;
    tend = 0.5;
    if (nargin < 2)
        tstep = .003;
    else
        tstep = arg1;
    end
    nsteps = round((tend-t)/tstep);
    
    % Reserve space to store results
    tout = tstep*(0:nsteps)';
    xout = zeros(nsteps+1, nstates);
    tout(1) = t;
    
    % Load equilbrium state x
    load('equilibrium.mat');
    
    % Run simulation
    xout(1,:) = x';
    % Initialize variables
    step_u = zeros(nmus,1);
    step_xdot = zeros(nstates,1);             
    tic
    for i=1:nsteps
        u = stimfun(t);

        % Advance simulation by a step
        [x, step_xdot, step_u] = das3step(x, u, tstep, step_xdot, step_u);

        xout(i+1,:) = x';   % store result

        t = t + tstep;
    end
    simtime = toc;
    
    % Report computation time on the screen
    fprintf('CPU time per time step: %8.3f ms\n', 1000*simtime/nsteps);
    fprintf('Simulation speed is %8.3f times faster than real time\n',tend/simtime);
    
    % Plots on screen
    plotangles(tout,xout);
    
    % Export to mat file and to opensim motion file
    save('simulation','tout','xout');
    make_osimm('simulation', dofnames, xout(:,1:ndof), tout);
    disp('Simulation result has been saved in simulation.mat');
    disp('Simulated motion has been saved in simulation.sto');
    
    % Compare joint angles to the explicit simulation test and report RMS difference
    tout_test = tout;
    xout_test = xout;
    if exist('ode15s_simulation.mat','file')
        load('ode15s_simulation');		% this loads tout and xout from the mat file
    else
        disp('Could not load ode15s_simulation.mat');
        disp('Run the ode15s_simulation test first, if you want to quantify simulation errors.');
        return
    end
    
    % Resample our implicit results to the same times as the explicit simulation
    xout_test = interp1(tout_test, xout_test, tout, 'linear', 'extrap');
    
    % Compute the RMS error in joint angles, by comparing to explicit result
    angdiff = 180/pi*(xout(:,1:ndof) - xout_test(:,1:ndof));
    rmsdiff = sqrt(mean(angdiff.^2));
    disp('RMS errors in each joint angle (deg):');
    for i=1:ndof
        fprintf('%-6s: %8.3f\n', dofnames{i}, rmsdiff(i));
    end
    
    % Output the overall RMS error
    out1 = sqrt(mean(mean(angdiff.^2)));
    fprintf('\nOverall RMS error: %8.3f degrees\n', out1);
    
end

%=====================================================
% The following function solves the state derivatives from state and control,
% so we can simulate using a Matlab ODE solver.
% There are more efficient ways to do this, but this is just for model testing, not for efficient simulation.
function [xdot] = odefun(t,x)

    nodefun = nodefun+1;
    xdot = xdotinitialguess;

    u = stimfun(t);

    % Use a simple Newton-Raphson method
    resnorm = 1e10;
    niter = 0;
    while resnorm > 1e-8
        niter = niter + 1;
        [f,J] = zero(xdot);
        xdot = xdot - (J\f);		% do one full Newton step
        resnorm = norm(f);			% calculate norm of residuals
        if niter > 100
            niter = 0;
            xdot = zeros(nstates,1);
            disp('odefun is not converging... reinitializing');
        end
    end
    % Give some output on screen, every once in a while
    if (toc > printinterval)
        tic;
        fprintf('Step %d: Neval = %d -- t = %20.14g -- Norm(f) = %10.3e\n', nodefun, neval, t, resnorm);
        if (printinterval == 0.0), pause; end
    end

    % Update the xdot initial guess for a better start of the next step
    xdotinitialguess = xdot;
    nodefun = nodefun + 1;

    function [f,J] = zero(xdot)
        % Evaluate dynamics in current x and xdot
        [f, dfdx, J, dfdu] = das3('Dynamics',x, xdot, u);                   
        neval = neval+1;
    end
end

end

%=====================================================
function plotangles(t,x)
figure;
subplot(2,2,1)
plot(t,180/pi*x(:,4:6));
legend('SC\_roty','SC\_rotz','SC\_rotx');
xlabel('time (s)');
ylabel('angle (deg)');

subplot(2,2,2)
plot(t,180/pi*x(:,7:9));
legend('AC\_roty','AC\_rotz','AC\_rotx');
xlabel('time (s)');
ylabel('angle (deg)');

subplot(2,2,3)
plot(t,180/pi*x(:,10:12));
legend('GH\_roty','GH\_rotz','GH\_rotyy');
ylabel('angle (deg)');
xlabel('time (s)');

subplot(2,2,4)
plot(t,180/pi*x(:,13:14));
legend('EL\_rotx','PS\_roty');
ylabel('angle (deg)');
xlabel('time (s)');

end
%==========================================================
function [u] = stimfun(t)
nmus = 138;

trampup = 0.5;      % time for muscle to ramp up

u = t/trampup*ones(nmus,1);

end
%==========================================================
function isometric_curves(x, Lceopt, dofnames, joint1, range1, joint2, range2)
% Produces isometric moment-angle curves for a joint
% One for each value in a range of angles in second joint

% Angles in degrees
ndof = length(dofnames);
angles = x(1:ndof)'*180/pi;
angvel = zeros(size(angles));

pascurves = zeros(length(range1),length(range2));
poscurves = zeros(length(range1),length(range2));
negcurves = zeros(length(range1),length(range2));
legends = cell(length(range2),1);
angle2_index=0;
for angle2 = range2
    angle2_index = angle2_index+1;
    angles(joint2) = angle2;
    x(joint2) = angle2*pi/180;
    pasmoments = zeros(length(range1),1);
    posmoments = zeros(length(range1),1);
    negmoments = zeros(length(range1),1);
    angle1_index=0;
    for angle1 = range1
        angle1_index = angle1_index+1;
        angles(joint1) = angle1;
        x(joint1) = angle1*pi/180;
        
        % Find sign of moment arm in this position
        momentarms = full(das3('Momentarms', x));
        
        pasmoments(angle1_index) = maxmoment(joint1, angles, angvel, momentarms, Lceopt, 0);
        posmoments(angle1_index) = maxmoment(joint1, angles, angvel, momentarms, Lceopt, 1);
        negmoments(angle1_index) = maxmoment(joint1, angles, angvel, momentarms, Lceopt, -1);
    end
    pascurves(:,angle2_index) = pasmoments;
    poscurves(:,angle2_index) = posmoments;
    negcurves(:,angle2_index) = negmoments;
    legends{angle2_index} = [char(dofnames(joint2)) ' ' num2str(angle2)];
    disp([char(dofnames(joint2)) ' ' num2str(angle2) ' done... ']);
end

% Find max and min moment to set axis limits
allcurves = [pascurves poscurves negcurves poscurves-pascurves negcurves-pascurves];
allcurves = reshape(allcurves,[],1);
minmom = min(allcurves);
maxmom = max(allcurves);
momrange = maxmom-minmom;

figure;
% Plot total moments on left side of figure
subplot(2,3,1);
plot(range1, poscurves,'x-');
ylim([minmom-0.1*momrange maxmom+0.1*momrange]);
xlim([min(range1) max(range1)]);
title('positive moment','Interpreter', 'none');
ylabel('moment (Nm)');
subplot(2,3,4);
plot(range1, negcurves,'x-');
ylim([minmom-0.1*momrange maxmom+0.1*momrange]);
xlim([min(range1) max(range1)]);
xlabel('angle (deg)');
ylabel('moment (Nm)');
title('negative moment','Interpreter', 'none');

% Plot passive moments in middle column of figure
subplot(2,3,2);
plot(range1, pascurves,'x-');
ylim([minmom-0.1*momrange maxmom+0.1*momrange]);
xlim([min(range1) max(range1)]);
title([char(dofnames(joint1)) ': passive moment'],'Interpreter', 'none');
xlabel('angle (deg)');

% Subtract passive moments and plot in rightmost column of figure
subplot(2,3,3);
plot(range1, poscurves-pascurves,'x-');
ylim([minmom-0.1*momrange maxmom+0.1*momrange]);
xlim([min(range1) max(range1)]);
title('positive - passive','Interpreter', 'none');
subplot(2,3,6);
plot(range1, negcurves-pascurves,'x-');
ylim([minmom-0.1*momrange maxmom+0.1*momrange]);
xlim([min(range1) max(range1)]);
title('negative - passive','Interpreter', 'none');
xlabel('angle (deg)');

legend(legends,'Interpreter','none','Position',[0.4 0.2 0.2 0.2]);
end

%=============================================================================================================
function isometric_curves_one_mus(x, Lceopt, dofnames, joint1, range1)
% Produces isometric moment-angle curves for a joint
% One for each muscle that crosses the joint

ndof = length(dofnames);

% Angles in degrees
angles = x(1:ndof)'*180/pi;
angvel = zeros(size(angles));

% Find sign of moment arm in this position
allmomentarms = full(das3('Momentarms', x));

% Find which muscles cross joint1
musindeces =  find(allmomentarms(:,joint1) ~= 0)';

pascurves = zeros(length(range1),length(musindeces));
poscurves = zeros(length(range1),length(musindeces));
negcurves = zeros(length(range1),length(musindeces));
legends = cell(length(musindeces),1);

mus_index=0;
for imus = musindeces
    mus_index=mus_index+1;
    
    pasmoments = zeros(length(range1),1);
    posmoments = zeros(length(range1),1);
    negmoments = zeros(length(range1),1);
    
    ang_index=0;
    for angle1 = range1
        ang_index=ang_index+1;
        angles(joint1) = angle1;
        x(joint1) = angle1*pi/180;
        
        % Find sign of moment arm in this position
        allmomentarms = full(das3('Momentarms', x));
        momentarms = zeros(size(allmomentarms));
        momentarms(imus,:) = allmomentarms(imus,:);
        pasmoments(ang_index) = maxmoment(joint1, angles, angvel, momentarms, Lceopt, 0);
        posmoments(ang_index) = maxmoment(joint1, angles, angvel, momentarms, Lceopt, 1);
        negmoments(ang_index) = maxmoment(joint1, angles, angvel, momentarms, Lceopt, -1);
    end
    pascurves(:,mus_index) = pasmoments;
    poscurves(:,mus_index) = posmoments;
    negcurves(:,mus_index) = negmoments;
    musname = das3('Musclename', imus);
    legends{mus_index} = musname;
    disp(['Muscle ' musname ' done... ']);
end

% Find max and min moment to set axis limits
allcurves = [pascurves poscurves negcurves poscurves-pascurves negcurves-pascurves];
allcurves = reshape(allcurves,[],1);
minmom = min(allcurves);
maxmom = max(allcurves);
momrange = maxmom-minmom;

figure;
% Plot total moments on left side of figure
subplot(2,3,1);
plot(range1, poscurves,'x-');
ylim([minmom-0.1*momrange maxmom+0.1*momrange]);
xlim([min(range1) max(range1)]);
title('positive mom','Interpreter', 'none');
ylabel('moment (Nm)');
subplot(2,3,4);
plot(range1, negcurves,'x-');
ylim([minmom-0.1*momrange maxmom+0.1*momrange]);
xlim([min(range1) max(range1)]);
xlabel('angle (deg)');
ylabel('moment (Nm)');
title('negative mom','Interpreter', 'none');

% Plot passive moments in middle column of figure
subplot(2,3,2);
plot(range1, pascurves,'x-');
ylim([minmom-0.1*momrange maxmom+0.1*momrange]);
xlim([min(range1) max(range1)]);
title([char(dofnames(joint1)) ': passive mom'],'Interpreter', 'none');
xlabel('angle (deg)');

% Subtract passive moments and plot in rightmost column of figure
subplot(2,3,3);
plot(range1, poscurves-pascurves,'x-');
ylim([minmom-0.1*momrange maxmom+0.1*momrange]);
xlim([min(range1) max(range1)]);
title('positive - passive','Interpreter', 'none');
subplot(2,3,6);
plot(range1, negcurves-pascurves,'x-');
ylim([minmom-0.1*momrange maxmom+0.1*momrange]);
xlim([min(range1) max(range1)]);
title('negative - passive','Interpreter', 'none');
xlabel('angle (deg)');
legend(legends,'Interpreter','none','Position',[0.4 0.2 0.2 0.2]);
end

function isokinetic_curves(x, momentarms, Lceopt, dofnames, joint, range)
% Produces isokinetic moment-angular velocity curves for a joint
%
% x             the state vector
% momentarms    the 138 muscle moment arms
% Lceopt        the 138 muscle optimal fibre lengths
% dofnames      the names of the ndof degrees of freedom
% joint         for which joint we will calculate curve
% range         the range of velocities

ndof = length(dofnames);

% Angles in degrees
angles = x(1:ndof)'*180/pi;
angvel = zeros(size(angles));
pasmoments = zeros(length(range),1);
posmoments = zeros(length(range),1);
negmoments = zeros(length(range),1);
vel_index=0;
for vel = range
    vel_index = vel_index+1;
    angvel(joint) = vel;
    pasmoments(vel_index) = maxmoment(joint, angles, angvel, momentarms, Lceopt, 0);
    posmoments(vel_index) = maxmoment(joint, angles, angvel, momentarms, Lceopt, 1);
    negmoments(vel_index) = maxmoment(joint, angles, angvel, momentarms, Lceopt, -1);
end

% Find max and min moment to set axis limits
allcurves = [pasmoments posmoments negmoments posmoments-pasmoments negmoments-pasmoments];
allcurves = reshape(allcurves,[],1);
minmom = min(allcurves);
maxmom = max(allcurves);
momrange = maxmom-minmom;

figure;
% Plot total moments on left side of figure
subplot(2,3,1);
plot(range, posmoments,'x-');
ylim([minmom-0.1*momrange maxmom+0.1*momrange]);
title('positive moment','Interpreter', 'none');
ylabel('moment (Nm)');
subplot(2,3,4);
plot(range, negmoments,'x-');
ylim([minmom-0.1*momrange maxmom+0.1*momrange]);
xlabel('angular velocity (deg/s)');
ylabel('moment (Nm)');
title('negative moment','Interpreter', 'none');

% Plot passive moments in middle column of figure
subplot(2,3,2);
plot(range, pasmoments,'x-');
ylim([minmom-0.1*momrange maxmom+0.1*momrange]);
title([char(dofnames(joint)) ': passive moment']);
xlabel('angular velocity (deg/s)');

% Subtract passive moments and plot in rightmost column of figure
subplot(2,3,3);
plot(range, posmoments-pasmoments,'x-');
ylim([minmom-0.1*momrange maxmom+0.1*momrange]);
title('positive - passive','Interpreter', 'none');
subplot(2,3,6);
plot(range, negmoments-pasmoments,'x-');
ylim([minmom-0.1*momrange maxmom+0.1*momrange]);
title('negative - passive','Interpreter', 'none');
xlabel('angular velocity (deg/s)');

end

%=============================================================================================================
function mom = maxmoment(joint, angles, angvel, momentarms, Lceopt, sign)
% Simulate maximum moment at one joint, as function of all joint angles and angular velocities
% joint         for which joint we will calculate moment
% angles        the eleven joint angles (deg)
% angvel        the eleven angular velocities (deg/s)
% momentarms    the 138 muscle moment arms
% Lceopt        the 138 muscle optimal fibre lengths
% sign          0: passive, 1: max positive moment, -1: max negative moment

angles = angles*pi/180;		% convert to radians
angvel = angvel*pi/180;
ndof = length(angles);
nmus = length(Lceopt);

Act =  sign*momentarms(:,joint) > 0;	% vector that has a 1 for all muscles we want to activate

% Determine lengthening velocities of the muscle-tendon complexes, normalize to Lceopt
Vmuscle = -(momentarms * angvel') ./ Lceopt;

% Determine the Lce's at which there is contraction equilibrium (dF/dt = 0, or Lcedot = Vmuscle)
% Use Newton's method
% We want these state derivatives:
xdot = [zeros(2*ndof,1);Vmuscle;zeros(nmus,1)];
u = zeros(nmus,1);				% no stim, we don't care about activation dynamics here
x = [angles angvel zeros(1,nmus) Act']';

for imus=1:length(Lceopt)		% max number of Newton iterations
    Lce = 1.0;                  % initial guess for this muscle's Lce
    [~, ~, flag] = fzero(@contraction_equilibrium, Lce);
end

if (flag < 0)
    fprintf('maxmoment: muscle contraction equilibrium not found within max number of iterations.\n');
    keyboard
end

% Now determine the joint moments at this state of the system
moments = das3('Jointmoments', x);
mom = moments(joint);

    function [F] = contraction_equilibrium(Lce)
        x(2*ndof+imus) = Lce;
        f = das3('Dynamics',x, xdot, u);
        F = f(2*ndof+imus);
    end

end

%=============================================================================================================
function make_osimm(filename,dof_names,angles,time)
% Creates motion file for OpenSim
%
% Inputs:
% filename: the name of the motion file, without the extension
% angles: an num_dofs x n or n x num_dofs matrix of angles in radians, 
% n the number of frames
% time (optional): a 1xn or nx1 vector of time values. If this is not
% provided, the timestep is assumed to be 0.01s.
%
% Corrected: angles now in radians instead of degrees
% Dimitra Blana, February 2012

[nrows,ncolumns]=size(angles);
if ncolumns~=length(dof_names)
    angles=angles';
    nrows = ncolumns;
end

if nargin <4
    time = 0.01:0.01:0.01*nrows;
end

if size(time,2)~=1, time = time'; end
if size(time,1)~=nrows
    errordlg('The time vector does not have the same length as the angle data.','Dimension error');
    return;
end
data = [time angles];  

% create motion file
% the header of the motion file is:
%
% <motion name>
% nRows=x
% nColumns=y
% endheader
% time dofnames
%

dofnames = 'time';
dofstr = '%f';
for idof = 1:length(dof_names)
    dofnames= [dofnames '  ' dof_names{idof}];
    dofstr =  [dofstr '  %f'];
end
dofstr = [dofstr '\n'];

fid = fopen([filename '.sto'],'wt');
fprintf(fid,'%s\n',filename);
fprintf(fid,'%s%i\n','nRows=',nrows);
fprintf(fid,'%s\n',['nColumns=' num2str(length(dof_names)+1)]);
fprintf(fid,'%s\n','endheader');
fprintf(fid,'%s\n',dofnames);
fprintf(fid,dofstr,data');
fclose(fid);

end

%=============================================================================================================
function [x, fnorm, info, iterations] = lmopt(fun, x0, options)
	% solves a least-squares optimization problem using the Levenberg-Marquardt method from Numerical Recipes

	% initialize
	info = 0;
	iterations = 0;
	x = x0;
	[f, J] = fun(x);
	bestfnorm = norm(f);
	if isfield(options, 'lambda')
		lambda = options.lambda;
	else
		lambda = 0.001;
	end
		
	% Start loop
	while (1)
		iterations = iterations + 1;
		
		% compute augmented Hessian H2= J'*J + lambda*I
		H2 = J'*J + lambda * eye(size(x,1));

		% solve dx from modified normal equations: H2*dx = -J'*f
		dx = -H2 \ (J'*f);
		
		% limit the step size, if requested
		if isfield(options, 'stepmax')
			stepfrac = max(abs(dx) ./ options.stepmax);
			if stepfrac > 1
				dx = dx/stepfrac;		% reduce step by this fraction
			end
		end
		
		% save the current iterate and do the step dx
		xsave = x;
		fsave = f;
		x = x + dx;
		
		% check if number of iterations exceeded
		if (iterations > options.maxiterations)
			info = 1;
			return
		end
		
		% See how good we are doing now
		[f,J] = fun(x);					
		fnorm = norm(f);

		% Use the numerical recipes algorithm to adjust lambda
		if (fnorm <= bestfnorm)							% it is an improvement
			if (1-fnorm/bestfnorm) < options.ftol		% was reduction in f small enough?
				if sqrt(mean(dx.^2)) < options.xtol		% was change in x small enough?
					info = 0;
					return;
				end
			end
			% otherwise, keep iterating
			bestfnorm = fnorm;
			lambda = lambda/2.0;
		else
			% not an improvement, undo the step and try again with larger lambda
			x = xsave;
			f = fsave;
			lambda = lambda*2.0;
		end
		% fprintf('Norm of f: %10.4e   Lambda: %10.4e   RMSdx: %10.4e  %10.4e\n', fnorm, lambda, sqrt(mean(dx.^2)),bestfnorm);
	end

end

%=============================================================================================================
function Rginv = glenoid_scap
% finds rotation matrix between scapular coordinate frame and glenoid
% orientation based on the Delft Shoulder and Elbow model cadaver file
% all positions are in the global coordinate frame, in cm

% Get positions from dsp file:
% position glenohumeral joint
GH_centre = [17.08   -1.92    6.55];
% mid-point articular surface glenoid
glenoid_centre=[15.14   -1.98    7.81];
% In vivo palpated bony landmark at the scapula (AA):
AA = [18.26    0.75   10.56];
% In vivo palpated bony landmark at the scapula (TS):
TS = [7.50   -1.17   15.60];
% In vivo palpated bony landmark at the scapula (AI):
AI=[10.16  -12.62   15.67];

% Find scapular coordinate frame:
% local x-axis : AA to TS               										
% local z-axis : perpendicular to x and the line connecting AA and AI     	
% local y-axis : perpendicular to z and x				                       	
Xs = (AA-TS) / norm(AA-TS);
Zs = cross(Xs,(AA-AI)); 
Zs = Zs/norm(Zs);
Ys = cross(Zs,Xs);
S = [Xs;Ys;Zs];

%% Find vector from glenoid to GH centre in the global frame:
glen_scap_v = glenoid_centre - GH_centre;
% in scapular frame:
glen_scap = S*glen_scap_v';

% find polar angles:
thetar = asin(-glen_scap(2));
if ~(sqrt(glen_scap(1)^2+glen_scap(3)^2))
    phir = 0.0;
else
    phir = asin(glen_scap(3)/(sqrt(glen_scap(1)^2+glen_scap(3)^2)));
end

% calculate orientation matrix of glenoid, Rg, and inverse
Rg=roty(phir)*rotz(thetar);
Rginv = Rg';
    
end

function [Ry]=roty(th)
% creates rotation matrix
% for rotations or th radians around the y axis
Ry(1,1)=cos(th);
Ry(1,3)=sin(th);
Ry(2,2)=1;
Ry(3,1)=-sin(th);
Ry(3,3)= cos(th);

end

function [Rz]=rotz(th)
% calculates the rotation matrix
% for rotations of th radians around the z axis

Rz(1,1)=cos(th);
Rz(1,2)=-sin(th);
Rz(2,1)= sin(th);
Rz(2,2)= cos(th);
Rz(3,3)=1;

end