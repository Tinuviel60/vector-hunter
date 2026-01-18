import math
import pytest
from vect_hunt.engine.core import Vector2D
from vect_hunt.engine.core import Geometry


# --------------------
# intervals_overlap
# --------------------
@pytest.mark.parametrize(
    "min1, max1, min2, max2, expected",
    [
        (0, 2, 1, 3, True),  # chevauchement partiel
        (0, 2, 2, 4, True),  # touchent à la frontière
        (0, 1, 2, 3, False),  # complètement séparés
        (-1, 1, -0.5, 0.5, True),  # chevauchement avec négatifs
        (5, 10, 0, 4, False),  # complètement séparés, non chevauchants
        (0, 0, 0, 0, True),  # points uniques
        (2, 2, 2, 2, True),  # points uniques
        (-10, -5, -8, -3, True),  # chevauchement négatif
    ],
)
def test_intervals_overlap(min1, max1, min2, max2, expected):
    assert Geometry.intervals_overlap(min1, max1, min2, max2) == expected


# --------------------
# project_polygon_on_axis
# --------------------
@pytest.mark.parametrize(
    "corners, axis, expected_min, expected_max",
    [
        # carré unité aligné axes
        (
            [Vector2D(0, 0), Vector2D(1, 0), Vector2D(1, 1), Vector2D(0, 1)],
            Vector2D(1, 0),
            0,
            1,
        ),
        (
            [Vector2D(0, 0), Vector2D(1, 0), Vector2D(1, 1), Vector2D(0, 1)],
            Vector2D(0, 1),
            0,
            1,
        ),
        # triangle
        ([Vector2D(0, 0), Vector2D(2, 0), Vector2D(1, 1)], Vector2D(1, 0), 0, 2),
        ([Vector2D(0, 0), Vector2D(2, 0), Vector2D(1, 1)], Vector2D(0, 1), 0, 1),
        # axe diagonal
        (
            [Vector2D(0, 0), Vector2D(1, 0), Vector2D(1, 1), Vector2D(0, 1)],
            Vector2D(1 / math.sqrt(2), 1 / math.sqrt(2)),
            0,
            math.sqrt(2),
        ),
    ],
)
def test_project_polygon_on_axis(corners, axis, expected_min, expected_max):
    min_proj, max_proj = Geometry.project_polygon_on_axis(corners, axis)
    tol = 1e-9
    assert math.isclose(min_proj, expected_min, abs_tol=tol)
    assert math.isclose(max_proj, expected_max, abs_tol=tol)


# --------------------
# get_polygon_normals
# --------------------
def test_get_polygon_normals_square():
    # carré 1x1, coin (0,0), (1,0), (1,1), (0,1)
    corners = [Vector2D(0, 0), Vector2D(1, 0), Vector2D(1, 1), Vector2D(0, 1)]
    normals = Geometry.get_polygon_normals(corners)

    # il doit y avoir 4 normales
    assert len(normals) == 4

    # normales unitaires
    for n in normals:
        assert math.isclose(n.magnitude(), 1.0, abs_tol=1e-9)

    # normales perpendiculaires aux arêtes
    edges = [(corners[i + 1] - corners[i]) for i in range(3)] + [
        corners[0] - corners[3]
    ]
    for edge, normal in zip(edges, normals):
        dot = edge.dot(normal)
        assert math.isclose(dot, 0.0, abs_tol=1e-9)


def test_get_polygon_normals_triangle():
    # triangle simple
    corners = [Vector2D(0, 0), Vector2D(2, 0), Vector2D(1, 1)]
    normals = Geometry.get_polygon_normals(corners)
    assert len(normals) == 3
    for n in normals:
        assert math.isclose(n.magnitude(), 1.0, abs_tol=1e-9)


def test_get_polygon_normals_degenerate_line():
    # 2 points identiques -> normale arbitraire mais gérée
    corners = [Vector2D(0, 0), Vector2D(0, 0)]
    normals = Geometry.get_polygon_normals(corners)
    assert len(normals) == 2
    for n in normals:
        # même si la longueur est zéro, la fonction normalisée ne plante pas
        assert math.isfinite(n.x) and math.isfinite(n.y)


def test_get_polygon_normals_extreme_values():
    # carrés avec valeurs très grandes ou très petites
    corners = [
        Vector2D(1e9, 1e9),
        Vector2D(1e9 + 1, 1e9),
        Vector2D(1e9 + 1, 1e9 + 1),
        Vector2D(1e9, 1e9 + 1),
    ]
    normals = Geometry.get_polygon_normals(corners)
    assert len(normals) == 4
    for n in normals:
        assert math.isclose(n.magnitude(), 1.0, abs_tol=1e-9)

    corners = [
        Vector2D(1e-9, 1e-9),
        Vector2D(1e-9 + 1e-9, 1e-9),
        Vector2D(1e-9 + 1e-9, 1e-9 + 1e-9),
        Vector2D(1e-9, 1e-9 + 1e-9),
    ]
    normals = Geometry.get_polygon_normals(corners)
    for n in normals:
        assert math.isclose(n.magnitude(), 1.0, abs_tol=1e-9)
