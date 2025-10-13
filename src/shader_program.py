from moderngl import Attribute, Uniform
import glms

class ShaderProgram:
    def __init__(self, ctx, vertex_shader_path, fragment_shader_path):
        with open(vertex_shader_path) as file:
            vertex_shader = file.read()
        with open(fragment_shader_path) as file:
            fragment_shader = file.read()

        self.prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
    
        attributes = []
        uniforms = []
        for name in self.prog:
            member = self.prog[name]
            if isinstance(member, Attribute):
                attributes.append(name)
            if isinstance(member, Uniform):
                uniforms.append(name)
        
        self.attributes = attributes
        self.uniforms = uniforms

    def set_uniform(self, name, value):
        if name in self.uniforms:
            uniform = self.prog[name]
            if isinstance(value, glm.mat4):
                uniform.write(value.to_bytes())
            elif hasattr(uniform, "value"):
                uniform.value = value

class ComputeShaderProgram:
    def __init__(self, ctx, compute_shader_path):
        with open(compute_shader_path) as file:
            compute_source = file.read()
        self.prog = ctx.compute_shader(compute_source)

        uniforms = []
        for name in self.prog:
            member = self.prog[name]
            if type(member) == Uniform:
                uniforms.append(name)
    
    def run(self):
        groups_x = (self.width + 15) // 16
        groups_y = (self.height + 15) // 16

        self.compute_shader.run(groups_x=groups_x, groups_y=groups_y, groups_z=1)
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        self.output_graphics.render({"u_texture": self.texture_unit})

    def set_uniform(self, name, value):
        if name in self.prog:
            uniform = self.prog[name]
            if isinstance(value, glm.mat4):
                uniform.write(value.to_bytes())
            if hasattr(uniform, "value"):
                uniform.value = value
    
    def run(self, groups_x, groups_y, groups_z):
        self.prog.run(groups_x=groups_x, groups_y=groups_y, groups_z=groups_z)