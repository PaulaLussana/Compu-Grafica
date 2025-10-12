#version 330

in vec2 in_pos;
in vec2 in_uv;
out vec2 v_uv;

uniform mat4 MVP;

void main(){
    gl_Position = MVP * vec4(in_pos, 0.0, 1.0);
    v_uv = in_uv;
}