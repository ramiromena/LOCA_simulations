# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 11:07:39 2021

@author: rmenaand

Python Script to define the BDF blocks
"""

# Python Script, API Version = V19

#*************************************
#Functions
#*************************************

#Function to generate one single block
def BDF_single_block(pointA, pointB, pointC, sweepAngle, j):
    # Set Sketch Plane
    sectionPlane = Plane.PlaneXY
    result = ViewHelper.SetSketchPlane(sectionPlane, None)
    # EndBlock

    # Set New Sketch
    result = SketchHelper.StartConstraintSketching()
    # EndBlock

    # Sketch Rectangle
    point1 = Point2D.Create(MM(pointA[0]),MM(pointA[1]))
    point2 = Point2D.Create(MM(pointB[0]),MM(pointB[1]))
    point3 = Point2D.Create(MM(pointC[0]),MM(pointC[1]))
    result = SketchRectangle.Create(point1, point2, point3)

    # Solidify Sketch
    mode = InteractionMode.Solid
    result = ViewHelper.SetViewMode(mode, None)
    # EndBlock

    # Revolve 1 Face
    selection = FaceSelection.Create(GetRootPart().Bodies[j].Faces[0])
    axisSelection = Selection.Create(GetRootPart().CoordinateSystems[0].Axes[0])
    axis = RevolveFaces.GetAxisFromSelection(selection, axisSelection)
    options = RevolveFaceOptions()
    options.ExtrudeType = ExtrudeType.ForceIndependent
    result = RevolveFaces.Execute(selection, axis, DEG(sweepAngle), options)
    # EndBlock

#Function to generate all BDF blocks
def BDF_block_generator(blockDiameter, blockThickness, claddingThickness, position, sweepAngle, iterator):

    #*********************
    #Cladding plate 1
    #**********************
    pointA1 = [0,0]
    pointA2 = [claddingThickness,0]
    pointA3 = [claddingThickness,blockDiameter]

    BDF_single_block(pointA1, pointA2, pointA3, sweepAngle, 0)
    
    #******************************
    #Cladding plate 2
    #*******************************
    pointB1 = [claddingThickness,blockDiameter-claddingThickness]
    pointB2 = [blockThickness-claddingThickness,blockDiameter-claddingThickness]
    pointB3 = [blockThickness-claddingThickness,blockDiameter]

    BDF_single_block(pointB1, pointB2, pointB3, sweepAngle, 1)

    #******************************
    #Cladding plate 3
    #*******************************
    pointC1 = [blockThickness-claddingThickness,0]
    pointC2 = [blockThickness,0]
    pointC3 = [blockThickness,blockDiameter]

    BDF_single_block(pointC1, pointC2, pointC3, sweepAngle, 2)
    
    #******************************
    #Solid block
    #*******************************
    # Sketch Rectangle
    pointD1 = [claddingThickness,0]
    pointD2 = [blockThickness-claddingThickness,0]
    pointD3 = [blockThickness-claddingThickness,blockDiameter-claddingThickness]
    
    BDF_single_block(pointD1, pointD2, pointD3, sweepAngle, 3)
    
    #******************************
    #Make Component and tran
    #*******************************

    # Make Components
    selection = BodySelection.Create(GetRootPart().Bodies[:])
    result = ComponentHelper.MoveBodiesToComponent(selection, None)
    # EndBlock
   
    # Final location
    # Translate Along X Handle
    selection = BodySelection.Create(GetRootPart().Components[iterator].Content.Bodies[:])
    direction = Direction.DirX
    options = MoveOptions()
    result = Move.Translate(selection, direction, MM(position), options)
    # EndBlock
    
#Function to select single edges
def BDF_edge_selection(component_id, body_id, edge_id, name_id):
    primarySelection = PowerSelection.Edges.ByLength(Selection.Create(GetRootPart().Components[component_id].Content.Bodies[body_id].Edges[edge_id]),
        PowerSelectOptions(True), 
        SearchCriteria.SizeComparison.Equal) 
    secondarySelection = Selection()
    result = NamedSelection.Create(primarySelection, secondarySelection)
    result = NamedSelection.Rename("Group1", "mesh_L_"+str(name_id))

#*************************************
#Geometry definition
#*************************************
ChannelWidth=180
ChannelThickness=5
blockDiameter = 125
claddingThickness=1.5
sweepAngle=-180

#Blocks diameters and distribution
blocks_length = [25,50,65,80,100,200,350]
blocks_dist = [3,0,0,0,0,0,0,0,1,1,2,3,3,1,3,4,5,6]
BDF_length = [ChannelThickness]
components_id=[1,8,10,0,15,16,17] #unique distribution (for meshing)
material_dist=[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1]  #0 for TZM, 1 for W

loop_control = len(blocks_dist)

#Define the blocks distribution and length
for i in range(len(blocks_dist)):
    #print('block',i,blocks_length[blocks_dist[i]])
    BDF_length.append(BDF_length[i]+blocks_length[blocks_dist[i]]+ChannelThickness)

#Delete everything
while GetRootPart().Components.Count > 0:
   GetRootPart().Components[0].Delete()
while GetRootPart().Bodies.Count > 0:
   GetRootPart().Bodies[0].Delete()
while GetRootPart().Curves.Count > 0:
   GetRootPart().Curves[0].Delete()
    
#*************************************
#Geometry generation
#*************************************
    
#Loop to generate the geometry
for i in range(loop_control):
    BDF_block_generator(blockDiameter,blocks_length[blocks_dist[i]],claddingThickness,BDF_length[i],sweepAngle,i)

# Slice Body by Faces
for i in range(loop_control):
    selection = BodySelection.Create([
        GetRootPart().Components[i].Content.Bodies[0],
        GetRootPart().Components[i].Content.Bodies[2]])
    toolFaces = FaceSelection.Create(GetRootPart().Components[i].Content.Bodies[1].Faces[0])
    result = SplitBody.ByCutter(selection, toolFaces, True)
# EndBlock

#**************************************
#Create groups
#***************************************
#Initialize the variables
sel_all=BodySelection.Empty()
sel_vface = FaceSelection.Empty()
sel_hface = FaceSelection.Empty()
sel_SymmZ = FaceSelection.Empty()

#Loop for selecting the bodies
for i in range(loop_control):
    temp_all = BodySelection.Create(GetRootPart().Components[i].Content.Bodies[:])
    
    temp_vf= FaceSelection.Create([
        GetRootPart().Components[i].Content.Bodies[0].Faces[1],
        GetRootPart().Components[i].Content.Bodies[2].Faces[3],
        GetRootPart().Components[i].Content.Bodies[4].Faces[2],
        GetRootPart().Components[i].Content.Bodies[5].Faces[5]])
    temp_hf= FaceSelection.Create([
        GetRootPart().Components[i].Content.Bodies[1].Faces[2],
        GetRootPart().Components[i].Content.Bodies[4].Faces[0],
        GetRootPart().Components[i].Content.Bodies[5].Faces[0]])
    temp_sz= FaceSelection.Create([
        GetRootPart().Components[i].Content.Bodies[0].Faces[2],
        GetRootPart().Components[i].Content.Bodies[1].Faces[4],
        GetRootPart().Components[i].Content.Bodies[1].Faces[5],
        GetRootPart().Components[i].Content.Bodies[2].Faces[2],
        GetRootPart().Components[i].Content.Bodies[3].Faces[3],
        GetRootPart().Components[i].Content.Bodies[4].Faces[3],
        GetRootPart().Components[i].Content.Bodies[4].Faces[4],
        GetRootPart().Components[i].Content.Bodies[5].Faces[3],
        GetRootPart().Components[i].Content.Bodies[5].Faces[4]])
       
    sel_all = sel_all + temp_all
    sel_vface = sel_vface + temp_vf
    sel_hface = sel_hface + temp_hf
    sel_SymmZ = sel_SymmZ + temp_sz

#Create groups to assign material and boundary conditions
sel_vface.CreateAGroup('Convection_vertical_faces')
sel_hface.CreateAGroup('Convection_horizontal_faces')
sel_SymmZ.CreateAGroup('Symm_Z')

# Create Datum Plane Y
selection = Selection.Create(GetRootPart().CoordinateSystems[0].Axes[1])
result = DatumPlaneCreator.Create(selection, False, None)
# EndBlock

# Create Datum Plane Z
selection = Selection.Create(GetRootPart().CoordinateSystems[0].Axes[2])
result = DatumPlaneCreator.Create(selection, False, None)
# EndBlock

# Translate Along Z Handle
selection = Selection.Create(GetRootPart().DatumPlanes[1])
direction = Move.GetDirection(selection)
options = MoveOptions()
result = Move.Translate(selection, direction, MM(-0.5*ChannelWidth), options, None)
# EndBlock

# Slice Bodies by Planes Y and Z
datum = Selection.Create(GetRootPart().DatumPlanes[:])
result = SplitBody.ByCutter(sel_all, datum, None)
# EndBlock

# Create Named Selection Group (L_cladding)
primarySelection = PowerSelection.Edges.ByLength(Selection.Create(GetRootPart().Components[0].Content.Bodies[4].Edges[3]),
    PowerSelectOptions(True), 
    SearchCriteria.SizeComparison.Equal) + PowerSelection.Edges.ByLength(Selection.Create(GetRootPart().Components[0].Content.Bodies[20].Edges[7]),
    PowerSelectOptions(True), 
    SearchCriteria.SizeComparison.Equal)
secondarySelection = Selection()
result = NamedSelection.Create(primarySelection, secondarySelection)
result = NamedSelection.Rename("Group1", "mesh_L_1")
# EndBlock

# Create Named Selection Group (L_Radius)
primarySelection = PowerSelection.Edges.ByLength(Selection.Create(GetRootPart().Components[0].Content.Bodies[7].Edges[0]),
    PowerSelectOptions(True), 
    SearchCriteria.SizeComparison.Equal) + PowerSelection.Edges.ByLength(Selection.Create(GetRootPart().Components[0].Content.Bodies[8].Edges[1]),
    PowerSelectOptions(True), 
    SearchCriteria.SizeComparison.Equal) + PowerSelection.Edges.ByLength(Selection.Create(GetRootPart().Components[0].Content.Bodies[8].Edges[9]),
    PowerSelectOptions(True), 
    SearchCriteria.SizeComparison.Equal) + PowerSelection.Edges.ByLength(Selection.Create(GetRootPart().Components[0].Content.Bodies[20].Edges[2]),
    PowerSelectOptions(True), 
    SearchCriteria.SizeComparison.Equal) 
secondarySelection = Selection()
result = NamedSelection.Create(primarySelection, secondarySelection)
result = NamedSelection.Rename("Group1", "mesh_L_2")
# EndBlock

# Create Named Selection Group (L_top_arc)
primarySelection = PowerSelection.Edges.ByLength(Selection.Create(GetRootPart().Components[0].Content.Bodies[8].Edges[3]),
    PowerSelectOptions(True), 
    SearchCriteria.SizeComparison.Equal) + PowerSelection.Edges.ByLength(Selection.Create(GetRootPart().Components[0].Content.Bodies[8].Edges[6]),
    PowerSelectOptions(True), 
    SearchCriteria.SizeComparison.Equal) 
secondarySelection = Selection()
result = NamedSelection.Create(primarySelection, secondarySelection)
result = NamedSelection.Rename("Group1", "mesh_L_3")
# EndBlock

# Create Named Selection Group (L_25)
for i in range(len(blocks_length)):
     BDF_edge_selection(components_id[i],1,2,blocks_length[i])
# EndBlock

#Groups for Cladding, TZM and W
#Initialize the variables
sel_all=BodySelection.Empty()
sel_clad=BodySelection.Empty()
sel_TZM=BodySelection.Empty()
sel_W=BodySelection.Empty()
sel_node = Selection.Empty()

#Loop for selecting the bodies
for i in range(loop_control):
    temp_clad = BodySelection.Create(GetRootPart().Components[i].Content.Bodies[:])
    temp_block = BodySelection.Create([
        GetRootPart().Components[i].Content.Bodies[3],
        GetRootPart().Components[i].Content.Bodies[15],
        GetRootPart().Components[i].Content.Bodies[16],
        GetRootPart().Components[i].Content.Bodies[17]])
    temp_node = Selection.Create(GetRootPart().Components[i].Content.Bodies[0].Edges[1].GetChildren[ICurvePoint]()[0])
    
    sel_all = sel_all + temp_clad
    sel_clad = sel_clad + temp_clad - temp_block
        
    if material_dist[i]==0:
        sel_TZM = sel_TZM + temp_block
    else:
        sel_W = sel_W + temp_block
    
    sel_node = sel_node + temp_node
    
#Create groups to assign material and boundary conditions
sel_all.CreateAGroup('all')
sel_clad.CreateAGroup('Cladding_ns')
sel_TZM.CreateAGroup('TZM_ns')
sel_W.CreateAGroup('W_ns')
sel_node.CreateAGroup('BC_node')

#*****************
# Share Topology
#*****************
# Share Topology
options = ShareTopologyOptions()
options.Tolerance = MM(0.1)
result = ShareTopology.FindAndFix(options)
# EndBlock


    
    