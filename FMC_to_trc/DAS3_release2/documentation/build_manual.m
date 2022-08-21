% Script that builds the manual
%
% Dimitra Blana

addpath('../realtime_model');

% Read in model parameters
load ('../realtime_model/model_struct');

% Place main page in top documentation directory
publish('das3doc_main.m','outputDir',pwd,'showCode',false);

% Place everything else in folder "html"
publish('das3doc_files.m','outputDir','html','showCode',false);
close all;
publish('das3doc_run.m','outputDir','html','showCode',true);
close all;
publish('das3doc_model.m','outputDir','html','showCode',false);
close all;
publish('das3doc_test.m','outputDir','html','showCode',true);
close all;