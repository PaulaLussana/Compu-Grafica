#version 330

// Inputs desde el VAO
in vec3 in_pos;
in vec3 in_color;

// Output => lo recibe el fragment shader
out vec3 v_color;

// Variable "global" que recibimos para aplicar transfomraciones al objeto
uniform mat4 MVP;

void main(){
    gl_Position = MVP * vec4(in_pos, 1.0);
    v_color = in_color;
}