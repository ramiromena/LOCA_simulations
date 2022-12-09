"""
Script for running a thermal transient block
Author: Ramiro Mena-Andrade (CERN-CIEMAT)
Data: 2022/05/10

Comments: 
    - The script uses the Fluka plug-in for loading the energy deposition
    - The location of the Fluka files (.lis) needs to be modified manually (if different files are applied)
    - For comparison between cladding candidates a constant h=1 W/m2K is used (option=0)
    
Manual operations:
    - The Fluka plugin does not allow to automatize two actions: application of the load and time
"""

#%%
import sys
import os
sys.path.append('C://Program Files//Ansys Inc//v202//Addins//')

def Temperature_FilmCoefficient_values(T,k,L):
    T_list = []
    h_list = []
    for i in range(len(T)):
        T_list.append(Quantity(str(T[i])+'[s]'))
        h_list.append(Quantity(str(k_air[i]/L) + '[W m^-1 m^-1 C^-1]'))
    return T_list, h_list


#Type of simulation

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

index = int(thermal[-1]) #choose always the last index
print('Transient thermal index', index)

#analysis_i = DataModel.GetObjectsByType(DataModelObjectCategory.Analysis)#DataModel.GetObjectsByName("Transient Thermal")
#index = len(analysis_i)-2
decay_heat = analyses_list[index]#Model.Analyses[1]
option = 0 #0 for htc=1, 1 for htc=f(T)

fluka_index = int((index/2-1)) #a factor of 0.5 is included to take into account the presence of the steady state structural case

#fluka_files_wd = r'F://Simulations//BDF//LOCA//Accidental_scenario_natural_convection//Natural_Convection_LIS//'
#fluka_files_wd = r'G:/Departments/SY/Groups/STI/TCD/0050-Global_Projects/BDF Target Complex/BDF Target simulations/Solid target/FLUKA/lis_Nb_toRamiro/'
#fluka_files_wd = r'G:/Departments/SY/Groups/STI/TCD/0050-Global_Projects/BDF Target Complex/BDF Target simulations/Solid target/FLUKA/lis_Ta_toRamiro/lis_Ta_toRamiro/'
#fluka_files_wd = r'G:/Departments/SY/Groups/STI/TCD/0050-Global_Projects/BDF Target Complex/BDF Target simulations/Solid target/FLUKA/lis_NbZr_toRamiro/'
fluka_files_wd = r'G:/Departments/SY/Groups/STI/TCD/0050-Global_Projects/BDF Target Complex/BDF Target simulations/Solid target/FLUKA/lis_NbHfTi_toRamiro/'

fluka_case = ['10ms','30ms','100ms','300ms','1s','10s','60s','10m','30m','1h','2h','6h','1d','2d','4d','1w','2w','3w','1mo','2mo','3mo','1y','2y']
fluka_time = [10e-3, 30e-3, 100e-3, 300e-3, 1, 10, 60, 10*60, 30*60, 60**2, 2*60**2, 6*60**2, 24*60**2, 2*24*60**2, 4*24*60**2, 7*24*60**2, 14*24*60**2, 21*24*60**2, 31*24*60**2, 61*24*60**2,92*24*60**2, 365*24*60**2, 2*365*24*60**2]

#Create a list with the available fluka number case ID (see readmeFile)
fluka_number_case=[]

for i in range(39,45):
    fluka_number_case.append(str(i))
    
for i in range(22,39):
    fluka_number_case.append(str(i))

file_name='EnDep_NbHfTi_usrbin_'+ fluka_number_case[fluka_index]
file_ext = '.bnn.lis'
file_to_load = fluka_files_wd + file_name + file_ext

#Scrip to generate the decay heat blocks
#Air data taken from Icropera 2007
T_air = [26.85, 76.85, 126.85, 176.85, 226.85, 276.85, 326.85, 376.85, 426.85, 476.85, 526.85, 576.85, 626.85, 676.85, 726.85, 826.85, 926.85, 1026.85, 1126.85, 1226.85, 1326.85, 1426.85, 1526.85, 1626.85, 1726.85, 1826.85, 1926.85, 2026.85, 2126.85, 2226.85, 2726.85]
k_air = [0.0263,0.03,0.0338,0.0373,0.0407,0.0439,0.0469,0.0497,0.0524,0.0549,0.0573,0.0596,0.062,0.0643,0.0667,0.0715,0.0763,0.082,0.091,0.1,0.106,0.113,0.12,0.128,0.137,0.147,0.16,0.175,0.196,0.222,0.486]
L = 5e-3 #BDF channel

#Beam properties for decay heat
ppp =1 #Protons per pulse (Intensity)
pulseTime=1 #Seconds
tableName = r'load_tab'

#************************
#Thermal loads
#************************
#Define Analysis Settings time
if fluka_index == 0:
    decay_heat.AnalysisSettings.StepEndTime = Quantity(fluka_time[fluka_index], "sec")
else:
    decay_heat.AnalysisSettings.StepEndTime = Quantity(fluka_time[fluka_index]-fluka_time[fluka_index-1], "sec")
    
#Convection Load during decay heat
T_list, h_list = Temperature_FilmCoefficient_values(T_air,k_air,L) #Define the temperature and film coefficient values with a function
named_selection = DataModel.GetObjectsByName("Convection_vertical_faces") #Select the vertical faces
convection_1 = decay_heat.AddConvection() #Add convection load
convection_1.Location = named_selection[0] #Assign the selected geometry
#Select the constant or variable h value
if option == 0:
    convection_1.FilmCoefficient.Output.SetDiscreteValue(0, Quantity(1, "W m^-1 m^-1 C^-1"))
else:
    convection_1.FilmCoefficient.Inputs[0].DiscreteValues = T_list #Populate the table with T_list
    convection_1.IndependentVariable = LoadVariableVariationType.Temperature #Define temperature as the independent variable
    convection_1.FilmCoefficient.Output.DiscreteValues = h_list #Populate the table with h_list
convection_1.AmbientTemperature.Output.SetDiscreteValue(0, Quantity(26.85, "C")) #Set the ambient temperature

#Load Table FlukaV1_Beta
user_load_1= decay_heat.CreateLoadObject('CustomObj1',"FlukaV1_Beta") #Create the table
user_load_1.Properties['TbData/Filedir'].Value = file_to_load #File to load (defined on top)
user_load_1.Properties['TbData/TableName'].Value = tableName #Given name to the load
user_load_1.Properties['TbData/ApplyTable'].Value = 'applied' # Load Table
user_load_1.Properties['Inputs/ARG1'].Value = ppp #Intesity
user_load_1.Properties['Inputs/ARG2'].Value = pulseTime #Pulse Time
temp_prop = user_load_1.Properties['Options/target']
temp_prop.Value = temp_prop.Options[1] #Applied on Elements
temp_prop = user_load_1.Properties['Options/target/targetdetail']
temp_prop.Value = temp_prop.Options[1]#Average on ElementCenter
temp_prop = user_load_1.Properties['TbData/SYC']#Coordinate system
temp_prop.Value = temp_prop.Options[1]
temp_prop = user_load_1.Properties['Definition/TypeAnalysis']#WB
temp_prop.Value = temp_prop.Options[0]
temp_prop = user_load_1.Properties['GeometrySelection/Geometry/DefineBy']
temp_prop.Value = temp_prop.Options[1]
#temp_prop = user_load_1.Properties['GeometrySelection/Geometry/DefineBy/NamedSelection'] #NOT WORKING to test
#temp_prop.Value = temp_prop.Options[13]
temp_prop = user_load_1.Properties['Outputs/Output1']#Check Ansys ON
temp_prop.Value = temp_prop.Options[0]
temp_prop = user_load_1.Properties['Outputs/Output2']#Check Fluka file ON
temp_prop.Value = temp_prop.Options[0]


# named_selection = DataModel.GetObjectsByName('all')
# temperature_result_1 = decay_heat.Solution.AddTemperature()
# temperature_result_1.ScopingMethod = GeometryDefineByType.Geometry
# temperature_result_1.Location= named_selection[0]
# #endregion

named_selections = ['all','Cladding_ns','TZM_ns','W_ns']

#Create the Temperature output solution
for i in range(len(named_selections)):
    named_selection = DataModel.GetObjectsByName(named_selections[i])
    temperature_result_i = decay_heat.Solution.AddTemperature()
    temperature_result_i.ScopingMethod = GeometryDefineByType.Geometry
    temperature_result_i.Location= named_selection[0]
    
    if i == 0:
        temperature_result_i = decay_heat.Solution.AddTotalHeatFlux()
        temperature_result_i.ScopingMethod = GeometryDefineByType.Geometry
        temperature_result_i.Location= named_selection[0]

#region Set object property
#named_selection = DataModel.GetObjectsByName("Path 1")
#path_1 = named_selection[0]
#temperature_result_1 = Model.Analyses[2].Solution.AddTemperature()
#temperature_result_1.ScopingMethod = GeometryDefineByType.Path
#temperature_result_1.Surface = named_selection[0]
#endregion

#region Set object property
#named_selection = DataModel.GetObjectsByName("Path 2")
#path_2 = named_selection[0]
#temperature_result_2 = Model.Analyses[2].Solution.AddTemperature()
#temperature_result_2.ScopingMethod = GeometryDefineByType.Path
#temperature_result_2.Surface = named_selection[0]
#endregion

#***********************
#Run Analysis
#***********************
#Model.Analyses[2].Solve()


