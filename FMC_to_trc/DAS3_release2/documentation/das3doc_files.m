%% Simtk project and files included in this release
% The Simtk project can be found at <https://simtk.org/home/das/>
%
%% 
% *Files included in this release*
%
% This release contains the following folders:
%
% *documentation*:
%
% This folder contains the model manual as a set of html files built in
% Matlab. It also contains the .m files used to publish the manual. This
% process runs various test routines on the model (contained in
% |das3test.m|), which allows the user to verify that the model works as it
% should, before using it.
%
% <html>
% <table border=1><tr><td>das3doc_main.html</td><td>This manual</td></tr>
% <tr><td>build_manual.m</td><td>Script that builds the manual</td></tr>
% <tr><td>das3doc_main.m</td><td>Script to publish 1st page of manual (main)</td></tr>
% <tr><td>das3doc_files.m</td><td>Script to publish 2nd page of manual (included files) </td></tr>
% <tr><td>das3doc_run.m</td><td>Script to publish 3rd page of manual (how to run) </td></tr>
% <tr><td>das3doc_model.m</td><td>Script to publish 4th page of manual (model reference) </td></tr>
% <tr><td>das3doc_test.m</td><td>Script to publish 5th page of manual (testing) </td></tr>
% <tr><td>html/</td><td>Other html pages and images required for this manual</td></tr></table>
% </html>
%
%%
% *OpenSim_model*:
%
% This folder contains the OpenSim model used to extract muscle moment arms
% and lengths (see <https://simtk.org/docman/view.php/322/1865/TBME-01023-2013.R2-preprint.pdf this publication> for more information). 
%
% <html>
% <table border=1><tr><td>das3.osim</td><td>OpenSim model</td></tr>
% <tr><td>Geometry</td><td>Geometry files for the OpenSim model</td></tr></table>
% </html>
% 
%%
% *realtime_model*:
%
% This folder contains the realtime model and functions for testing and
% using it
%
% <html>
% <table border=1><tr><td>das3.mexw32</td><td>The MEX function that contains the system dynamics for 32 bit Matlab</td></tr>
% <tr><td>das3.mexw64</td><td>The same MEX function for 64 bit Matlab</td></tr>
% <tr><td>model_struct.mat</td><td>A Matlab structure containing all model parameters</td></tr>
% <tr><td>equilibrium.mat</td><td>Passive equilibrium state used as initial condition to start simulator</td></tr>
% <tr><td>eq_position.sto</td><td>OpenSim motion file of the passive equilibrium state</td></tr>
% <tr><td>ode15s_simulation.mat</td><td>Output of the ode15s test, to allow comparison with the real-time solver</td></tr>
% <tr><td>ode15s_simulation.sto</td><td>OpenSim motion file of the ode15s test output</td></tr>
% <tr><td>das3test.m</td><td>Routines used to test the MEX function and the realtime model</td></tr>
% <tr><td>das3stick.m</td><td>Function that draws a stick figure of the model</td></tr>
% <tr><td>das3step.m</td><td>Advances the model by one time step using a first order Rosenbrock formula</td></tr>
% <tr><td>das3driver.m</td><td>Matlab GUI application to run real-time simulator and display movement in the Opensim Visualizer</td></tr>
% <tr><td>das3driver.fig</td><td>Figure file for the above GUI</td></tr></table>
% </html>
%
%%
% <html> 
% <b>Next:</b> <a href="das3doc_run.html">How to run the model</a><br>
% <b>Home:</b> <a href="../das3doc_main.html">Main</a>
% </html>
%