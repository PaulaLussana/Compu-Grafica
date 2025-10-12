from pathlib import Path
from window import Window
from texture import Texture
from material import Material
from shader_program import ShaderProgram
from cube import Cube
from quad import Quad
from camera import Camera
from scene import RayScene
import numpy as np

# Constantes de pantalla
WIDTH, HEIGHT = 400, 300

# Crear ventana
window = Window(WIDTH, HEIGHT, "Parcial")

# Shaders
shader_dir = Path(__file__).resolve().parent.parent / "shaders"
shader_program = ShaderProgram(window.ctx, shader_dir / "basic.vert", shader_dir / "basic.frag")
shader_program_skybox = ShaderProgram(window.ctx, shader_dir / "sprite.vert", shader_dir / "sprite.frag")

# Textura base (framebuffer del raytracer)
skybox_texture = Texture(width=WIDTH, height=HEIGHT, channels_amount=3, color=(0, 0, 0))

# Materiales
material = Material(shader_program)
material_sprite = Material(shader_program_skybox, textures_data=[skybox_texture])

# Modelos
cube1 = Cube((-2, 0, 2), (0, 45, 0), (1, 1, 1), "Cube1")
cube2 = Cube((2, 0, 2), (0, 45, 0), (1, 0.5, 1), "Cube2")
quad = Quad((0, 0, 0), (0, 0, 0), (6, 5, 1), name="Sprite", hittable=False)

# Cámara
camera = Camera((0, 0, 10), (0, 0, 0), (0, 1, 0), 45, window.width / window.height, 0.1, 100.0)

# Escena con raytracer
scene = RayScene(window.ctx, camera, WIDTH, HEIGHT)

scene.add_object(quad, material_sprite)
scene.add_object(cube1, material)
scene.add_object(cube2, material)

window.set_scene(scene)
window.run()
