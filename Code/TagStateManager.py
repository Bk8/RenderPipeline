

from panda3d.core import NodePath, BitMask32, ColorWriteAttrib, CullFaceAttrib
from panda3d.core import DepthOffsetAttrib

from .Util.DebugObject import DebugObject
from .Globals import Globals

class TagStateManager(DebugObject):

    """ This manager handles the various tag states """

    MASK_GBUFFER  = BitMask32.bit(1)
    MASK_SHADOWS  = BitMask32.bit(2)
    MASK_VOXELIZE = BitMask32.bit(3)

    TAG_SHADOWS = "Shadows"
    TAG_VOXELIZE = "Voxelize"

    def __init__(self, pipeline):
        DebugObject.__init__(self)
        self._pipeline = pipeline
        self._shadow_cameras = []

        # Set the default camera mask
        Globals.base.camNode.set_camera_mask(self.MASK_GBUFFER)

    def apply_shadow_state(self, object, shader, name, sort):
        """ Applies the given shader to the given object, so that when rendering
        the shadows, the object gets rendered with the given shader, assuming the
        sort is higher than the other sorts """ 
        self.debug("Constructing new state", name)
        initial_state = NodePath(name)
        initial_state.set_shader(shader, sort)
        initial_state.set_attrib(ColorWriteAttrib.make(ColorWriteAttrib.C_off), 100000)
        state_name = "S-" + name
        object.set_tag(self.TAG_SHADOWS, state_name)
        for cam in self._shadow_cameras:
            cam.node().set_tag_state(state_name, initial_state.get_state())

    def register_shadow_source(self, source):
        """ Registers a new shadow camera, which is supposed to render shadows.
        The manager then setups all required tags and keeps track of updating them """ 
        source.node().set_tag_state_key(self.TAG_SHADOWS)
        source.node().set_camera_mask(self.MASK_SHADOWS)

        initial_state = NodePath("ShadowInitial")
        initial_state.set_attrib(ColorWriteAttrib.make(ColorWriteAttrib.C_off), 100000)
        # initial_state.set_attrib(CullFaceAttrib.make(CullFaceAttrib.M_cull_counter_clockwise), 100000)
        # initial_state.set_attrib(DepthOffsetAttrib.make(-1), 100000)
        source.node().set_initial_state(initial_state.get_state())
        self._shadow_cameras.append(source)
