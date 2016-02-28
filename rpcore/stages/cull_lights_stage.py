"""

RenderPipeline

Copyright (c) 2014-2016 tobspr <tobias.springer1@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import math

from panda3d.core import Texture, Vec4

from rpcore.render_stage import RenderStage
from rpcore.image import Image

class CullLightsStage(RenderStage):

    """ This stage takes the list of used cells and creates a list of lights
    for each cell """

    required_pipes = ["CellListBuffer"]
    required_inputs = ["AllLightsData", "maxLightIndex"]

    def __init__(self, pipeline):
        RenderStage.__init__(self, pipeline)
        self.max_lights_per_cell = pipeline.settings["lighting.max_lights_per_cell"]
        self.slice_width = pipeline.settings["lighting.culling_slice_width"]

        # Amount of light classes. Has to match the ones in LightClassification.inc.glsl
        self.num_light_classes = 4

    @property
    def produced_pipes(self):
        return {"PerCellLights": self._per_cell_lights}

    @property
    def produced_defines(self):
        return {
            "LC_SHADE_SLICES": self._num_rows,
            "LC_LIGHT_CLASS_COUNT": self.num_light_classes
        }

    def create(self):
        max_cells = self._pipeline.light_mgr.total_tiles
        self._num_rows = int(math.ceil(max_cells / float(self.slice_width)))
        self._target = self.make_target("CullLights")

        # Don't use an oversized triangle for the target, since this leads to
        # overshading
        self._target.USE_OVERSIZED_TRIANGLE = False
        self._target.size = self.slice_width, self._num_rows
        self._target.prepare_offscreen_buffer()

        self._per_cell_lights = Image.create_buffer(
            "PerCellLights", max_cells * (self.max_lights_per_cell + self.num_light_classes),
            Texture.T_int, Texture.F_r32)
        self._per_cell_lights.set_clear_color(0)
        self._target.set_shader_input("PerCellLightsBuffer", self._per_cell_lights)

        self.debug("Using", self._num_rows, "culling lines")

    def set_shaders(self):
        self._target.set_shader(self.load_shader(
            "tiled_culling.vert.glsl", "cull_lights.frag.glsl"))