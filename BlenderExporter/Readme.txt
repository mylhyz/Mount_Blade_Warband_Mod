This file shows how to use Mount & Blade animation exporter for Blender 2.49b

--------------------------------------------------------------------
STARTING

"MB_TRF_Exporter.py" must be in the same folder with .blend file. Or
But if you think Blender not able to find exporter files, copy this file: "MB_TRF_Exporter.py" to this location:
# Windows XP: C:\Program Files\Blender Foundation\Blender\.blender\scripts
# Windows XP (alt): C:\Documents and Settings\USERNAME\Application Data\Blender Foundation\Blender\.blender\scripts
# Windows Vista: C:\Users\USERNAME\AppData\Roaming\Blender Foundation\Blender\.blender\scripts


--------------------------------------------------------------------
CREATING ANIMATIONs

Before starting read these two rules:
-Don't edit skeletons in edit mode. If you edit output animations will be broken for the game.
-Scaling does not effect output animation, so you may prefer not using it.

1- Open action panel
2- Press the button to add a new action and enter it's name
3- Select skeleton in object mode and then open pose mode.
4- Select all of the bones. You can do that with 'A' key.
5- Be sure you are at first frame of action, make your pose.
   Than press 'I' on 3D View panel and select Rot or LocRot
   Exporter needs rotation values of ipo curves. So you need to choose Rot or LocRot.
6- Complete animation.
7- IpoCurve names of bones must be in "action_name.bone_name" format.
   Open Ipo-Curve Edıtor and Action Panel at same time.
   Select Pose Mode from Ipo-Curve Editor.
   Select a bone from action editor, you will see it's ipo curve name at ipo-curve editor.
   Rename ipo curve name to action_name.bone_name
   Repeat this for all bones.
   Example:
	Bone Name: Tail
	Action Name: Jump
	IpoCurve Name: Jump.Tail


--------------------------------------------------------------------
ANIMATION EXPORTING

1- Open text editor.
2- Select "M&B animation.py"
3- Change SKELETON_TYPE to skel_human for exporting human animation
   Change SKELETON_TYPE to skel_horse for exporting horse animation
4- Change ANIMATION_NAME to your action's name.
   ANIMATION_NAME will be used at in game.
5- Change PATH to output location. Use ".trf" extension at file name.
6- Before running script make sure you selected right skeleton in 3d view panel and right action in action panel.
7- In text editor, select Text->Run Python Script or press ALT+P.
8- Now you have your animation in trf format.
9- Example script:

from TRF_Animation_Exporter import *
exporter  = Exporter()
skel_horse = Skeleton("skel_horse","anim_horse")
exporter.open("C:/animation_horse.trf")
exporter.write_skeleton_anims()
exporter.file.write("\nend\n")
exporter.close()
print "finished."


--------------------------------------------------------------------
MESH EXPORTING

1- Open text editor.
2- Select "M&B mesh.py"
3- You need to change MESH_NAME and PATH
3- MESH_NAME is name of mesh which will be exported
4- PATH is the path of output file, can be in "C:/output.trf" format.
5- usage of SKELETON_NAME, AUTOSMOOTH are optional.
6- If mesh is rigged, write name of skeleton to SKELETON_NAME
   If mesh is not rigged, you can write "" to SKELETON_NAME Area (Make it empty)
8- AUTOSMOOTH will be 120 if you don't enter anything to there.
9- In text editor, select Text-Run Python Script or press ALT+P.
10- Output trf file must be at desired location.
11- Example script:

from TRF_Animation_Exporter import *
exporter  = Exporter()
exporter.add_mesh(Mesh_obj("armor1"))
exporter.add_mesh(Mesh_obj("armor2","",0,90))
exporter.add_mesh(Mesh_obj("armor3","skel_human",0,120))
exporter.open("C:/armor_meshes.trf")
print ("exporting " + exporter.file_name)
exporter.write_meshes()
exporter.file.write("\nend\n")
exporter.close()
print "finished."


--------------------------------------------------------------------
BODY EXPORTING

1- While you are creating physics bodies, you can use icosphere and cylinder.
   Make sure you don't edit them in edit mode. You have to use scale, grab, rotate at object mode.
   Because you can do everything to sphere and cylinder in object mode, exporter will not export edit mode  changes for bodies.
   When you view transformation information (N key), all scale values of icosphere must be same.

2- You must name body names in that format:
   For spheres use names which start with   "s." and follow with mesh's name
   For cylinders use names which start with "c." and follow with mesh's name
   For manifolds use names which start with "m." and follow with mesh's name

   Example naming:
   If we created a sphere for mesh "IRON_WALL" than name will be: "s.IRON_WALL"
   It can be "s.IRON_WALL.001" and etc. But must start with "s.IRON_WALL"
   At end when you start body exporting, exporter will recognize them.

3- To export bodies you must use:    exporter.add_body("MESH_NAME")
   This will search for objects which starting with "s.MESH_NAME", "c.MESH_NAME", "m.MESH_NAME".
   
   Than at the end of script:    exporter.write_bodies()
   will export body information to TRF file.

4- Example script:

from TRF_Animation_Exporter import *
exporter  = Exporter()

exporter.add_body("pole")

exporter.add_body("chair")

exporter.open("C:/bodies.trf")
print ("exporting " + exporter.file_name)
exporter.write_meshes()
exporter.write_bodies()
exporter.file.write("\nend\n")
exporter.close()
print "finished."


--------------------------------------------------------------------
INFORMATION ABOUT TRF FILES

Mount&Blade can use two types of files: .trf and .brf
And these two files being used in the same way.
M&B looks to creation time of trf and brf files. 
If you have two files with names X.trf and X.brf, trf file only being used if it's creation time more closer to current time.
If you put a .trf file to resource folders of M&B, it will be converted to .brf files while game in loading stage.

And of course you need to add file's name to "module.ini".
If you have X.trf, you must add "load_resource = X" to "module.ini". Than game can search for X.trf or X.brf in resource folder.

So step by step explanation is here:
1-) Create your "NAME.trf" file
2-) Copy it to CommonRes folder of Mount&Blade or Resource folder of your Module.
3-) Open module.ini of your module.
4-) If you copied trf file to CommonRes, add "load_resource = NAME" to file "module.ini"
5-) If you copied trf file to Resource folder of module, add "load_mod_resource = NAME" to file "module.ini"
6-) When you start game, file "NAME.trf" will be converted to "NAME.brf" in loading stage, and available to use immediately.

Note: If you have two files with names "NAME.trf" and "NAME.brf", game can overwrite to "NAME.brf". So copy your brf files if you need them.


--------------------------------------------------------------------
IMPORTING ( About Coordinate Spaces)

If you look to project of skeletons, skel_human and skel_horse looking to y+ axis. 
When you import meshes, if they don't look to y+ axis, don't turn them in object mode. 
Because if you change their values in object mode, their coordinate space being changed too.
Mesh's coordinate space must be same with blender's world coordinate space.
So instead of making changes in object mode, rotate/scale/grab them in edit mode. So their coordinate space can stay same with skeletons and blender.

