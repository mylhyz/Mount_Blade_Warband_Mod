import Blender
import string
import math

f_collision   = 0x0001
f_tex         = 0x0004
f_light       = 0x0010
f_shared      = 0x0040
f_tiles       = 0x0080
f_halo        = 0x0100
f_two_sided   = 0x0200
f_invisible   = 0x0400
f_obcolor     = 0x0800
f_billboard   = 0x1000
f_shadow      = 0x2000
f_text        = 0x4000

rgl_two_sided    = 0x0001
rgl_no_collision = 0x0002
rgl_no_shadow    = 0x0004

rgl_difficult  = 0x0100
rgl_unwalkable = 0x0200

def convert_face_flags(mode):
  flags = 0
  if not (mode & f_collision):
    flags |= rgl_no_collision
  if not (mode & f_shadow):
    flags |= rgl_no_shadow
  if (mode & f_two_sided):
    flags |= rgl_two_sided
  if (mode & f_shared):
    flags |= rgl_difficult
  if (mode & f_billboard):
    flags |= rgl_unwalkable
  return flags

def write_float(file,x):
  file.write("%f",x)

def writeln(file):
  file.write("\n")

def write_vec(file,v):
  file.write("%f %f %f "% (v[0],v[1],v[2]))

def writeln_vec(file,v):
  write_vec(file,v)
  writeln(file)

def write_orientation(file,frm):
  writeln_vec(file,frm[0])
  writeln_vec(file,frm[1])
  writeln_vec(file,frm[2])

def write_frame(file,frm):
  write_orientation(file,frm)
  writeln_vec(file,frm[3])


class Exporter:
  def __init__(self,optimize = 0):
    self.entities = []
    self.entity_names = []
    self.textures = []
    self.bodies = []
    self.complexes = []
    self.skeletons = []
    self.meshes = []
    self.sub_meshes = []
    self.optimize = optimize

  def open(self,file_name):
    self.file_name = file_name
    self.file = open(self.file_name, "w")

  def close(self):
    self.file.close()

  def add_texture(self,texture_name,flags = 0):
    found = 0
    for tex_rec in self.textures:
      if texture_name == tex_rec[0]:
        found = 1
    if not (found):
      self.textures.append((texture_name, flags))

  def add_mesh(self,mesh):
    if mesh in self.meshes:
      return
    self.meshes.append(mesh)
    for sub_mesh in mesh.sub_meshes:
      if self.optimize:
        num_misses1 = sub_mesh.count_cache_misses()
        sub_mesh.optimize()
        num_misses2 = sub_mesh.count_cache_misses()
        print "Num cache misses before:" + str(num_misses1) + " after:" + str(num_misses2)
      self.sub_meshes.append(sub_mesh)
    
  def add_skeleton(self,skeleton):
    if not (skeleton in self.skeletons):
      self.skeletons.append(skeleton)

  def write_manifold(self,mesh_name):
    if not mesh_name:
      self.file.write("0\n 0\n")
      print "Warning: no manifold assigned."
      return
    me = Blender.NMesh.GetRaw(mesh_name)
    if not me:
      print "Error: unable to find manifold " + mesh_name
      exit()
    self.file.write("%d\n"%len(me.verts))
    for v in me.verts:
      writeln_vec(self.file,v.co)
    self.file.write("%d\n"%len(me.faces))
    for f in me.faces:
      if (not f.image):
        print "Error face does not have image :"
        print "Coords: "
        for fv in f.v:
          print fv.co
      tag = f.mat
      self.file.write("  %d"%(tag))
      flags = convert_face_flags(f.mode)
      self.file.write(" %d "%(flags))
      self.file.write(" %d "%(len(f.v)))
      for fv in f.v:
        self.file.write(" %d "%(fv.index))
      self.file.write("\n")

  def write_textures(self):
    self.file.write("texture\n")
    self.file.write("%d\n"%len(self.textures))
    for t in self.textures:
      self.file.write(" %s %d\n"%t)
    writeln(self.file)

  def add_body(self,bname):
    body_objs = []
    all_objs = Blender.Object.Get()
    for obj in all_objs:
      name = obj.name
      if (name[0] == 's' or name[0] == 'c' or name[0] == 'm') and name[1] == '.':
        rpos = string.rfind(name,'.')
        if rpos==1: rpos = len(name)
        bodyName = name[2:rpos]
        if bodyName == bname:
          body_objs.append(name)
    if (len(body_objs) >= 0):
      body = self.process_body(bname,body_objs)
      self.bodies.append(body)
    else:
      print "WARNING: NO BODY OBJECT EXISTS FOR " + bname

  def process_body(self, bodyName, bodyObjs):
      body = Body(bodyName)
      baseobj = Blender.Object.Get(bodyName)
      baseMatrix = baseobj.matrix
      for bobj in bodyObjs:
        if bobj[0] == 's':
          obj = Blender.Object.Get(bobj)
          m = obj.matrix
          localm = transform_matrix_to_dest(m,m)
          radius = math.sqrt(localm[0][0])
          #print "b_radius:" + str(obj.data.radius)
          center = transform_point_to_dest(baseMatrix,m[3])
          bp = Body_part(0)
          bp.v.append(center)
          bp.radius = radius
          mesh = obj.data
          bp.flags = convert_face_flags(mesh.faces[0].mode)
          body.add_part(bp)
        elif bobj[0] == 'c':
          obj = Blender.Object.Get(bobj)
          m = obj.matrix
          localm = transform_matrix_to_dest(m,m)
          radius = math.sqrt(localm[0][0])
          height = math.sqrt(localm[2][2])
          lpoint1 = vec_add(m[3],scal_vec_mul(-height,vec_normal(m[2])))
          lpoint2 = vec_add(m[3],scal_vec_mul( height,vec_normal(m[2])))
          point1 = transform_point_to_dest(baseMatrix,lpoint1)
          point2 = transform_point_to_dest(baseMatrix,lpoint2)
          bp = Body_part(1)
          bp.v.append(point1)
          bp.v.append(point2)
          bp.radius = radius
          mesh = obj.data
          bp.flags = convert_face_flags(mesh.faces[0].mode)
          body.add_part(bp)
        elif bobj[0] == 'm':
          obj = Blender.Object.Get(bobj)
          matrix = obj.matrix
          mesh    = obj.data
          for face in mesh.faces:
            bp = Body_part(2)
            bp.flags = convert_face_flags(face.mode)
            nv = len(face.v)
            for i in range(nv):
              lpoint = face.v[i].co
              gpoint = transform_point_to_src(matrix,lpoint) 
              point = transform_point_to_dest(baseMatrix,gpoint)
              bp.v.append(point)
            body.add_part(bp)
      return body
    
  def write_bodies(self):
    self.file.write("body %d\n"%len(self.bodies))
    for b in self.bodies:
      b.write(self.file)
    self.file.write("\n")

  def write_meshes(self):
    self.file.write("mesh\n")
    self.file.write("%d\n"%(len(self.sub_meshes)))
    for s in self.sub_meshes:
      s.write(self.file)
    writeln(self.file)

  def write_skeletons(self):
    self.file.write("skeleton %d\n"%len(self.skeletons))
    for s in self.skeletons:
      print "exporting skeleton: " + str(s.name)
      s.write(self.file)
    writeln(self.file)

  def write_skeleton_anims(self):
    self.file.write("skeleton_anim %d\n"%len(self.skeletons))
    for s in self.skeletons:
      s.write_anims(self.file)
    writeln(self.file)

class Bone:
  def add_action(self, blendipo):
    sample_points = blendipo.curves[0].bezierPoints
    num_keys = len(sample_points)
    for sample_point in sample_points:
      q = [0,0,0,0]
      if (sample_point.pt[0] < self.last_key):
        print "ERROR Key out of order, last key = " + str(self.last_key) + " new key = " + str(sample_point.pt[0])
        exit()
      haveRotation = False
      for curve in blendipo.curves:
        if curve.name == 'QuatX':
          haveRotation = True
          q[0]=curve[sample_point.pt[0]]
        if curve.name == 'QuatY':
          q[1]=curve[sample_point.pt[0]]
        if curve.name == 'QuatZ':
          q[2]=curve[sample_point.pt[0]]
        if curve.name == 'QuatW':
          q[3]=curve[sample_point.pt[0]]
      if haveRotation == False:
        print "ERROR: First frame of animation must have rotation values."
        exit()
      self.keys.append((sample_point.pt[0],q))
      self.last_key = sample_point.pt[0]
    if len(blendipo.curves) >= 7:
      pos_points = blendipo.curves[0].bezierPoints
      haveLocation = False
      for axis in blendipo.curves:
        if curve.name == 'LocX':
          haveLocation = True
          pos_points = blendipo.curves[axis].bezierPoints
      if haveLocation == True:
        for pos_point in pos_points:
          p = [0,0,0]
          for curve in blendipo.curves:
            if curve.name == 'LocX':
              p[0] = curve[pos_point.pt[0]]
            if curve.name == 'LocY':
              p[1] = curve[pos_point.pt[0]]
            if curve.name == 'LocZ':
              p[2] = curve[pos_point.pt[0]]
          self.position_keys.append((pos_point.pt[0],p))
    
  def __init__(self,blender_bone,index_no,parent_bone,action_prefixes):
    self.name = blender_bone.name
    self.index = index_no
    self.parent = parent_bone
    if (parent_bone):
      parent_bone.children.append(self)
    self.children = []
    bs = blender_bone.matrix['BONESPACE']
    restMat_row0 = [ bs[0][0] , bs[0][1] , bs[0][2] ]
    restMat_row1 = [ bs[1][0] , bs[1][1] , bs[1][2] ]
    restMat_row2 = [ bs[2][0] , bs[2][1] , bs[2][2] ]
    row3_0 = blender_bone.head['BONESPACE'][0]
    row3_1 = blender_bone.head['BONESPACE'][1]
    row3_2 = blender_bone.head['BONESPACE'][2]
    
    if (parent_bone):
      pm = blender_bone.parent.matrix['ARMATURESPACE']

      ph = blender_bone.parent.head['ARMATURESPACE']
      ch = blender_bone.head['ARMATURESPACE']

      minus = [ ch[0]-ph[0] , ch[1]-ph[1] , ch[2]-ph[2] ]
      row3_0 = minus[0]*pm[0][0] + minus[1]*pm[0][1] + minus[2]*pm[0][2]
      row3_1 = minus[0]*pm[1][0] + minus[1]*pm[1][1] + minus[2]*pm[1][2]
      row3_2 = minus[0]*pm[2][0] + minus[1]*pm[2][1] + minus[2]*pm[2][2]
    
    restMat_row3 = [ row3_0 , row3_1 , row3_2 ]
    self.restMat = [ restMat_row0 , restMat_row1 , restMat_row2 , restMat_row3 ]
    
    self.local_frame = self.restMat
    self.keys = []
    self.position_keys = []
    self.last_key = -1

    for action_prefix in action_prefixes:
      action_name = action_prefix + "." + self.name
      blendipo = Blender.Ipo.get(action_name)
      if blendipo:
        pass
      else:
        print "Error: unable to find ipo " + action_name
        exit(0)
        return
      if len(blendipo.curves) < 4:
        print "Error: not enough curves for ipo " +nm
        exit(0)
      self.add_action(blendipo)

  def write_parent_frame(self,file):
    if self.parent:
      file.write("%d\n"%self.parent.index)
    else:
      file.write("-1\n")
    writeln_vec(file,self.parent_frame[0]) #rest position
    writeln_vec(file,self.parent_frame[1]) #rest position
    writeln_vec(file,self.parent_frame[2]) #rest position
    writeln_vec(file,self.parent_frame[3]) #rest position
    file.write("\n")
    
  def write_global_frame(self,file):
    file.write("\n{\n")
    file.write("  {%f, %f, %f},\n"%(self.global_frame[0][0],self.global_frame[0][1],self.global_frame[0][2]))
    file.write("  {%f, %f, %f},\n"%(self.global_frame[1][0],self.global_frame[1][1],self.global_frame[1][2]))
    file.write("  {%f, %f, %f},\n"%(self.global_frame[2][0],self.global_frame[2][1],self.global_frame[2][2]))
    file.write("  {%f, %f, %f} \n"%(self.global_frame[3][0],self.global_frame[3][1],self.global_frame[3][2]))
    file.write("},\n")

  def write(self,file):
    if self.parent:
      file.write("%d"%self.parent.index)
    else:
      file.write("-1")
    file.write(" %s 0\n"%self.name)      
    writeln_vec(file,self.local_frame[0]) #rest position
    writeln_vec(file,self.local_frame[1]) #rest position
    writeln_vec(file,self.local_frame[2]) #rest position
    writeln_vec(file,self.local_frame[3]) #rest position
    file.write("\n")

  def write_anim(self,file):
    file.write("%d\n"%(len(self.keys)+1))
    rest_quat = Quaternion_from_matrix(self.local_frame)
    file.write(" 0   %f %f %f %f\n"%(rest_quat[0],rest_quat[1],rest_quat[2],rest_quat[3]))
    for key in self.keys:
      key_quat = [key[1][0],key[1][1],key[1][2],key[1][3]] 
      lkey = transform_quaternion_to_src(rest_quat,key_quat)
      file.write(" %d   %f %f %f %f\n"%(int(key[0]),lkey[0],lkey[1],lkey[2],lkey[3]))

  def set_parent_frame(self,parent_frame):
    self.parent_frame = parent_frame
    self.global_frame = transform_matrix_to_src(self.parent_frame, self.local_frame)
    for child in self.children:
      child.set_parent_frame(self.global_frame)
    
def compile_bone_children(cur_blender_bone,index,parent_bone,action_names):
  #print "Adding bone " + cur_blender_bone.name + " at index " + str(index)
  new_bone = Bone(cur_blender_bone,index,parent_bone,action_names)
  new_bone_list = [new_bone]
  index += 1
  for child_bone in cur_blender_bone.children:
    bone_list = compile_bone_children(child_bone,index,new_bone,action_names)
    index += len(bone_list)
    new_bone_list.extend(bone_list)
  return new_bone_list
  
class Skeleton:
  def __init__(self,name,anim_name,extra_skeletons=[]):
    self.name = name
    self.anim_name = anim_name
    self.extra_skeletons = extra_skeletons
    self.bones = []
    self.rest_pos = []
    self.poses = []
    self.num_bones = 0
    obj = Blender.Object.Get(name)
    if not obj:
      print "Unable to get object for skeleton " + name
      exit(0)
    armature = Blender.Armature.Get(obj.data.name)
    if not armature:
      print "Unable to get armature for skeleton " + name
      exit(0)
    obj_names = [name]
    obj_names.extend(extra_skeletons)
    action_names = []
    for obj_name in obj_names:
      action_obj = Blender.Object.Get(obj_name)
      if not action_obj:
        print "Unable to get object for extra skeleton " + obj_name
        exit(0)
      action_name = action_obj.action.getName()
      action_names.append(action_name)
    for bone in armature.bones.values():
      if bone.hasParent() == 0:
        bone_list = compile_bone_children(bone,0,0,action_names)
        bone_list[0].set_parent_frame(identityMatrix4())
        self.bones.extend(bone_list)
 
  def write(self,file):
    file.write(" %s %d\n"%(self.name, len(self.bones)))

    for bone in self.bones:
      bone.write(file)

  def write_parent_frames(self,file):
    file.write(" %s %d\n"%(self.name, len(self.bones)))

    for bone in self.bones:
      bone.write_parent_frame(file)

  def write_global_frames(self,file):
    for bone in self.bones:
      bone.write_global_frame(file)
    file.write("\n")

  def write_anims(self,file):
    print "exporting skeleton animations..."
    file.write(" %s %d\n"%(self.anim_name, len(self.bones)))

    for bone in self.bones:
      #print "writing_anims"
      #print bone.name
      bone.write_anim(file)

    if len(self.bones):
      #write position ipo
      file.write("%d\n  0  0.0 0.0 0.0\n"%(len(self.bones[0].position_keys)+1))
      for key in self.bones[0].position_keys:
        lkey = transform_dir_to_src(self.bones[0].local_frame,key[1])
        file.write(" %d   %f %f %f\n"%(int(key[0]),lkey[0],lkey[1],lkey[2]))
    else:
      file.write("0\n")
    file.write("\n")

class Body_part:
  def __init__(self,bp_type):
    self.v = []
    self.radius = 0
    self.bp_type = bp_type
    self.flags = 0

  def write(self,file):
    if (self.bp_type == 0):
      file.write("   sphere %f "%self.radius)
      write_vec(file,self.v[0])
    elif (self.bp_type == 1):
      file.write("   capsule %f "%self.radius)
      write_vec(file, self.v[0])
      write_vec(file, self.v[1])
    elif (self.bp_type == 2):
      file.write("   face %d "%len(self.v))
      for vert in self.v:
        write_vec(file,vert)
    file.write(" %d \n"%self.flags)

class Body:
  def __init__(self,name):
    self.body_parts = []
    self.name = name

  def add_part(self,bp):
    self.body_parts.append(bp)

  def write(self,file):
    file.write(" bo_%s "%self.name)
    if (len(self.body_parts) != 1):
      file.write(" composite %d \n"%len(self.body_parts))
    for bp in self.body_parts:
      bp.write(file)

############################################################################################################################################

def scal_vec_mul(s,v):
   return [s * v[0],s * v[1],s * v[2]]

def scal_vec_mul2(s,v):
   return [s * v[0],s * v[1]]

def vec_scal_mul(v,s):
   return [s * v[0],s * v[1],s * v[2]]

def vec_copy(v):
   return [v[0], v[1], v[2]]

def vec_add(va,vb):
   return [va[0]+vb[0], va[1]+vb[1], va[2]+vb[2]]

def vec_add2(va,vb):
   return [va[0]+vb[0], va[1]+vb[1]]

def vec_sub(va,vb):
   return [va[0]-vb[0], va[1]-vb[1], va[2]-vb[2]]

def vec_sub2(va,vb):
   return [va[0]-vb[0], va[1]-vb[1]]

def dotp(va, vb):
    return (va[0]*vb[0] + va[1]*vb[1] + va[2]*vb[2])

def crossp(va,vb):
    return ([va[1]*vb[2] - va[2]*vb[1],va[2]*vb[0] - va[0]*vb[2],va[0]*vb[1] - va[1]*vb[0]])

def vec_len(v):
    return math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])

def vec_normal(v):
    l = vec_len(v)
    return [v[0]/l,v[1]/l,v[2]/l]

def nearly_equals(a,b):
  return ((a - 0.01) < b) and ( b < (a + 0.01))

def vec_nearly_equals(a,b):
  return nearly_equals(a[0],b[0]) and nearly_equals(a[1],b[1]) and nearly_equals(a[2],b[2])
 
def vec_nearly_equals2(a,b):
  return nearly_equals(a[0],b[0]) and nearly_equals(a[1],b[1])

def transform_dir_to_src(m,v):
    v0 = scal_vec_mul(v[0],m[0])
    v1 = scal_vec_mul(v[1],m[1])
    v2 = scal_vec_mul(v[2],m[2])
    return vec_add(v0,vec_add(v1,v2))

def transform_dir_to_src2(m,v):
    v0 = scal_vec_mul2(v[0],m[0])
    v1 = scal_vec_mul2(v[1],m[1])
    return vec_add2(v0,v1)

def transform_dir_to_dest(m,v):
    return [dotp(m[0],v), dotp(m[1],v), dotp(m[2],v)]

def transform_point_to_src(m,v):
    p = transform_dir_to_src(m,v)
    return vec_add(p,m[3])

def transform_point_to_src2(m,v):
    p = transform_dir_to_src2(m,v)
    return vec_add2(p,m[2])

def transform_point_to_dest(m,v):
    vo = vec_sub(v,m[3])
    return transform_dir_to_dest(m,vo)

def transform_matrix_to_src(m,mt):
    return [transform_dir_to_src(m,mt[0]), transform_dir_to_src(m,mt[1]), transform_dir_to_src(m,mt[2]), transform_point_to_src(m,mt[3])]

def transform_matrix_to_dest(m,mt):
    return [transform_dir_to_dest(m,mt[0]), transform_dir_to_dest(m,mt[1]), transform_dir_to_dest(m,mt[2]), transform_point_to_dest(m,mt[3])]

def transform_frame_to_dest(m,f):
    rot = transform_matrix_to_dest(m,f)
    return [rot[0],rot[1],rot[2],transform_point_to_dest(m,f[3])]

def matrix_advance(m,alpha):
    m[3] = vec_add(m[3],vec_scal_mul(m[1],alpha))

def matrix_rotate_about_side(m,alpha):
    ca = math.cos(alpha)
    sa = math.sin(alpha)
    new_f = vec_add(vec_scal_mul(m[1],ca) , vec_scal_mul(m[2],sa))
    new_u = vec_sub(vec_scal_mul(m[2],ca) , vec_scal_mul(m[1],sa))
    m[1][0], m[1][1],m[1][2] = new_f
    m[2][0], m[2][1],m[2][2] = new_u

def matrix_rotate_about_forward(m,alpha):
    ca = math.cos(alpha)
    sa = math.sin(alpha)
    new_s = vec_sub(vec_scal_mul(m[0],ca) , vec_scal_mul(m[2],sa))
    new_u = vec_add(vec_scal_mul(m[2],ca) , vec_scal_mul(m[0],sa))
    m[0] = new_s
    m[2] = new_u

def matrix_rotate_about_up(m,alpha):
    ca = math.cos(alpha)
    sa = math.sin(alpha)
    new_s = vec_add(vec_scal_mul(m[0],ca) , vec_scal_mul(m[1],sa))
    new_f = vec_sub(vec_scal_mul(m[1],ca) , vec_scal_mul(m[0],sa))
    m[0] = new_s
    m[1] = new_f

def identityMatrix4():
    return [[1.0, 0.0, 0.0, 0.0],[0.0, 1.0, 0.0, 0.0],[0.0, 0.0, 1.0, 0.0],[0.0, 0.0, 0.0, 1.0]]

def identityMatrix3():
    return [[1.0, 0.0, 0.0],[0.0, 1.0, 0.0],[0.0, 0.0, 1.0]]

def matrix_inverse2(mat):
  det = mat[0][0]*mat[1][1] - mat[0][1]*mat[1][0]
  return [[mat[1][1]/det,-mat[0][1]/det],[-mat[1][0]/det,mat[0][0]/det]]  

def matrix_inverse3(mat):
  det = mat[0][0]*mat[1][1]*mat[2][2] + mat[0][1]*mat[1][2]*mat[2][0] + mat[0][2]*mat[1][0]*mat[2][1] - mat[2][0]*mat[1][1]*mat[0][2] - mat[2][1]*mat[1][2]*mat[0][0] - mat[2][2]*mat[1][0]*mat[0][1]
  d1 = mat[1][1]*mat[2][2]-mat[2][1]*mat[1][2]
  d2 = (mat[1][0]*mat[2][2]-mat[2][0]*mat[1][2])*(-1)
  d3 = mat[1][0]*mat[2][1]-mat[2][0]*mat[1][1]
  d4 = (-1)*(mat[0][1]*mat[2][2]-mat[0][2]*mat[2][1])
  d5 = mat[0][0]*mat[2][2]-mat[2][0]*mat[0][2]
  d6 = (-1)*(mat[0][0]*mat[2][1]-mat[2][0]*mat[0][1])
  d7 = mat[0][1]*mat[1][2]-mat[0][2]*mat[1][1]
  d8 = (-1)*(mat[0][0]*mat[1][2]-mat[1][0]*mat[0][2])
  d9 = mat[0][0]*mat[1][1]-mat[0][1]*mat[1][0]
  return [[d1/det,d2/det,d3/det],[d4/det,d5/det,d6/det],[d7/det,d8/det,d9/det]]

def matrix_multiplication(m,v):
   d1 = m[0][0]*v[0][0]+m[0][0]*v[1][0]+m[0][0]*v[2][0]
   d2 = m[0][1]*v[0][1]+m[0][1]*v[1][1]+m[0][1]*v[2][1]
   d3 = m[0][2]*v[0][2]+m[0][2]*v[1][2]+m[0][2]*v[2][2]
   d4 = m[1][0]*v[1][0]+m[1][0]*v[1][0]+m[1][0]*v[2][0]
   d5 = m[1][1]*v[0][1]+m[1][1]*v[1][1]+m[1][1]*v[2][1]
   d6 = m[1][2]*v[0][2]+m[1][2]*v[1][2]+m[1][2]*v[2][2]
   d7 = m[2][0]*v[1][0]+m[2][0]*v[1][0]+m[2][0]*v[2][0]
   d8 = m[2][1]*v[0][1]+m[2][1]*v[1][1]+m[2][1]*v[2][1]
   d9 = m[2][2]*v[0][2]+m[2][2]*v[1][2]+m[2][2]*v[2][2]
   return [[d1,d2,d3],[d4,d5,d6],[d7,d8,d9]]

def Quaternion_from_matrix(m):
  nxt = [1, 2, 0]
  quat = [0.0, 0.0, 0.0, 0.0]
  trace = m[0][0] + m[1][1] + m[2][2]

  if (trace > 0.0): 
    s = math.sqrt (trace + 1.0)
    quat[3] = s * 0.5;
    s = 0.5 / s;
    quat[0] = (m[1][2] - m[2][1]) * s
    quat[1] = (m[2][0] - m[0][2]) * s
    quat[2] = (m[0][1] - m[1][0]) * s
  else: 
    i = 0
    if (m[1][1] > m[0][0]): 
      i = 1
    if (m[2][2] > m[i][i]): 
      i = 2;
    j = nxt[i]
    k = nxt[j]
    
    s = math.sqrt ((m[i][i] - (m[j][j] + m[k][k])) + 1.0)
    q = [0.0, 0.0, 0.0, 0.0]
    q[i] = s * 0.5
    if (s != 0.0): 
      s = 0.5 / s
    q[3] = (m[j][k] - m[k][j]) * s
    q[j] = (m[i][j] + m[j][i]) * s
    q[k] = (m[i][k] + m[k][i]) * s
    quat[0] = q[0]
    quat[1] = q[1]
    quat[2] = q[2]
    quat[3] = q[3]
  return quat

def transform_quaternion_to_src(s,q):
  result = [0.0, 0.0, 0.0, 0.0]
  result[0] = (s[1] * q[2] - s[2] * q[1]) + s[3] * q[0] + s[0] * q[3]
  result[1] = (s[2] * q[0] - s[0] * q[2]) + s[3] * q[1] + s[1] * q[3]
  result[2] = (s[0] * q[1] - s[1] * q[0]) + s[3] * q[2] + s[2] * q[3]
  result[3] = (s[3] * q[3]) - (s[0] * q[0] + s[1] * q[1] + s[2] * q[2])
  return result

############################################################################################################################################


#Blender.NMface mode flags:
f_collision   = 0x0001
f_tex         = 0x0004
f_light       = 0x0010
f_shared      = 0x0040
f_tiles       = 0x0080
f_halo        = 0x0100
f_two_sided   = 0x0200
f_invisible   = 0x0400
f_obcolor     = 0x0800
f_billboard   = 0x1000
f_shadow      = 0x2000
f_text        = 0x4000

no_fog             = 0x000001
no_lighting        = 0x000002
alpha_test         = 0x000004
no_modify_z_buffer = 0x000008
no_depth_test      = 0x000010
specular_enable    = 0x000020
alpha_blend        = 0x000100
alpha_blend_add    = 0x000200
render_first       = 0x001000
origin_at_camera   = 0x002000
position_map       = 0x010000
normal_map         = 0x020000
reflection_map     = 0x030000
sphere_map         = 0x040000

render_order_default   = 0x00000000
render_order_plus_1    = 0x01000000
render_order_plus_2    = 0x02000000
render_order_plus_3    = 0x03000000
render_order_plus_4    = 0x04000000
render_order_plus_5    = 0x05000000
render_order_plus_6    = 0x06000000
render_order_plus_7    = 0x07000000
render_order_minus_8   = 0x08000000
render_order_minus_7   = 0x09000000
render_order_minus_6   = 0x0a000000
render_order_minus_5   = 0x0b000000
render_order_minus_4   = 0x0c000000
render_order_minus_3   = 0x0d000000
render_order_minus_2   = 0x0e000000
render_order_minus_1   = 0x0f000000

def pack_color(color):
  packed_col = long(color.a) << 24 | long(color.r) << 16 | long(color.g) << 8 | (color.b)
  return packed_col
  
class Sub_mesh_vertex:
  def __init__(self, nmesh_vertex):
    self.nmv = nmesh_vertex
    pass
class Patch_node:
  def __init__(self):
    pass

class Sub_mesh_face:
  def __init__(self, nmesh_face):
    self.nmv   = nmesh_face.v
    if nmesh_face.uv:
      self.uv  = nmesh_face.uv
      self.uv2 = [(0.0,0.0),(0.0,0.0),(0.0,0.0),(0.0,0.0)]
    else:
      self.uv = [(0.0,0.0),(0.0,0.0),(0.0,0.0),(0.0,0.0)]
      self.uv2 = [(0.0,0.0),(0.0,0.0),(0.0,0.0),(0.0,0.0)]
    self.patch_nodes = []
    self.vertex_normals = [[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]]
    self.nmf = nmesh_face
    self.vertex_indices = []
    #self.face_normal = nmesh_face.normal
    #for i in range(len(self.nmv)):
        #self.vertex_normals[i] = self.nmv[i].no

class Sub_mesh_node:
  def __init__(self):
    pass

class Sub_mesh:
  def __init__(self, object, nmesh, index, flags, auto_smooth, nmesh_face, raw_vertex_groups):
    self.object = object
    self.nmesh = nmesh
    if (index):
      self.name = object.name + "." + str(index)
    else:
      self.name = object.name
    self.flags = flags
    self.auto_smooth = auto_smooth
    self.material_no = nmesh_face.mat
    self.material_name = "default"
    if ( len(nmesh.materials) != 0 ):
      self.material_name = nmesh.getMaterials(1)[self.material_no].name
    self.raw_vertex_groups = raw_vertex_groups
    self.faces = []
    self.vertices = []
    self.nmesh_faces = []
    self.vertex_groups = []
    self.vertex_keys = []

  def build(self, nmesh):
    self.build_vertices()
    self.build_faces()
    self.compute_face_normals()
    self.compute_patch_nodes(nmesh)
    self.build_vertex_groups()

  def build_vertices(self):
    self.v_map = []
    for v in self.nmesh.verts:
      self.v_map.append(-1)

  def build_faces(self):
    for nmf in self.nmesh_faces:
      if (len(nmf.v) >= 3):
        new_face = Sub_mesh_face(nmf)
        for v in nmf.v:
          if self.v_map[v.index] == -1:
            new_vertex = Sub_mesh_vertex(v)
            new_vertex.index = len(self.vertices)
            self.vertices.append(new_vertex)
            self.v_map[v.index] = new_vertex.index
          new_face.vertex_indices.append(self.v_map[v.index])
        self.faces.append(new_face)
      else:
        print "warning: Mesh " +  self.name +" has a face with " +  str(len(nmf.v)) + " corners. skipping"
        print "Coords: " + str(nmf.v[0].co) + " , " +  str(nmf.v[1].co)

  def compute_face_normals(self):
    auto_smooth_angle_radians = self.auto_smooth * 3.1416 / 180.0
    cos_a = math.cos(auto_smooth_angle_radians)

    # compute face normals
    for f in self.faces:
      va = vec_sub(self.vertices[f.vertex_indices[1]].nmv.co, self.vertices[f.vertex_indices[0]].nmv.co) 
      vb = vec_sub(self.vertices[f.vertex_indices[2]].nmv.co, self.vertices[f.vertex_indices[0]].nmv.co) 
      normal = crossp(va,vb)
      if ((normal[0] == 0.0) and (normal[1] == 0.0) and (normal[2] == 0.0)):
        f.face_normal = [1.0,0.0,0.0]
      else:
        f.face_normal = vec_normal(normal)

    for f in self.faces:
      for i in range(4):
        f.vertex_normals[i] = vec_copy(f.face_normal) 

    vertex_faces = []
    for v in self.vertices:
      vertex_faces.append([])
    for f in self.faces:
      for i_v in range(len(f.vertex_indices)):
        vertex_faces[f.vertex_indices[i_v]].append((f,i_v))

    for v in vertex_faces:
      for i_f in range(len(v)):
        for j_f in range(i_f + 1, len(v)):
          v[i_f][0].vertex_normals[v[i_f][1]] = vec_add(v[i_f][0].vertex_normals[v[i_f][1]], v[j_f][0].face_normal)
          v[j_f][0].vertex_normals[v[j_f][1]] = vec_add(v[j_f][0].vertex_normals[v[j_f][1]], v[i_f][0].face_normal)

##    for v in vertex_faces:
##      for i_f in range(len(v)):
##        for j_f in range(i_f + 1, len(v)):
##          dp = dotp(v[i_f][0].face_normal, v[j_f][0].face_normal)
##          if (dp  > cos_a):
##            v[i_f][0].vertex_normals[v[i_f][1]] = vec_add(v[i_f][0].vertex_normals[v[i_f][1]], v[j_f][0].face_normal)
##            v[j_f][0].vertex_normals[v[j_f][1]] = vec_add(v[j_f][0].vertex_normals[v[j_f][1]], v[i_f][0].face_normal)

    for f in self.faces:
      for i_v in range(4):
        f.vertex_normals[i_v] = vec_normal(f.vertex_normals[i_v])
        #print f.vertex_normals[i_v]
        #print f.nmf.normal
        
  def recompute_patch_node_normals(self,deformation_data):
    auto_smooth_angle_radians = self.auto_smooth * 3.1416 / 180.0
    cos_a = math.cos(auto_smooth_angle_radians)

    pn_normals = []
    for pn in self.patch_nodes:
      pn_normals.append([0.0, 0.0, 0.0])
    for f in self.faces:
      va = vec_sub(deformation_data[f.vertex_indices[1]], deformation_data[f.vertex_indices[0]]) 
      vb = vec_sub(deformation_data[f.vertex_indices[2]], deformation_data[f.vertex_indices[0]])
      normal = crossp(va,vb)
      if ((normal[0] == 0.0) and (normal[1] == 0.0) and (normal[2] == 0.0)):
        f.face_normal = [1.0,0.0,0.0]
      else:
        f.face_normal = vec_normal(normal)

    for f in self.faces:
      for i in range(4):
        f.vertex_normals[i] = vec_copy(f.face_normal) 

    vertex_faces = []
    for v in self.vertices:
      vertex_faces.append([])
    for f in self.faces:
      for i_v in range(len(f.vertex_indices)):
        vertex_faces[f.vertex_indices[i_v]].append((f,i_v))

    for v in vertex_faces:
      for i_f in range(len(v)):
        for j_f in range(i_f + 1, len(v)):
          dp = dotp(v[i_f][0].face_normal, v[j_f][0].face_normal)
          if (dp  > cos_a):
            v[i_f][0].vertex_normals[v[i_f][1]] = vec_add(v[i_f][0].vertex_normals[v[i_f][1]], v[j_f][0].face_normal)
            v[j_f][0].vertex_normals[v[j_f][1]] = vec_add(v[j_f][0].vertex_normals[v[j_f][1]], v[i_f][0].face_normal)

     
    for f in self.faces:
      for fpn in f.patch_nodes:
        pn_normals[fpn.index] = vec_normal(f.vertex_normals[self.patch_nodes[fpn.index].corner_no])

    for ipn in xrange(len(pn_normals)):
      f = self.faces[self.patch_nodes[ipn].face_no]
      pn_normals[ipn] = vec_normal(f.vertex_normals[self.patch_nodes[ipn].corner_no])
    return pn_normals

  def compute_patch_nodes(self, nmesh):
    vertex_patch_nodes = []
    for v in self.vertices:
      vertex_patch_nodes.append([])
    for i_f in xrange(len(self.faces)):
      f = self.faces[i_f]
      for i_corner in range(len(f.vertex_indices)):
        vertex_index = f.vertex_indices[i_corner]
        found = 0
        i = 0
        while (not found) and (i < len(vertex_patch_nodes[vertex_index])):
          if vec_nearly_equals(vertex_patch_nodes[vertex_index][i].normal, f.vertex_normals[i_corner]):
            found = 1
            if f.nmf.uv: #Unknown results.
              if not vec_nearly_equals2(vertex_patch_nodes[vertex_index][i].uv, f.uv[i_corner]):
                found = 0
            #if f.nmf.image2:
              #a = 5
              #if not vec_nearly_equals2(vertex_patch_nodes[vertex_index][i].uv2, f.uv2[i_corner]):  ###CHANGE
                #found = 0
          if not found:
            i += 1
          else:
            new_patch_node = vertex_patch_nodes[vertex_index][i]
        if not found:
          new_patch_node = Patch_node()
          new_patch_node.vertex_index = f.vertex_indices[i_corner]
          new_patch_node.normal = vec_copy(f.vertex_normals[i_corner])
          new_patch_node.uv  = f.uv[i_corner]
          new_patch_node.uv2 = f.uv2[i_corner]
          if nmesh.hasVertexColours():
            new_patch_node.vertex_color = pack_color(f.nmf.col[i_corner])
          else:
            new_patch_node.vertex_color = long(255) << 24 | long(255) << 16 | long(255) << 8 | (255)
          new_patch_node.face_no = i_f
          new_patch_node.corner_no = i_corner
          vertex_patch_nodes[vertex_index].append(new_patch_node)
        f.patch_nodes.append(new_patch_node)

    self.patch_nodes = []
    i_patch_node =0
    for v in vertex_patch_nodes:
      for pn in v:
        self.patch_nodes.append(pn)      
        pn.index = i_patch_node
        i_patch_node += 1

  def build_vertex_groups(self):
    for raw_group in self.raw_vertex_groups:
      vgroup = (raw_group[0],[])
      first = 1
      group = raw_group[1]
      for t in group:
        if self.v_map[t[0]] == -1:
          pass
        else:
          if first:
            self.vertex_groups.append(vgroup)
            first = 0
          vgroup[1].append([self.v_map[t[0]],t[1]])         
    self.normalize_vertex_group_weights()

  def normalize_vertex_group_weights(self):
    for iv in range(len(self.vertices)):
      total = 0.0
      for g in self.vertex_groups:
        for c in g[1]:
          if c[0] == iv:
            total += c[1]
      for g in self.vertex_groups:
        for c in g[1]:
          if c[0] == iv:
            if c[1] != 0:
              c[1] /= total

  def add_key(self,key_pos,deformed_mesh):
    deformation_data = []
    for v in self.vertices:
      deformed_co = deformed_mesh.verts[v.nmv.index].co
      deformation_data.append(vec_copy(deformed_co))
    deformed_normals = self.recompute_patch_node_normals(deformation_data)
    self.vertex_keys.append((key_pos,deformation_data,deformed_normals))

  def write(self,file):
    file.write(" %s  "%self.name)
    file.write(" %d "%self.flags)
    file.write(" %s  "%self.material_name)
    file.write("\n")
    self.write_vertices(file)
    self.write_vertex_groups(file)
    self.write_vertex_keys(file)
    self.write_patch_nodes(file)
    self.write_faces(file)

  def write_vertices(self,file):
    file.write(" %d\n"%len(self.vertices))
    for v in self.vertices:
      file.write("    %f %f %f\n"%(v.nmv.co[0],v.nmv.co[1],v.nmv.co[2]))

  def write_vertex_groups(self,file):
    file.write(" %d\n"%len(self.vertex_groups))
    for group in self.vertex_groups:
      file.write("  %d "%(group[0]))
      file.write("  %d \n" % (len(group[1])))
      for t in group[1]:
        file.write("  %d %f\n"%(t[0],t[1]))
      
  def write_vertex_keys(self,file):
    file.write(" %d\n"%len(self.vertex_keys))
    for vertex_key in self.vertex_keys:
      file.write("   %d\n"%(vertex_key[0]))
      file.write("    %d\n"%(len(vertex_key[1])))
      for v in vertex_key[1]:
        file.write("    %f %f %f\n"%(v[0],v[1],v[2]))
      file.write("    %d\n"%(len(vertex_key[2])))
      for pn_normal in vertex_key[2]:
        file.write("    %f %f %f\n"%(pn_normal[0],pn_normal[1],pn_normal[2]))

  def write_patch_nodes(self,file):
    file.write(" %d\n"%len(self.patch_nodes))
    for node in self.patch_nodes:
      file.write("  %d  " % node.vertex_index)
      file.write("%d " % node.vertex_color)
      file.write(" %f %f %f\n"%(node.normal[0],node.normal[1],node.normal[2]))
      file.write("   %f %f\n" %(node.uv[0] ,node.uv[1]))
      file.write("   0.0 0.0\n")

  def write_faces(self,file):
    two_sided_warning_issued = 0
    num_triangles = 0
    for f in self.faces:
      num_face_triangles = 1
      if len(f.patch_nodes) == 4:
        num_face_triangles = 2
      if (f.nmf.mode & f_two_sided):
        if (two_sided_warning_issued == 0):
          print "WARNING: Mesh " +  self.name +" has two sided polygons!"
          two_sided_warning_issued = 1
        num_face_triangles = num_face_triangles * 2
      num_triangles += num_face_triangles

    file.write(" %d\n"%num_triangles)
    for f in self.faces:
      if len(f.patch_nodes) == 3:
        file.write("  %d %d %d\n" % (f.patch_nodes[0].index,f.patch_nodes[1].index,f.patch_nodes[2].index))
        if (f.nmf.mode & f_two_sided):
          file.write("  %d %d %d\n" % (f.patch_nodes[0].index,f.patch_nodes[2].index,f.patch_nodes[1].index))
      elif len(f.patch_nodes) == 4:
        file.write("  %d %d %d\n" % (f.patch_nodes[0].index,f.patch_nodes[1].index,f.patch_nodes[2].index))
        if (f.nmf.mode & f_two_sided):
          file.write("  %d %d %d\n" % (f.patch_nodes[0].index,f.patch_nodes[2].index,f.patch_nodes[1].index))
        file.write("  %d %d %d\n" % (f.patch_nodes[2].index,f.patch_nodes[3].index,f.patch_nodes[0].index))
        if (f.nmf.mode & f_two_sided):
          file.write("  %d %d %d\n" % (f.patch_nodes[2].index,f.patch_nodes[0].index,f.patch_nodes[3].index))

  def update_vcache(self,selected_face):
    for pn in selected_face.patch_nodes:
      if pn.index in self.v_cache:
        pass
      else:
        self.v_cache[self.v_cache_pos] = pn.index
        self.v_cache_pos = (self.v_cache_pos + 1) % 16

  def optimize(self):
    for f in self.faces:
      f.remapped = 0
    self.v_cache = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    self.v_cache_pos = 0
    self.mapped_faces = []
    for i in xrange(len(self.faces)):
      selected_face = 0
      minimum_cost = 1000000
      for f in self.faces:
        cost = 0
        if f.remapped:
          continue
        has_vertex_in_cache = 0
        num_in_cache = 0
        scr2 = 0
        for pn in f.patch_nodes:
          for ivc in xrange(len(self.v_cache)):
            if pn.index == self.v_cache[ivc]:
              cache_pos = ((ivc + 16) - self.v_cache_pos) % 16
              a = 1.0 - ((1.0 * cache_pos)/16.0)
              scr2 += 1.0 - a * a  
              num_in_cache += 1
        scr1 = len(f.patch_nodes) - num_in_cache
        cost = 10.0 * scr1 + scr2
        if cost < minimum_cost:
          selected_face = f
          minimum_cost = cost
      self.mapped_faces.append(selected_face)
      selected_face.remapped = 1
      self.update_vcache(selected_face)
    self.faces = self.mapped_faces
# update indices if necessary

  def count_cache_misses(self):
    self.v_cache = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    self.v_cache_pos = 0
    num_missed = 0
    for f in self.faces:
      num_in_cache = 0
      for pn in f.patch_nodes:
        if pn.index in self.v_cache:
          num_in_cache += 1
      num_missed += len(f.patch_nodes) - num_in_cache
      self.update_vcache(f)
    return num_missed
      
class Mesh_obj:
  def __init__(self, name, skeleton_name = "", flags = 0, auto_smooth = 120.0):
    group_names = []   
    self.sub_meshes = []
    self.sub_mesh_images = []
    self.raw_vertex_groups = []
    self.object = Blender.Object.Get(name)
    if not self.object:
      print "ERROR: No object exists with name " + name
      return
    Blender.Set("curframe",0)
    #self.nmesh = Blender.NMesh.GetRaw(self.object.data.name)
    self.nmesh = self.object.getData()
    
    if not self.nmesh:
      print "ERROR: Object " + name + " is not a mesh "
      return
    self.name = self.nmesh.name
    if skeleton_name != "":
      self.get_group_names(group_names,skeleton_name)
    self.get_raw_vertex_groups(group_names)
    for f in self.nmesh.faces:
      i_sub = 0
      found = 0
      while (not found) and (i_sub < len(self.sub_meshes)):
        found = 0
        if (f.mat == self.sub_meshes[i_sub].material_no):
          found = 1
        if (f.mat >= len(self.nmesh.materials)) and (self.sub_meshes[i_sub].material_no >= len(self.nmesh.materials)):
          found = 1
        if not found:
          i_sub += 1
      if not found:
        self.sub_meshes.append(Sub_mesh(self.object, self.nmesh, i_sub, flags, auto_smooth, f, self.raw_vertex_groups))
      self.sub_meshes[i_sub].nmesh_faces.append(f)
    a = 1
    for sub_mesh in self.sub_meshes:
        sub_mesh.build(sub_mesh.nmesh)
        a = a + 1

  def get_group_names(self, group_names, skeleton_name):
    names = self.nmesh.getVertGroupNames()
    skeletonObject = Blender.Object.Get(skeleton_name)
    if not skeletonObject:
      print "Unable to get object for skeleton " + name
      exit(0)
    armature = Blender.Armature.Get(skeletonObject.data.name)
    if not armature:
      print "Unable to get armature for skeleton " + name
      exit(0)
    for bone in armature.bones.values():
      if bone.hasParent() == 0:
        for name in names:
          if bone.name == name:
            group_names.append(name)
        for child in bone.children:
          self.group_name_from_bone(child,group_names,names)

  def group_name_from_bone(self, bone, group_names, names):
    for name in names:
      if bone.name == name:
        group_names.append(name)
    for child in bone.children:
      self.group_name_from_bone(child,group_names,names)
    
  def get_raw_vertex_groups(self, group_names):
    i_group = 0
    for group_name in group_names:
      group = self.nmesh.getVertsFromGroup(group_name,1)
      if not group:
        pass
      else:
        #print "Adding vertex group " + group_name + " to mesh " + self.name
        self.raw_vertex_groups.append((i_group,group))
      i_group += 1

  def add_key(self, key_pos):
    Blender.Set("curframe",key_pos)
    deformed_mesh = Blender.NMesh.GetRawFromObject(self.object.name)
    for s in self.sub_meshes:
      s.add_key(key_pos,deformed_mesh)

  def write(self,file):
    file.write(" %d "%len(self.sub_meshes))
    for s in self.sub_meshes:
      file.write(" %s "%s.name)
    file.write("\n")

############################################################################################################################################


top_disable = 1
top_selectarg1 = 2
top_selectarg2 = 3
top_modulate = 4
top_modulate2x = 5
top_modulate4x = 6
top_add = 7
top_addsigned = 8
top_addsigned2x = 9
top_subtract = 10
top_addsmooth = 11
top_blenddiffusealpha = 12
top_blendtexturealpha = 13
top_blendfactoralpha = 14
top_blendtexturealphapm = 15
top_blendcurrentalpha = 16
top_premodulate = 17
top_modulatealpha_addcolor = 18
top_modulatecolor_addalpha = 19
top_modulateinvalpha_addcolor = 20
top_modulateinvcolor_addalpha = 21
top_bumpenvmap = 22
top_bumpenvmapluminance = 23
top_dotproduct3 = 24
top_multiplyadd = 25
top_lerp = 26

#also in graphics_context.h

ta_current  = 0
ta_diffuse  = 1
ta_specular = 2
ta_temp     = 3
ta_texture  = 4
ta_factor   = 5

arg1_current  = ta_current   << 5
arg1_diffuse  = ta_diffuse   << 5
arg1_specular = ta_specular  << 5
arg1_temp     = ta_temp      << 5
arg1_texture  = ta_texture   << 5
arg1_factor   = ta_factor    << 5

arg2_current  = ta_current   << 8
arg2_diffuse  = ta_diffuse   << 8
arg2_specular = ta_specular  << 8
arg2_temp     = ta_temp      << 8
arg2_texture  = ta_texture   << 8
arg2_factor   = ta_factor    << 8
