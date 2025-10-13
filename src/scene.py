import math
from graphics import Graphics
import moderngl
import glm
import numpy as np
from raytracer import RayTracer, RayTracerGPU
from graphics import ComputeGraphics

class Scene:
    def __init__(self, ctx, camera):
        self.ctx = ctx
        self.time = 0.0
        self.camera = camera
        self.graphics = {}
        self.objects = []
        self.model = glm.mat4(1)
        self.view = camera.get_view_matrix()
        self.projection = camera.get_perspective_matrix()

        self.ctx.enable(moderngl.DEPTH_TEST)

    def add_object(self, model, material):
        self.objects.append(model)
        self.graphics[model.name] = Graphics(self.ctx, model, material)
    
    def render(self):
        self.time += 0.01
        for obj in self.objects:
            if (obj.animated):
                obj.rotation += glm.vec3(0.8, 0.6, 0.4)
                obj.position.x += math.sin(self.time) * 0.01

            model = obj.get_model_matrix()
            MVP = self.projection * self.view * model
            self.graphics[obj.name].render({'MVP': MVP})

    def on_mouse_click(self, u, v):
        ray = self.camera.raycast(u, v)
        for obj in self.objects:
            if obj.check_hit(ray.origin, ray.direction):
                print(f"Golpeaste al objeto {obj.name}!")

    def on_resize(self, width, height):
        self.ctx.viewport = (0, 0, width, height)
        self.camera.projection = glm.perspective(glm.radians(45), width / height, 0.1, 100.0)
        self.projection = self.camera.get_perspective_matrix()

    def start(self):
        print("Start!")

class RayScene(Scene):
    def __init__(self, ctx, camera, width, height):
        super().__init__(ctx, camera)
        self.raytracer = RayTracer(camera, width, height)
    
    def start(self):
        self.raytracer.render_frame(self.objects)
        if "Sprite" in self.graphics:
            self.graphics["Sprite"].update_texture("u_texture", self.raytracer.get_texture())
    
    def render(self):
        super().render()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.raytracer = RayTracer(self.camera, width, height)
        self.start()

class RaySceneGPU(Scene):
    def __init__(self, ctx, camera, width, height, output_model, output_material):
        self.ctx = ctx
        self.camera = camera
        self.width = width
        self.height = height
        self.raytracer = None

        self.output_graphics = Graphics(ctx, output_model, output_material)
        self.raytracer = RayTracerGPU(self.ctx, self.camera, self.width, self.height, self.output_graphics)

        super().__init__(self.ctx, self.camera)

    def add_object(self, self_, model, material):
        self.objects.append(model)
        self.graphics[model.name] = ComputeGraphics(self.ctx, model, material)

    def start(self):
        print("Start Raytracing!")
        self.primitives = []
        n = len(self.objects)
        self.models_f = np.zeros((n, 16), dtype='f4')
        self.inv_f = np.zeros((n, 16), dtype='f4')
        self.mats_f = np.zeros((n, 4), dtype='f4')

        self._update_matrix()
        self._matrix_to_ssbbo()

    def run(self):
        groups_x = (self.width + 15) // 16
        groups_y = (self.height + 15) // 16

        self.compute_shader.run(groups_x=groups_x, groups_y=groups_y, groups_z=1)
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        self.output_graphics.render({"u_texture": self.texture_unit})

    def render(self):
        self.time = 0.01
        for obj in self.objects:
            if obj.animated:
                obj.rotation += glm.vec3(0.8, 0.6, 0.4)
                obj.position.x = math.sin(self.time) * 0.01

        if (self.raytracer is not None):
            self._update_matrix()
            self._matrix_to_ssbbo()
            self.raytracer.run()
    
    def _update_matrix(self):
        self.primitives = []

        for i, (name, graphics) in enumerate(self.graphics.items()):
            graphics.create_primitive(self.primitives)
            graphics.create_transformation_matrix(self.models_f, i)
            graphics.create_inverse_transformation_matrix(self.inv_f, i)
            graphics.create_material_matrix(self.mats_f, i)

    def _matrix_to_ssbo(self):
        self.raytracer.matrix_to_ssbo(self.models_f, 0)
        self.raytracer.matrix_to_ssbo(self.inv_f, 1)
        self.raytracer.matrix_to_ssbo(self.mats_f, 2)
        self.raytracer.primitives_to_ssbo(self.primitives, 3)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.width, self.height = width, height
        self.camera.aspect = width / height
