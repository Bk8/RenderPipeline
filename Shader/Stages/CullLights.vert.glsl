#version 400

#pragma include "Includes/Configuration.inc.glsl"

uniform mat4 p3d_ModelViewProjectionMatrix;

in vec4 p3d_Vertex;
out vec2 texcoord;

uniform isamplerBuffer CellListBuffer;


void main() {
    int numTotalCells = texelFetch(CellListBuffer, 0).x;

    int numUsedSlices = int(ceil(numTotalCells / 512))+1;
    float percentageHeight = numUsedSlices / float(LC_SHADE_SLICES);

    float pcHeight = p3d_Vertex.z * 0.5 + 0.5;
    
    gl_Position = vec4(p3d_Vertex.x, (pcHeight * percentageHeight) * 2 - 1 , 0, 1);
    texcoord = sign(p3d_Vertex.xz * 0.5 + 0.5);
}