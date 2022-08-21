function das3stick(x, model, options)
% das3_stick.m: draw a stick figure of the model in state(s) x.
% 
% Inputs:
%	x               (nstates x N matrix) 	Model state (N=1), or a series of states
%	model           Matlab struct with model information
%   options         plotting options
%
% Dimitra Blana & Ton van den Bogert

	% set default options
	if nargin < 3 || ~isfield(options,'box')
		options.box = 1;
	end
	if nargin < 3 || ~isfield(options,'axes')
		options.axes = 1;
	end
    if nargin < 3 || ~isfield(options,'keepview')
        options.keepview = 0;
    end
	    
    % radii of thorax ellipsoid 
	Ax  = model.thorax_radii(1);
	Ay  = model.thorax_radii(2);
	Az  = model.thorax_radii(3);
    
    % center of thorax ellipsoid
	Mx  = model.thorax_center(1);
	My  = model.thorax_center(2);
	Mz  = model.thorax_center(3);
    
	% set plotting volume 
	xrange = [-0.3 0.6];
	yrange = [-1 0.5];
	zrange = [-0.35 0.35];
	
	% define the points used to draw each bone as stick or polygon, and their colors
	black = [0 0 0];
	red = [0.5 0 0];
	green = [0 0.5 0];
	blue = [0 0 0.5];
	yellow = [.75 .75 0];
	magenta = [.75 0 .75];
	cyan = [0 .75 .75];
    
    bonepoints = cell(model.nJoints,2);
    for iJnt = 2:model.nJoints
        bonepoints{iJnt-1,1} = [0,0,0;model.joints{iJnt}.location];
        bonepoints{iJnt-1,2} = black;        
    end
    bonepoints{model.nJoints,1} = [0,0,0;model.joints{iJnt-1}.location]; % estimated endpoint hand coordinates
    bonepoints{model.nJoints,2} = black;        
        
    bonepoints{1,2} = yellow;       % IJ-SC
    bonepoints{4,2} = green;        % SC-AC
    bonepoints{7,2} = magenta;      % AC-GH
    bonepoints{10,2} = red;         % GH-UL
    bonepoints{11,2} = blue;        % UL-RD
    bonepoints{12,2} = cyan;        % RD-HD
       	
	cla
    
	for i=1:size(x,2)
		
		% get the 3D bone position and orientation 
		d = das3('Visualization',x);
		if size(d,1) ~= size(bonepoints,1)
			error('das3stick: bonepoints structure is not consistent with number of bones');
		end
		
		R = reshape(d(1,4:12),3,3)';	% orientation matrix
        [xx,yy,zz] = ellipsoid(Mx,My,Mz,Ax,Ay,Az,R);
        [row,col,~] = find(zz>0);
        newx = xx(row,col);
        newy = yy(row,col);
        newz = zz(row,col);
        mesh(newz,newx,newy);
    
		% draw each bone
		hold on
		for j = 1:size(d,1);
			p = d(j,1:3)';					% position vector of bone
			R = reshape(d(j,4:12),3,3)';	% orientation matrix
			
			% create n x 3 matrix of the bone points local coordinates
			plocal = bonepoints{j,1}';
			npoints = size(plocal,2);
			
			% transform to global coordinates
			pglobal = repmat(p,1,npoints) + R*plocal;
			
			% plot points
			color = bonepoints{j,2};
			xx = pglobal(1,:);
			yy = pglobal(2,:);
			zz = pglobal(3,:);
			plot3(zz,xx,yy,'Color',color,'LineWidth',2)
		end

		% set the axes and viewpoint
		axis('equal');
		axis([zrange xrange yrange]);
		xlabel('Z');
		ylabel('X');
		zlabel('Y');
		if (options.box)
			box on
		end
		if (~options.keepview)
			view(157, 6);
		end
		if (~options.axes)
			axis off
		end
	end
	
	hold off;
end


function [xx,yy,zz]=ellipsoid(varargin)
%ELLIPSOID Generate ellipsoid.
%   [X,Y,Z]=ELLIPSOID(XC,YC,ZC,XR,YR,ZR,R,N) generates three
%   (N+1)-by-(N+1) matrices so that SURF(X,Y,Z) produces an
%   ellipsoid with center (XC,YC,ZC) and radii XR, YR, ZR, rotated by R.
% 
%   [X,Y,Z]=ELLIPSOID(XC,YC,ZC,XR,YR,ZR,R) uses N = 20.
%   [X,Y,Z]=ELLIPSOID(XC,YC,ZC,XR,YR,ZR) uses R = eye(3).

%   ELLIPSOID(...) and ELLIPSOID(...,N) with no output arguments
%   graph the ellipsoid as a SURFACE and do not return anything.
%
%   ELLIPSOID(AX,...) plots into AX instead of GCA.
%
%   The ellipsoidal data is generated using the equation:
%
%    (X-XC)^2     (Y-YC)^2     (Z-ZC)^2
%    --------  +  --------  +  --------  =  1
%      XR^2         YR^2         ZR^2
%
%   See also SPHERE, CYLINDER.

%   Dimitra Blana Nov 2014 based on ellipsoid.m 
%   by Laurens Schalekamp and Damian T. Packer
%   Copyright 1984-2002 The MathWorks, Inc. 

% Parse possible Axes input
narginchk(6,8);
[cax,args,nargs] = axescheck(varargin{:});

[xc,yc,zc,xr,yr,zr] = deal(args{1:6});
n  = 20;
R = eye(3);
if nargs > 6
	R = args{7}; 
end
if nargs > 7
	n = args{8}; 
end

[x,y,z] = sphere(n);

x = xr*x+xc;
y = yr*y+yc;
z = zr*z+zc;

for i=1:size(x,1)
    for j=1:size(x,2)
        rot_xyz = R*[x(i,j);y(i,j);z(i,j)];
        x(i,j) = rot_xyz(1);
        y(i,j) = rot_xyz(2);
        z(i,j) = rot_xyz(3);
    end
end

if(nargout == 0)
    cax = newplot(cax);
	surf(x,y,z,'parent',cax)
else
	xx=x;
	yy=y;
	zz=z;
end

end
