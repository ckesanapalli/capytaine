#!/usr/bin/env python
# coding: utf-8
"""
Compare results of Capytaine with results from Nemoh 2.0.
"""

from capytaine.geometric_bodies.sphere import generate_clever_sphere
from capytaine.geometric_bodies.cylinder import generate_horizontal_cylinder
from capytaine.geometric_bodies.free_surface import FreeSurface
from capytaine.symmetries import *
from capytaine.problems import DiffractionProblem, RadiationProblem
from capytaine.results import assemble_dataset
from capytaine.Nemoh import Nemoh


def test_immersed_sphere():
    """Compare with Nemoh 2.0 for a sphere in infinite fluid.

    The test is ran for two degrees of freedom; due to the symmetries of the problem, the results should be the same.
    They are slightly different due to the meshing of the sphere.
    """
    sphere = generate_clever_sphere(radius=1.0, ntheta=10, nphi=40)
    sphere.dofs["Heave"] = sphere.faces_normals @ (0, 0, 1)
    sphere.dofs["Surge"] = sphere.faces_normals @ (1, 0, 0)
    solver = Nemoh()

    problem = RadiationProblem(body=sphere, radiating_dof="Heave", free_surface=np.infty, sea_bottom=-np.infty)
    result = solver.solve(problem)
    assert np.isclose(result.added_masses["Heave"],       2187, atol=1e-3*sphere.volume*problem.rho)
    assert np.isclose(result.added_masses["Surge"],        0.0, atol=1e-3*sphere.volume*problem.rho)
    assert np.isclose(result.radiation_dampings["Heave"],  0.0, atol=1e-3*sphere.volume*problem.rho)
    assert np.isclose(result.radiation_dampings["Surge"],  0.0, atol=1e-3*sphere.volume*problem.rho)

    problem = RadiationProblem(body=sphere, radiating_dof="Surge", free_surface=np.infty, sea_bottom=-np.infty)
    result = solver.solve(problem)
    assert np.isclose(result.added_masses["Surge"],       2194, atol=1e-3*sphere.volume*problem.rho)
    assert np.isclose(result.added_masses["Heave"],        0.0, atol=1e-3*sphere.volume*problem.rho)
    assert np.isclose(result.radiation_dampings["Surge"],  0.0, atol=1e-3*sphere.volume*problem.rho)
    assert np.isclose(result.radiation_dampings["Heave"],  0.0, atol=1e-3*sphere.volume*problem.rho)


def test_floating_sphere_finite_freq():
    """Compare with Nemoh 2.0 for some cases of a heaving sphere at the free surface in infinite depth."""
    sphere = generate_clever_sphere(radius=1.0, ntheta=3, nphi=12, clip_free_surface=True)
    sphere.dofs["Heave"] = sphere.faces_normals @ (0, 0, 1)
    solver = Nemoh()

    # omega = 1, radiation
    problem = RadiationProblem(body=sphere, omega=1.0, sea_bottom=-np.infty)
    result = solver.solve(problem, keep_details=True)
    assert np.isclose(result.added_masses["Heave"],       1819.6, atol=1e-3*sphere.volume*problem.rho)
    assert np.isclose(result.radiation_dampings["Heave"], 379.39, atol=1e-3*sphere.volume*problem.rho)

    # omega = 1, free surface
    free_surface = FreeSurface(x_range=(-62.5, 62.5), nx=5, y_range=(-62.5, 62.5), ny=5)
    eta = solver.get_free_surface_elevation(result, free_surface)
    ref = np.array(
            [[-0.4340802E-02-0.4742809E-03j, -0.7986111E-03+0.4840984E-02j, 0.2214827E-02+0.4700642E-02j, -0.7986111E-03+0.4840984E-02j, -0.4340803E-02-0.4742807E-03j],
             [-0.7986111E-03+0.4840984E-02j, 0.5733187E-02-0.2179381E-02j, 0.9460892E-03-0.7079404E-02j, 0.5733186E-02-0.2179381E-02j, -0.7986110E-03+0.4840984E-02j],
             [0.2214827E-02+0.4700643E-02j, 0.9460892E-03-0.7079403E-02j, -0.1381670E-01+0.6039315E-01j, 0.9460892E-03-0.7079405E-02j, 0.2214827E-02+0.4700643E-02j],
             [-0.7986111E-03+0.4840984E-02j, 0.5733186E-02-0.2179381E-02j, 0.9460891E-03-0.7079404E-02j, 0.5733187E-02-0.2179380E-02j, -0.7986113E-03+0.4840984E-02j],
             [-0.4340803E-02-0.4742807E-03j, -0.7986111E-03+0.4840984E-02j, 0.2214827E-02+0.4700643E-02j, -0.7986113E-03+0.4840983E-02j, -0.4340803E-02-0.4742809E-03j]]
        )
    assert np.allclose(eta.reshape((5, 5)), ref, rtol=1e-4)

    # omega = 1, diffraction
    problem = DiffractionProblem(body=sphere, omega=1.0, sea_bottom=-np.infty)
    result = solver.solve(problem)
    assert np.isclose(result.forces["Heave"], 1834.9 * np.exp(-2.933j), rtol=1e-3)

    # omega = 2, radiation
    problem = RadiationProblem(body=sphere, omega=2.0, sea_bottom=-np.infty)
    result = solver.solve(problem)
    assert np.isclose(result.added_masses["Heave"],       1369.3, atol=1e-3*sphere.volume*problem.rho)
    assert np.isclose(result.radiation_dampings["Heave"], 1425.6, atol=1e-3*sphere.volume*problem.rho)

    # omega = 2, diffraction
    problem = DiffractionProblem(body=sphere, omega=2.0, sea_bottom=-np.infty)
    result = solver.solve(problem)
    assert np.isclose(result.forces["Heave"], 5846.6 * np.exp(-2.623j), rtol=1e-3)


def test_alien_sphere():
    """Compare with Nemoh 2.0 for some cases of a heaving sphere at the free surface in infinite depth
    for a non-usual gravity and density."""
    sphere = generate_clever_sphere(radius=1.0, ntheta=3, nphi=12, clip_free_surface=True)
    sphere.dofs["Heave"] = sphere.faces_normals @ (0, 0, 1)

    # radiation
    problem = RadiationProblem(body=sphere, rho=450.0, g=1.625, omega=1.0, sea_bottom=-np.infty)
    result = Nemoh().solve(problem)
    assert np.isclose(result.added_masses["Heave"],       515, atol=1e-3*sphere.volume*problem.rho)
    assert np.isclose(result.radiation_dampings["Heave"], 309, atol=1e-3*sphere.volume*problem.rho)

    # diffraction
    problem = DiffractionProblem(body=sphere, rho=450.0, g=1.625, omega=1.0, sea_bottom=-np.infty)
    result = Nemoh().solve(problem)
    assert np.isclose(result.forces["Heave"], 548.5 * np.exp(-2.521j), rtol=1e-2)


def test_floating_sphere_finite_depth():
    """Compare with Nemoh 2.0 for some cases of a heaving sphere at the free surface in finite depth."""
    sphere = generate_clever_sphere(radius=1.0, ntheta=3, nphi=12, clip_free_surface=True)
    sphere.dofs["Heave"] = sphere.faces_normals @ (0, 0, 1)
    solver = Nemoh()

    # omega = 1, radiation
    problem = RadiationProblem(body=sphere, omega=1.0, sea_bottom=-10.0)
    result = solver.solve(problem)
    assert np.isclose(result.added_masses["Heave"],       1740.6, atol=1e-3*sphere.volume*problem.rho)
    assert np.isclose(result.radiation_dampings["Heave"], 380.46, rtol=1e-3*sphere.volume*problem.rho)

    # omega = 1, diffraction
    problem = DiffractionProblem(body=sphere, omega=1.0, sea_bottom=-10.0)
    result = solver.solve(problem)
    assert np.isclose(result.forces["Heave"], 1749.4 * np.exp(-2.922j), rtol=1e-3)

    # omega = 2, radiation
    problem = RadiationProblem(body=sphere, omega=2.0, sea_bottom=-10.0)
    result = Nemoh().solve(problem)
    assert np.isclose(result.added_masses["Heave"],       1375.0, atol=1e-3*sphere.volume*problem.rho)
    assert np.isclose(result.radiation_dampings["Heave"], 1418.0, rtol=1e-3*sphere.volume*problem.rho)

    # omega = 2, diffraction
    problem = DiffractionProblem(body=sphere, omega=2.0, sea_bottom=-10.0)
    result = Nemoh().solve(problem)
    assert np.isclose(result.forces["Heave"], 5872.8 * np.exp(-2.627j), rtol=1e-3)


def test_multibody():
    """Compare with Nemoh 2.0 for two bodies."""
    sphere = generate_clever_sphere(radius=1.0, ntheta=5, nphi=20)
    sphere.translate_z(-2.0)
    sphere.dofs["Surge"] = sphere.faces_normals @ (1, 0, 0)
    sphere.dofs["Heave"] = sphere.faces_normals @ (0, 0, 1)

    cylinder = generate_horizontal_cylinder(length=5.0, radius=1.0, nx=10, nr=1, ntheta=10)
    cylinder.translate([-1.0, 3.0, -3.0])
    cylinder.dofs["Surge"] = cylinder.faces_normals @ (1, 0, 0)
    cylinder.dofs["Heave"] = cylinder.faces_normals @ (0, 0, 1)

    both = cylinder + sphere
    # both.show()

    problems = [RadiationProblem(body=both, radiating_dof=dof, omega=1.0, free_surface=0.0, sea_bottom=-np.infty)
                for dof in both.dofs]
    solver = Nemoh()
    results = [solver.solve(problem) for problem in problems]
    data = assemble_dataset(results)

    Nemoh_2 = np.array([
        [3961.86548, 50.0367661, -3.32347107, 6.36901855E-02, 172.704819, 19.2018471, -5.67303181, -2.98873377],
        [-3.08301544, 5.72392941E-02, 14522.1689, 271.796814, 128.413834, 6.03351116, 427.167358, 64.1587067],
        [161.125534, 17.8332844, 126.392113, 5.88006783, 2242.47412, 7.17850924, 1.29002571, 0.393169671],
        [-5.02560759, -2.75930357, 419.927460, 63.3179016, 1.23501396, 0.416424811, 2341.57593, 15.8266096],
    ])

    dofs_names = list(both.dofs.keys())
    assert np.allclose(data['added_mass'].sel(omega=1.0, radiating_dof=dofs_names, influenced_dof=dofs_names).values,
                       Nemoh_2[:, ::2],  atol=1e-3*both.volume*problems[0].rho)
    assert np.allclose(data['radiation_damping'].sel(omega=1.0, radiating_dof=dofs_names, influenced_dof=dofs_names).values,
                       Nemoh_2[:, 1::2], atol=1e-3*both.volume*problems[0].rho)
