%% Model reference
%% Degrees of freedom
% The generalized coordinates (degrees of freedom, DOF) of the model are:
dofnames = cell(model.nDofs,1);
for idof = 1:model.nDofs
    fprintf('%3d.  %15s\n',idof,model.dofs{idof}.osim_name);
end

%% Muscles
% The muscle elements of the model are:
musclenames = cell(model.nMus,1);
for imus=1:model.nMus
    fprintf('%3d.  %10s\n',imus,model.muscles{imus}.name);
end

%% Muscle-skeleton coupling
%
% In the Opensim model, muscles are coupled to the skeleton by a muscle
% path model.  The muscle path model consists of an origin point, an
% insertion point, and points or objects in between which ensure that the
% muscle wraps realistically around the bones.  For the real-time
% simulator, we want to avoid using such a path model, for two reasons: (1)
% computation speed, and (2) differentiability.
%
% Fortunately, we can achieve these goals and stay consistent with the
% Opensim model.  We will represent the muscle-skeleton model by an
% analytical function $L_M(\textbf{q})$ which produces the muscle-tendon length as a
% function of the joint angles.  If this function is the same as what
% Opensim produces with its path model, the muscle is coupled to the
% skeleton in a way that is mechanically equivalent as far as the simulated
% movement is concerned.
%
% For fast computation and differentiability, we choose a multivariate
% polynomial function:
%
% $$L_{M}(q) = \sum_{i=1}^{Nterms}c_{i}\prod_{j=1}^{Ndof}q_{j}^{e_{ij}}$$
%
% The muscle path model is now fully encoded in a series of coefficients $c_i$
% and exponents $e_{ij}$. The exponents and coefficients are formatted 
% in the |model| struct as follows:

fprintf('For example, muscle %s:\n',model.muscles{1}.name); 
fprintf('model.muscles{1}.dof_indeces:\n');
disp(model.muscles{1}.dof_indeces);
fprintf('model.muscles{1}.lparams (e_ij):\n');
disp(model.muscles{1}.lparams);
fprintf('model.muscles{1}.lcoefs (c_i):\n');
disp(model.muscles{1}.lcoefs);

fprintf('This muscle has %d terms in its path polynomial.\n',model.muscles{1}.lparam_count); 
fprintf('There are %d joint angles involved, so each term has %d integer exponents e_ij  and one coefficient c_i.\n',model.muscles{1}.dof_count, model.muscles{1}.dof_count);  

%%
% <html> 
% <b>Next:</b> <a href="das3doc_test.html">Model testing</a><br>
% <b>Previous:</b> <a href="das3doc_run.html">How to run the model</a><br>
% <b>Home:</b> <a href="../das3doc_main.html">Main</a>
% </html>
%