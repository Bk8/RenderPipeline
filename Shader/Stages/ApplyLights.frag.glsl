#version 400

#pragma include "Includes/Configuration.inc.glsl"
#pragma include "Includes/LightCulling.inc.glsl"
#pragma include "Includes/PositionReconstruction.inc.glsl"
#pragma include "Includes/LightingPipeline.inc.glsl"
#pragma include "Includes/GBufferPacking.inc.glsl"
#pragma include "Includes/Structures/Material.struct.glsl"

in vec2 texcoord;
out vec4 result;

uniform sampler2D GBufferDepth;

uniform sampler2D GBuffer0;
uniform sampler2D GBuffer1;
uniform sampler2D GBuffer2;

void main() {    

    ivec2 coord = ivec2(gl_FragCoord.xy);
    float depth = texelFetch(GBufferDepth, coord, 0).x;
    ivec3 tile = getCellIndex(coord, depth);

    if (tile.z >= LC_TILE_SLICES) {
        result = vec4(0);
        return;
    }

    Material m = unpack_material(GBufferDepth, GBuffer0, GBuffer1, GBuffer2);

    result.xyz = shade_material_from_tile_buffer(m, tile);
    // result.xyz = m.normal.yxyy;
    result.w = 1.0;
}