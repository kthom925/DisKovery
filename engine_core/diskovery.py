from diskovery_instance import DkInstance
from diskovery_buffer import UniformBuffer
from diskovery_image import Texture
from diskovery_mesh import Mesh
from diskovery_pipeline import Shader, Pipeline
from diskovery_descriptor import make_set_layout, Descriptor
import pygame
from xmath import *

_dk = None

_meshes = { }
_textures = { }

_shaders = { }
_descriptors = { }
_pipelines = { }

_samplers = { }

class Entity():
	def __init__(self, position=None):
		self.position = position if position != None else (0, 0, 0)

		self.parent = None
		self.children = []

	def world_position(self):
		p = self.parent
		pos = self.position

		while p != None:
			pos = vec_add(pos, p.position)
			p = p.parent

		return pos

	def detach(self):
		self.parent.children.remove(self)
		self.parent = None

	def set_parent(self, parent):
		if self.parent != None:
			self.detach()

		self.parent = parent
		parent.children.append(self)

class RenderedEntity(Entity):
	global _dk
	def __init__(self, 
		position=None, 
		rotation=None, 
		scale=None, 
		shade=None,
		textures=None,
		mesh=None):
		Entity.__init__(self, position)

		self.rotation = rotation if rotation != None else (0, 0, 0)
		self.scale = scale if scale != None else (1, 1, 1)

		self.pipeline = shader(shade).definition if shade != None else shader("Default").definition
		self.textures = textures if textures != None else ["Default"]
		self.mesh = mesh if mesh != None else None

		self.uniforms = []
		self.descriptor_sets = []

		uniform_types = shader(shade).uniforms

		for u_type in uniform_types:
			self.uniforms.append(UniformBuffer(_dk, u_type))

		self.descriptor = Descriptor(
			_dk, 
			self.pipeline, 
			descriptor(self.pipeline), 
			self.uniforms, 
			self.textures
		)	

	def update(self, ind):
		m = MVPMatrix()
		m.model = glm.translate(glm.mat4(1.), self.position)
		m.view = glm.lookAt(glm.vec3(2, 2, 2), glm.vec3(), glm.vec3(0, 0, 1))
		m.projection = glm.perspective(
			glm.radians(45.), 
			extent().width/extent().height, 
			0.1, 
			10.
		)
		m.projection[1][1] *= -1

		for uniform in self.uniforms:
			uniform.update(m, ind)


	def cleanup(self):
		for u in self.uniforms:
			u.cleanup()

		self.descriptor.cleanup()



def add_mesh(filename, name=None):
	global _meshes

	m = Mesh(_dk, filename)
	if name is None:
		_meshes[filename[:-4]] = m
	else:
		_meshes[name] = m

def add_texture(filename, name=None):
	global _textures

	t = Texture(_dk, filename)
	if name is None:
		_textures[filename[:-4]] = t
	else:
		_textures[name] = t

def add_shader(name, files, definition, uniforms):
	global _shaders

	s = Shader(files, definition, uniforms)

	_shaders[name] = s

	if s.definition not in _descriptors.keys():
		_descriptors[s.definition] = make_set_layout(_dk, s.definition)

	_pipelines[s.definition] = Pipeline(_dk, s, _descriptors[s.definition])

def shader(name):
	global _shaders
	return _shaders[name]

def descriptor(definition):
	global _descriptors
	return _descriptors[definition]

def init(debug_mode=False):
	global _dk
	_dk = DkInstance(debug_mode)

def run():
	global _dk

	running = True
	while running:

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
				quit()
				break

def quit():
	global _dk, _meshes, _textures, _pipelines, _descriptors

	for mesh in _meshes.values():
		mesh.cleanup()

	for texture in _textures.values():
		texture.cleanup()

	for pipeline in _pipelines.values():
		pipeline.cleanup()

	for descriptor in _descriptors.values():
		_dk.DestroyDescriptorSetLayout(_dk.device, descriptor, None)

	_dk.cleanup()

