#Script to mesh the blocks of BDF

#************************
#Inputs
#************************

#Setup disk (name of the regions and mesh size)
name_1=[1,2,3]
size_1=[3,25,25]

#setup blocks
name_2=[25,50,65,80,100,200,350]

gral_mesh = 5
L=5e-3
num_points=99

#*******************
#Coordinate system
#*******************
#AddCoordinate system
coordinate_system_1 = Model.CoordinateSystems.AddCoordinateSystem()
coordinate_system_1.CoordinateSystemType = Ansys.ACT.Interfaces.Analysis.CoordinateSystemTypeEnum.Cylindrical
coordinate_system_1.OriginDefineBy = CoordinateSystemAlignmentType.Fixed
coordinate_system_1.PrimaryAxis = CoordinateSystemAxisType.PositiveZAxis
coordinate_system_1.OriginX = Quantity(-1*L, "m")
#endregion

#************************
#Construction Geometry
#***********************
#Create the construction geometry object
construction_geometry_1= Model.AddConstructionGeometry()

#region Set object property
path_1 = construction_geometry_1.AddPath()
path_1.EndXCoordinate = Quantity(1.5, "m")
path_1.Name = 'Path 1'
path_1.NumberOfSamplingPoints = num_points

path_2 = construction_geometry_1.AddPath()
path_2.StartYCoordinate = Quantity(50E-3, "m")
path_2.EndXCoordinate = Quantity(1.5, "m")
path_2.EndYCoordinate = Quantity(50E-3, "m")
path_2.Name = 'Path 2'
path_2.NumberOfSamplingPoints = num_points
#endregion

#***********************************
#Processing
#***********************************
#Define mesh variable
mesh_1=Model.Mesh

#Clean the available mesh data
mesh_1.ClearGeneratedData()

#Choose mesh type
mesh_1.PhysicsPreference=MeshPhysicsPreferenceType.Mechanical

#Element size general
mesh_1.ElementSize = Quantity(gral_mesh*1e-3, "m")

#Add MeshSizing and Set object property
for i in range(len(name_1)):
    named_selection=DataModel.GetObjectsByName("mesh_L_"+str(name_1[i]))
    mesh=Model.Mesh.AddSizing()
    mesh.Location=named_selection[0]
    mesh.Type = SizingType.NumberOfDivisions
    mesh.NumberOfDivisions = int(size_1[i])
    mesh.Behavior = SizingBehavior.Hard
#endregion

#Add MeshSizing and Set object property
for i in range(len(name_2)):
    named_selection=DataModel.GetObjectsByName("mesh_L_"+str(name_2[i]))
    mesh=Model.Mesh.AddSizing()
    mesh.Location=named_selection[0]
    mesh.Type = SizingType.ElementSize
    mesh.ElementSize = Quantity(gral_mesh*1e-3, "m") #(int(name_2[i])/10)*1
    mesh.Behavior = SizingBehavior.Hard
#endregion

#Mesh generation
mesh_1.GenerateMesh()

