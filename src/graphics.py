import numpy as np
import glm

class Graphics:
    def __init__(self, ctx, model, material):
        self.__ctx = ctx
        self.__model = model
        self.__material = material

        # Buffers y VAO
        self.__vbo = self.create_buffers()
        self.__ibo = ctx.buffer(model.indices.tobytes())
        self.__vao = ctx.vertex_array(
            material.shader_program.prog,
            [*self.__vbo],
            self.__ibo
        )

        # Diccionario de texturas (nombre: (objeto CPU, textura GPU))
        self.__textures = self.load_textures(material.textures_data)

    # --- Properties de solo lectura para compatibilidad externa ---
    @property
    def vbo(self):
        return self.__vbo

    @property
    def ibo(self):
        return self.__ibo

    @property
    def vao(self):
        return self.__vao

    @property
    def textures(self):
        return self.__textures
    # --------------------------------------------------------------

    def create_buffers(self):
        buffers = []
        shader_attributes = self.__material.shader_program.attributes

        for attribute in self.__model.vertex_layout.get_attributes():
            if attribute.name in shader_attributes:
                vbo = self.__ctx.buffer(attribute.array.tobytes())
                # (buffer, format, attribute_name)
                buffers.append((vbo, attribute.format, attribute.name))
        return buffers

    def load_textures(self, textures_data):
        textures = {}
        if not textures_data:
            return textures
        for texture in textures_data:
            # Acepta None/arrays; evita truthiness ambiguo con numpy
            if texture.image_data is not None:
                texture_ctx = self.__ctx.texture(
                    texture.size,
                    texture.channels_amount,
                    texture.image_data.tobytes()
                )
                if getattr(texture, "build_mipmaps", False):
                    texture_ctx.build_mipmaps()
                texture_ctx.repeat_x = getattr(texture, "repeat_x", False)
                texture_ctx.repeat_y = getattr(texture, "repeat_y", False)
                textures[texture.name] = (texture, texture_ctx)
        return textures

    def bind_to_image(self, name="u_texture", unit=0, read=False, write=True):
        if name not in self.__textures:
            # Si no existe, no rompas el render loop
            return
        self.__textures[name][1].bind_to_image(unit, read, write)

    def render(self, uniforms):
        # Seteo de uniforms si existen en el shader
        for name, value in uniforms.items():
            if name in self.__material.shader_program.prog:
                self.__material.set_uniform(name, value)

        # Bind de texturas: usa el diccionario correcto
        for i, (name, (texture_obj, texture_ctx)) in enumerate(self.__textures.items()):
            texture_ctx.use(i)
            # Pasar el sampler como entero de unidad
            self.__material.shader_program.set_uniform(name, i)

        # Dibuja
        self.__vao.render()

    def update_texture(self, texture_name, new_data):
        if texture_name not in self.__textures:
            raise ValueError(f"No existe la textura {texture_name}")

        texture_obj, texture_ctx = self.__textures[texture_name]
        texture_obj.update_data(new_data)
        texture_ctx.write(texture_obj.image_data.tobytes())


class ComputeGraphics(Graphics):
    def __init__(self, ctx, model, material):
        # Mantengo la misma convención de atributos "protegidos"
        self._ctx = ctx
        self._model = model
        self._material = material
        self.self_textures = material.textures_data
        super().__init__(ctx, model, material)

    def create_primitive(self, primitives):
        amin, amax = self._model.aabb
        primitives.append({"aabb_min": amin, "aabb_max": amax})

    def create_transformation_matrix(self, transformations_matrix, index):
        m = self._model.get_model_matrix()
        transformations_matrix[index, :] = np.array(m.to_list(), dtype="f4").reshape(16)

    def create_inverse_transformation_matrix(self, inverse_transformations_matrix, index):
        m = self._model.get_model_matrix()
        inverse = glm.inverse(m)
        inverse_transformations_matrix[index, :] = np.array(inverse.to_list(), dtype="f4").reshape(16)

    def create_material_matrix(self, materials_matrix, index):
        reflectivity = self._material.reflectivity
        r, g, b = self._material.colorRGB

        r = r / 255.0 if r > 1.0 else r
        g = g / 255.0 if g > 1.0 else g
        b = b / 255.0 if b > 1.0 else b

        materials_matrix[index, :] = np.array([r, g, b, reflectivity], dtype="f4")
