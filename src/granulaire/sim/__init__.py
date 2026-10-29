"""Physics checks of generated scenes, read back from the OpenUSD files.

* ``scene``: what the checks read from a file (grains, collision hulls,
  masses, friction, ground) and the unit scaling shared by every engine.
* ``mujoco_test``: the pile test in MuJoCo (``granulaire sim-test``).
* ``granulaire/blender/pile_test.py``: the same test in Blender
  (``granulaire blender-test``).
"""
