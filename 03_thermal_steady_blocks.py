#Script to mesh the blocks of BDF

#Model analysis selection
thermal_analysis = Model.Analyses[0]

#named_selection = ['TZM','W','Ta']

#*************************
#Material assignment
#**************************
#Material assignment TZM
named_selection = DataModel.GetObjectsByName("TZM_ns")
material_assignment_1=Model.Materials.AddMaterialAssignment()
material_assignment_1.Name = 'TZM Assignment'
material_assignment_1.Location=named_selection[0]
material_assignment_1.Material = 'TZM'

#Material assignment Tungsten W
named_selection = DataModel.GetObjectsByName("W_ns")
material_assignment_2=Model.Materials.AddMaterialAssignment()
material_assignment_2.Name = 'W Assignment'
material_assignment_2.Location=named_selection[0]
material_assignment_2.Material = 'Tungsteng W'

#Material assignment for the cladding
named_selection = DataModel.GetObjectsByName("Cladding_ns")
material_assignment_3=Model.Materials.AddMaterialAssignment()
material_assignment_3.Name = 'Nb-C103 Assignment'
material_assignment_3.Location=named_selection[0]
material_assignment_3.Material = 'Niobium Nb-10Hf-1Ti C103'

#************************
#Thermal loads
#************************
#Initial Temperature
initial_condition_1 = thermal_analysis.Children[0]
initial_condition_1.InitialTemperatureValue = Quantity(26.85, "C")

#Convection
named_selection = DataModel.GetObjectsByName("Convection_vertical_faces")
convection_1 = thermal_analysis.AddConvection() #Add convection load
convection_1.Location = named_selection[0]
convection_1.FilmCoefficient.Output.SetDiscreteValue(0, Quantity(20E3, "W m^-1 m^-1 C^-1"))
convection_1.AmbientTemperature.Output.SetDiscreteValue(0, Quantity(26.85, "C"))

#FSI interaction
named_selection = DataModel.GetObjectsByName("Convection_vertical_faces")
fluid_solid_interface_1 = thermal_analysis.AddFluidSolidInterface() #Add FSI interface
fluid_solid_interface_1.Location=named_selection[0]
fluid_solid_interface_1.ExportResults = True

#FSI interaction
named_selection = DataModel.GetObjectsByName("Convection_horizontal_faces")
fluid_solid_interface_2 = thermal_analysis.AddFluidSolidInterface() #Add FSI interface
fluid_solid_interface_2.Location=named_selection[0]
fluid_solid_interface_2.ExportResults = True

#Radiation
#named_selection = DataModel.GetObjectsByName("Convection_vertical_faces")
#radiation_1 = thermal_analysis.AddRadiation() #Add radiation load
#radiation_1.Location = named_selection[0]
#radiation_1.Correlation = RadiationType.SurfaceToSurface
#radiation_1.Emissivity.Output.SetDiscreteValue(0,Quantity(0.9, ""))

#Imported load (Fluka) #CHECK!!!!!!!!!!!
# named_selection = DataModel.GetObjectsByName("all")
# imported_load_1 = thermal_analysis.Children[6].AddImportedHeat()#Ansys.ACT.Automation.Mechanical.ImportedLoads.AddImported
# imported_load_1.ScopingMethod = GeometryDefineByType.Component
# imported_load_1.Location = named_selection[0]

#***********************
#Outputs definition
#***********************

named_selections = ['all','Cladding_ns','TZM_ns','W_ns']

#Create the Temperature output solution
for i in range(len(named_selections)):
    named_selection = DataModel.GetObjectsByName(named_selections[i])
    temperature_result_i = thermal_analysis.Solution.AddTemperature()
    temperature_result_i.ScopingMethod = GeometryDefineByType.Geometry
    temperature_result_i.Location= named_selection[0]
    
    if i == 0:
        temperature_result_i = thermal_analysis.Solution.AddTotalHeatFlux()
        temperature_result_i.ScopingMethod = GeometryDefineByType.Geometry
        temperature_result_i.Location= named_selection[0]

# #Temperature results
# named_selection = DataModel.GetObjectsByName("all")
# temperature_result_1 = thermal_analysis.Solution.AddTemperature()
# temperature_result_1.ScopingMethod = GeometryDefineByType.Component
# temperature_result_1.Location=named_selection[0]

# #Temperature results 2
# named_selection = DataModel.GetObjectsByName("Symm_Z")
# temperature_result_2 = thermal_analysis.Solution.AddTemperature()
# temperature_result_2.ScopingMethod = GeometryDefineByType.Component
# temperature_result_2.Location=named_selection[0]

# #Heat flux results
# named_selection = DataModel.GetObjectsByName("all")
# heat_flux_result = thermal_analysis.Solution.AddTotalHeatFlux()
# heat_flux_result.ScopingMethod = GeometryDefineByType.Component
# heat_flux_result.Location=named_selection[0]

#***********************
#Run Analysis
#***********************
#Model.Solve()




