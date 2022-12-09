"""
Script to generate a complete LOCA simulation of BDF Target

Author: Ramiro Mena Andrade (CERN)
Date: 2020/03/18

email: ramiro.francisco.mena.andrade@cern.ch

"""
import os
import sys

#Folder location
cwd = 'F:/Simulations/BDF/LOCA_param/Scripts/01_target_blocks_v2/' #Define your own path where the files are stored

script_folder = cwd
user_files = cwd + 'user_files/'

#Append all the previously defined folders
sys.path.append(scripts_folder)
sys.path.append(user_files)

def loadCommand(cwd,filename):
    """
    function to read the DS_macro_file to get all the commands from a predefined Python script
    Inputs: cwd (string) path where the file is located
            filename (string) name of the script to be loaded (with .py)
    Output: DSScriptcommand
    """
    DSscript = open(cwd+filename, "r")
    DSscriptcommand=DSscript.read()
    DSscript.close()
    return DSscriptcommand

def execute_command(system, DSscriptcommand):
    """
    function to execute a script as a command
    Inputs: system (Ansys system) system where the script will be executed
            DSscriptcommand (script) script previously loeaded by loadCommand
    Output: None
    """
    # Send the command
    setup = system.GetContainer(ComponentName="Setup")
    setup.Edit(Interactive = True)
    setup.SendCommand(Language="Python", Command = DSscriptcommand)
    setup.Exit()
    return

def load_external_data(system_i, system_j, file_name, row, header, coord_sys=[0,0,0]):
    """
    Function to load a external data file
    Inputs: system_i (Ansys system setup) system where the data will be added
            system_j (Ansys system setup) system where the data will be trasferred
            file_name (string) name of the file, including the working directory and its extension '.csv
            row (int) starting row to read the data
            header (string) Name of the External Load Colum Data (e.g "X Coordinate", "Y Coordinate", "Z Coordinate", "Heat Generation")
            coord_sys (list): XYZ components of the Origin for the coordinate system (in m), [0,0,0] by default
    Outputs: externalLoadFileData
    
    """
    #From system_i, define setup_i
    setup_i = system_i.GetContainer(ComponentName="Setup")
    
    #From setup_i, load external data
    externalLoadFileData = setup_i.AddDataFile(FilePath=file_name)
    
    #Define the origin of the coordinate system
    externalLoadFileDataProperty = externalLoadFileData.GetDataProperty()
    externalLoadFileDataProperty.OriginX = coord_sys[0]
    externalLoadFileDataProperty.OriginY = coord_sys[1]
    externalLoadFileDataProperty.OriginZ = coord_sys[2]
    
    #Define the starting line
    externalLoadFileData.SetStartImportAtLine(
        FileDataProperty=externalLoadFileDataProperty,
        LineNumber=row)
    
    #Select the info available in the file
    for i in range(len(header)):
        if i==0:
            externalLoadColumnData_i = externalLoadFileDataProperty.GetColumnData(Name="ExternalLoadColumnData")
            externalLoadFileDataProperty.SetColumnDataType(
                ColumnData=externalLoadColumnData_i,
                DataType= header[i])
        else:
            externalLoadColumnData_i = externalLoadFileDataProperty.GetColumnData(Name="ExternalLoadColumnData "+str(i))
            externalLoadFileDataProperty.SetColumnDataType(
                ColumnData=externalLoadColumnData_i,
                DataType= header[i])
        
    #Update the external data
    setupComponent1 = system_i.GetComponent(Name="Setup")
    setupComponent1.Update(AllDependencies=True)
    
    #Transfer data from system_i to system_j
    setupComponent2 = system_j.GetComponent(Name="Setup")
    setupComponent1.TransferData(TargetComponent=setupComponent2)
        
    return externalLoadFileData

def sys_generation(system1, name_thermal_case, option=0):
    """
    Function to create a static structural system and a transient thermal analysis for decay heat
    Inputs: system1 (ANSYS system), where the previous information will be propagated
            name_thermal_case (string), name of the current decay heat
    Outputs: system2 (ANSYS static structural)
            system3 (ANSYS transient thermal)
    """
    
    #Generate the new Structural system
    template1 = GetTemplate(
        TemplateName="Static Structural",
        Solver="ANSYS")
    
    #system1 = GetSystem(Name="SYS")
    
    engineeringDataComponent1 = system1.GetComponent(Name="Engineering Data")
    geometryComponent1 = system1.GetComponent(Name="Geometry")
    modelComponent1 = system1.GetComponent(Name="Model")
    solutionComponent1 = system1.GetComponent(Name="Solution")
    componentTemplate1 = GetComponentTemplate(Name="SimulationSetupCellTemplate_StructuralStaticANSYS")
    
    #Locate the structural system at the right of system 1
    system2 = template1.CreateSystem(
        ComponentsToShare=[engineeringDataComponent1, geometryComponent1, modelComponent1],
        DataTransferFrom=[Set(FromComponent=solutionComponent1, TransferName=None, ToComponentTemplate=componentTemplate1)],
        Position="Right",
        RelativeTo=system1)
    
    if option == 1:
        return system2
    
    #Generate the new transient thermal
    template2 = GetTemplate(
        TemplateName="Transient Thermal",
        Solver="ANSYS")
    componentTemplate2 = GetComponentTemplate(Name="SimulationSetupCellTemplate_ThermalTransientANSYS")
    
    #Locate the transient therlal below the static structural
    system3 = template2.CreateSystem(
        ComponentsToShare=[engineeringDataComponent1, geometryComponent1, modelComponent1],
        DataTransferFrom=[Set(FromComponent=solutionComponent1, TransferName=None, ToComponentTemplate=componentTemplate2)],
        Position="Below",
        RelativeTo=system2)
    system3.DisplayText = name_thermal_case
    setupComponent1 = system2.GetComponent(Name="Setup")
    setupComponent1.UpdateUpstreamComponents()
    modelComponent1.Refresh()
    setupComponent1.Refresh()
    #setup1 = system2.GetContainer(ComponentName="Setup")

    return system2, system3

def solve_system(system, cwd, script_name):
    """
    Function to solve a system by using a script
    Inputs: system (ANSYS system)
            cwd (string) where the script is located
            script_name (string) name of the script to execute (with the extention .py)
    Outputs: none
    """
    # Upload the script
    filename = script_name
    DSscriptcommand = loadCommand(cwd,filename)
    execute_command(system, DSscriptcommand)
    return


#%%
#Scripts to be executed (names)
geometry_script          = '01_geometry_blocks.py'
mesh_script              = '02_mesh_blocks.py'
thermal_steady_script    = '03_thermal_steady_blocks.py' 
thermal_transient_script = '04_thermal_transient_blocks.py'
structural_steady_script = '05_static_structural_blocks.py'

#Fluka cases for LOCA (names)
fluka_case = ['10ms','30ms','100ms','300ms','1s','10s','60s','10m','30m','1h','2h','6h','1d','2d','4d','1w','2w','3w','1mo','2mo','3mo','1y','2y']

#External files used in the simulation
materials_library = user_files + 'BDF_materials.xml'
steady_energy_profile = user_files + 'HGEN_Cylin_circle50_8mm_ALL.csv'

#%%
#*******************************************
# System 1 & 2 : External data and steady state
#*******************************************
#Generate the external data (system1)
template1 = GetTemplate(TemplateName="External Data")
system1 = template1.CreateSystem()

#Generate the Steady state (system2)
template2 = GetTemplate(
    TemplateName="Steady-State Thermal",
    Solver="ANSYS")
system2 = template2.CreateSystem(
    Position="Right",
    RelativeTo=system1)

#Load the steady state Energy Deposition

header_heat_gen = ["Z Coordinate", "Y Coordinate", "X Coordinate", "Heat Generation"] #Header that defines the type of information to be imported
row=1 #starting row to extract the data
externalLoadData1 = load_external_data(system1, system2, steady_energy_profile, row, header_heat_gen, coord_sys=[5e-3,0,0])

#####################
#GEOMETRY GENERATION
######################

# Load the script
DSscriptcommand = loadCommand(cwd,geometry_script)

#Select the geometry
geometry2 = system2.GetContainer(ComponentName="Geometry")

#Execute the script
geometry2.Edit(IsSpaceClaimGeometry=True, Interactive=True)
geometry2.SendCommand(Language="Python", Command = DSscriptcommand)
geometry2.Exit()

# #Transfer data (to check)
modelComponent1 = system2.GetComponent(Name="Model")
setupComponent1 = system1.GetComponent(Name="Setup")
setupComponent2 = system2.GetComponent(Name="Setup")
# setupComponent1.TransferData(TargetComponent=setupComponent2)

#Update (all)
setupComponent1.Update(AllDependencies=True)
modelComponent1.Update(AllDependencies=True)

#Load the material library OK
favorites1 = EngData.LoadFavoriteItems()
library1 = EngData.OpenLibrary(Name="BDF_materials", Source=materials_library)
engineeringData1 = system2.GetContainer(ComponentName="Engineering Data")
matl1 = engineeringData1.ImportMaterial(Name="Tantalum Ta", Source=materials_library)
matl2 = engineeringData1.ImportMaterial(Name="Tungsteng W", Source=materials_library)
matl3 = engineeringData1.ImportMaterial(Name="TZM", Source=materials_library)
matl4 = engineeringData1.ImportMaterial(Name="Niobium Nb-10Hf-1Ti C103", Source=materials_library)
modelComponent1.Refresh()

####################
#MESH GENERATION
####################
#Load the script
DSscriptcommand = loadCommand(cwd,mesh_script)

# Select the system
setup2 = system2.GetContainer(ComponentName="Setup")

#Send the command
setup2.Edit(Interactive = True)
setup2.SendCommand(Language="Python", Command = DSscriptcommand)
setup2.Exit()

##############################
#STEADY THERMAL SIMULATION
##############################
# Load the script
DSscriptcommand = loadCommand(cwd,thermal_steady_script)

# Select the system
setup2 = system2.GetContainer(ComponentName="Setup")

# Send the command
setup2.Edit(Interactive = True)
setup2.SendCommand(Language="Python", Command = DSscriptcommand)
setup2.Exit()

#*****************************************
#System generation loop
#******************************************
for i in range(2):#len(fluka_case)): #This loop can be modified to test short cases during debugging 
    if i==0:
        system_temp = system2
    else:
        system_temp = system_j
        
    system_i, system_j = sys_generation(system_temp, 'Decay_heat_' + fluka_case[i])
    solve_system(system_i, cwd,structural_steady_script)
    solve_system(system_j, cwd,thermal_transient_script)

#last step
system_n = sys_generation(system_j, 'none', option=1)
solve_system(system_n, cwd,structural_steady_script)


