#!/usr/bin/env python
# coding: utf-8
"""
Tests for the functions that computes hydrostatic from the mesh vertices 
and faces
"""

import pytest
import pickle
import json
import pprint 
from pathlib import Path

import capytaine as cpt
import numpy as np


def test_sphere():
    density = 1000
    gravity = 9.80665


    sphere = cpt.Sphere(
        radius=10.0,          # Dimension
        center=(0,0,-1),   # Position
        nphi=100, ntheta=50,  # Fineness of the mesh
    )

    horizontal_cylinder = cpt.HorizontalCylinder(
        length=10.0, radius=5.0,  # Dimensions
        center=(0,10,-1),        # Position
        nr=10, nx=10, ntheta=10,   # Fineness of the mesh
    )

    vertical_cylinder = cpt.VerticalCylinder(
        length=10.0, radius=5.0,  # Dimensions
        center=(0,0,0),        # Position
        nr=10, nx=10, ntheta=10,   # Fineness of the mesh
    )

    cog = np.zeros(3)
    old_body = sphere + horizontal_cylinder + vertical_cylinder
    body = cpt.FloatingBody(mesh=old_body.mesh, name="Pod")
    body.add_all_rigid_body_dofs()

    capy_hsdb = body.compute_hydrostatics(cog=cog, density=density, gravity=gravity)
    capy_hsdb["stiffness_matrix"] = capy_hsdb["stiffness_matrix"][2:5,2:5]
    capy_hsdb["inertia_matrix"] = capy_hsdb["inertia_matrix"][3:,3:]
    # =============================================================================
    # Meshmagick
    # =============================================================================
    case_dir = Path(__file__).parent / "Hydrostatics_cases"
    # import meshmagick.mesh as mmm
    # import meshmagick.hydrostatics as mmhs
    # body_mesh = mmm.Mesh(body.mesh.vertices, body.mesh.faces, name=body.mesh.name)
    # mm_hsdb = mmhs.compute_hydrostatics(body_mesh, np.array(cog), density, gravity)
    # mm_hsdb["inertia_matrix"] = body_mesh.eval_plain_mesh_inertias(rho_medium=density).inertia_matrix
    # mm_hsdb["mesh"] = ""
    # with open(f'{case_dir}/sphere__hor_cyl__ver_cyl.pkl.json', 'w') as convert_file:
    #     mm_hsdb_json = {key:(value.tolist() if type(value)==np.ndarray else value)
    #                         for key, value in mm_hsdb.items() }
    #     convert_file.write(json.dumps(mm_hsdb_json))

    with open(f'{case_dir}/sphere__hor_cyl__ver_cyl.pkl.json', 'r') as f:
        mm_hsdb = json.load(f)

    # =============================================================================
    # Logging
    # =============================================================================
    for var in capy_hsdb.keys():
        if var in mm_hsdb.keys():
            assert(np.isclose(capy_hsdb[var], mm_hsdb[var], rtol=1e-2, 
                              atol=1e-3).all())