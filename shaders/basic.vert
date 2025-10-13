#version 330

in vec3 in_pos;
in vec3 in_color;

out vec3 v_color;

void main(){
    gl_Position = vec4(in_pos, 1.0);
    v_color = in_color;
}