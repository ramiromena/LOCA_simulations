# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 18:22:24 2021

@author: rmenaand
"""

#Static structural

analyses_list = DataModel.AnalysisList #select all the available analyses
thermal = []
structural=[]

#Loop to classify thermal and structural analyses
for i in range(len(analyses_list)):
    analysis_i = analyses_list[i].PhysicsType
    
    if str(analysis_i) == 'Thermal':
        thermal.append(str(i))
    else:
        structural.append(str(i))

index = int(structural[-1]) #choose always the last index

#analysis_i = DataModel.GetObjectsByType(DataModelObjectCategory.Analysis)
#index = len(analysis_i)-1
static_structural = analyses_list[index]#Model.Analyses[2]

#**************************
#Add boundary conditions
#**************************
#Symmetry in Z
named_selection = DataModel.GetObjectsByName("Symm_Z")
bc_1 = static_structural.AddFrictionlessSupport()
bc_1.Location = named_selection[0]

#Fixed supports (nodes)
named_selection = DataModel.GetObjectsByName("BC_node")
bc_2 = static_structural.AddFixedSupport()
bc_2.Location = named_selection[0]

#******************************
#Add solutions
#******************************
named_selections = ['all','Cladding_ns','TZM_ns','W_ns']

#Elastic strain
named_selection = DataModel.GetObjectsByName("all")
equivalent_elastic_strain = static_structural.Solution.AddEquivalentElasticStrain()
equivalent_elastic_strain.ScopingMethod = GeometryDefineByType.Component
equivalent_elastic_strain.Location = named_selection[0]

#Von Mises stresses in each named_selection
for i in range(len(named_selections)):

    named_selection = DataModel.GetObjectsByName(named_selections[i])
    equivalent_sigma = static_structural.Solution.AddEquivalentStress()
    equivalent_sigma.ScopingMethod = GeometryDefineByType.Component
    equivalent_sigma.Location = named_selection[0]

#******************
#Solve the analysis
#********************
#static_structural.Solve()
