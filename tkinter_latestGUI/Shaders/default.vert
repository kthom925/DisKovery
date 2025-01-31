#version 450
#extension GL_ARB_separate_shader_objects : enable

layout(binding = 1) uniform MVPMatrix {
    mat4 model;
    mat4 view;
    mat4 proj;
} mvp;

layout(location = 0) in vec3 inPosition;
layout(location = 1) in vec3 inColor;
layout(location = 2) in vec2 inTexCoord;
layout(location = 3) in vec3 inNormal;

layout(location = 0) out vec3 fragColor;
layout(location = 1) out vec2 fragTexCoord;
layout(location = 2) out vec3 fragNormal;
layout(location = 3) out vec4 worldPosition;

void main() {
    worldPosition = mvp.model * vec4(inPosition, 1.0);
    gl_Position = mvp.proj * mvp.view * worldPosition;
    fragColor = inColor;
    fragTexCoord = inTexCoord;
    fragNormal = (mvp.model * vec4(inNormal, 0.0)).xyz;
}