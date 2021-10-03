from cadquery.sketch import Sketch, Vector

from pytest import approx, raises
from math import pi, sqrt


def test_face_interface():

    s1 = Sketch().rect(1, 2, 45)

    assert s1._faces.Area() == approx(2)
    assert s1.vertices(">X")._selection[0].toTuple()[0] == approx(1.5 / sqrt(2))

    s2 = Sketch().circle(1)

    assert s2._faces.Area() == approx(pi)

    s3 = Sketch().ellipse(2, 0.5)

    assert s3._faces.Area() == approx(pi)

    s4 = Sketch().trapezoid(2, 0.5, 45)

    assert s4._faces.Area() == approx(0.75)

    s4 = Sketch().trapezoid(2, 0.5, 45)

    assert s4._faces.Area() == approx(0.75)

    s5 = Sketch().slot(3, 2)

    assert s5._faces.Area() == approx(6 + pi)
    assert s5.edges(">Y")._selection[0].Length() == approx(3)

    s6 = Sketch().regularPolygon(1, 5)

    assert len(s6.vertices()._selection) == 5
    assert s6.vertices(">Y")._selection[0].toTuple()[1] == approx(1)

    s7 = Sketch().polygon([(0, 0), (0, 1), (1, 0)])

    assert len(s7.vertices()._selection) == 3
    assert s7._faces.Area() == approx(0.5)

    with raises(ValueError):
        Sketch().face(Sketch())


def test_modes():

    s1 = Sketch().rect(2, 2).rect(1, 1, mode="a")

    assert s1._faces.Area() == approx(4)
    assert len(s1._faces.Faces()) == 2

    s2 = Sketch().rect(2, 2).rect(1, 1, mode="s")

    assert s2._faces.Area() == approx(4 - 1)
    assert len(s2._faces.Faces()) == 1

    s3 = Sketch().rect(2, 2).rect(1, 1, mode="i")

    assert s3._faces.Area() == approx(1)
    assert len(s3._faces.Faces()) == 1

    s4 = Sketch().rect(2, 2).rect(1, 1, mode="c", tag="t")

    assert s4._faces.Area() == approx(4)
    assert len(s4._faces.Faces()) == 1
    assert s4._tags["t"][0].Area() == approx(1)

    with raises(ValueError):
        Sketch().rect(2, 2).rect(1, 1, mode="c")

    with raises(ValueError):
        Sketch().rect(2, 2).rect(1, 1, mode="dummy")


def test_distribute():

    s1 = Sketch().rarray(2, 2, 3, 3).rect(1, 1)

    assert s1._faces.Area() == approx(9)
    assert len(s1._faces.Faces()) == 9

    s2 = Sketch().parray(2, 0, 90, 3).rect(1, 1)

    assert s2._faces.Area() == approx(3)
    assert len(s2._faces.Faces()) == 3

    with raises(ValueError):
        Sketch().rarray(2, 2, 3, 0).rect(1, 1)

    with raises(ValueError):
        Sketch().parray(2, 0, 90, 0).rect(1, 1)

    s3 = Sketch().circle(4, mode="c", tag="c").edges(tag="c").distribute(3).rect(1, 1)

    assert s2._faces.Area() == approx(3)
    assert len(s3._faces.Faces()) == 3
    assert len(s3.reset().vertices("<X")._selection) == 2

    for f in s3._faces.Faces():
        assert f.Center().Length == approx(4)

    s4 = (
        Sketch()
        .circle(4, mode="c", tag="c")
        .edges(tag="c")
        .distribute(3, rotate=False)
        .rect(1, 1)
    )

    assert s4._faces.Area() == approx(3)
    assert len(s4._faces.Faces()) == 3
    assert len(s4.reset().vertices("<X")._selection) == 4

    for f in s4._faces.Faces():
        assert f.Center().Length == approx(4)

    with raises(ValueError):
        Sketch().rect(2, 2).faces().distribute(5)

    with raises(ValueError):
        Sketch().rect(2, 2).distribute(5)

    s5 = Sketch().push([(0, 0), (1, 1)]).rarray(2, 2, 3, 3).rect(0.5, 0.5)

    assert s5._faces.Area() == approx(18 * 0.25)
    assert len(s5._faces.Faces()) == 18

    s6 = Sketch().push([(0, 0), (1, 1)]).parray(2, 0, 90, 3).rect(0.5, 0.5)

    assert s6._faces.Area() == approx(6 * 0.25)
    assert len(s6._faces.Faces()) == 6

    s7 = Sketch().parray(2, 0, 90, 3, False).rect(0.5, 0.5).reset().vertices(">(1,1,0)")

    assert len(s7._selection) == 1

    s8 = Sketch().push([(0, 0), (0, 1)]).parray(2, 0, 90, 3).rect(0.5, 0.5)
    s8.reset().faces(">(1,1,0)")

    assert s8._selection[0].Center().Length == approx(3)

    s9 = Sketch().push([(0, 1)], tag="loc")

    assert len(s9._tags["loc"]) == 1


def test_each():

    s1 = Sketch().each(lambda l: Sketch().push([l]).rect(1, 1))

    assert len(s1._faces.Faces()) == 1

    s2 = (
        Sketch()
        .push([(0, 0), (2, 2)])
        .each(lambda l: Sketch().push([l]).rect(1, 1), ignore_selection=True)
    )

    assert len(s2._faces.Faces()) == 1


def test_modifiers():

    s1 = Sketch().push([(-2, 0), (2, 0)]).rect(1, 1).reset().vertices("<X").fillet(0.1)

    assert len(s1._faces.Faces()) == 2
    assert len(s1._faces.Edges()) == 10

    s2 = Sketch().push([(-2, 0), (2, 0)]).rect(1, 1).reset().vertices(">X").chamfer(0.1)

    assert len(s2._faces.Faces()) == 2
    assert len(s2._faces.Edges()) == 10

    s3 = Sketch().push([(-2, 0), (2, 0)]).rect(1, 1).reset().hull()

    assert len(s3._faces.Faces()) == 3
    assert s3._faces.Area() == approx(5)

    s4 = Sketch().push([(-2, 0), (2, 0)]).rect(1, 1).reset().hull()

    assert len(s4._faces.Faces()) == 3
    assert s4._faces.Area() == approx(5)

    s5 = (
        Sketch()
        .push([(-2, 0), (0, 0), (2, 0)])
        .rect(1, 1)
        .reset()
        .faces("not >X")
        .edges()
        .hull()
    )

    assert len(s5._faces.Faces()) == 4
    assert s5._faces.Area() == approx(4)

    s6 = Sketch().segment((0, 0), (0, 1)).segment((1, 0), (2, 0)).hull()

    assert len(s6._faces.Faces()) == 1
    assert s6._faces.Area() == approx(1)

    with raises(ValueError):
        Sketch().rect(1, 1).vertices().hull()

    with raises(ValueError):
        Sketch().hull()

    s7 = Sketch().rect(2, 2).wires().offset(1)

    assert len(s7._faces.Faces()) == 2
    assert len(s7._faces.Edges()) == 4 + 4 + 4

    s7.clean()

    assert len(s7._faces.Faces()) == 1
    assert len(s7._faces.Edges()) == 4 + 4

    s8 = Sketch().rect(2, 2).wires().offset(-0.5, mode="s")

    assert len(s8._faces.Faces()) == 1
    assert len(s8._faces.Edges()) == 4 + 4


def test_delete():

    s1 = Sketch().push([(-2, 0), (2, 0)]).rect(1, 1).reset()

    assert len(s1._faces.Faces()) == 2

    s1.faces("<X").delete()

    assert len(s1._faces.Faces()) == 1

    s2 = Sketch().segment((0, 0), (1, 0)).segment((0, 1), tag="e").close()
    assert len(s2._edges) == 3

    s2.edges("<X").delete()

    assert len(s2._edges) == 2


def test_selectors():

    s = Sketch().push([(-2, 0), (2, 0)]).rect(1, 1).reset()

    assert len(s._selection) == 0

    s.vertices()

    assert len(s._selection) == 8

    s.reset()

    assert len(s._selection) == 0

    s.edges()

    assert len(s._selection) == 8

    s.reset().wires()

    assert len(s._selection) == 2

    s.reset().faces()

    assert len(s._selection) == 2

    s.reset().vertices("<Y")

    assert len(s._selection) == 4

    s.reset().edges("<X or >X")

    assert len(s._selection) == 2

    s.tag("test").reset()

    assert len(s._selection) == 0

    s.select("test")

    assert len(s._selection) == 2


def test_edge_interface():

    s1 = (
        Sketch()
        .segment((0, 0), (1, 0))
        .segment((1, 1))
        .segment(1, 180)
        .close()
        .assemble()
    )

    assert len(s1._faces.Faces()) == 1
    assert s1._faces.Area() == approx(1)

    s2 = Sketch().arc((0, 0), (1, 1), (0, 2)).close().assemble()

    assert len(s2._faces.Faces()) == 1
    assert s2._faces.Area() == approx(pi / 2)

    s3 = Sketch().arc((0, 0), (1, 1), (0, 2)).arc((-1, 1), (0, 0)).assemble()

    assert len(s3._faces.Faces()) == 1
    assert s3._faces.Area() == approx(pi)


def test_assemble():

    s1 = Sketch()
    s1.segment((0.0, 0), (0.0, 2.0))
    s1.segment(Vector(4.0, -1)).close().arc((0.7, 0.6), 0.4, 0.0, 360.0).assemble()


def test_finalize():

    parent = object()
    s = Sketch(parent).rect(2, 2).circle(0.5, mode="s")

    assert s.finalize() is parent


def test_misc():

    with raises(ValueError):
        Sketch()._startPoint()

    with raises(ValueError):
        Sketch()._endPoint()


def test_constraint_validation():

    with raises(ValueError):
        Sketch().segment(1.0, 1.0, "s").constrain("s", "Dummy", None)

    with raises(ValueError):
        Sketch().segment(1.0, 1.0, "s").constrain("s", "s", "Fixed", None)

    with raises(ValueError):
        Sketch().spline([(1.0, 1.0), (2.0, 1.0), (0.0, 0.0)], "s").constrain(
            "s", "Fixed", None
        )

    with raises(ValueError):
        Sketch().segment(1.0, 1.0, "s").constrain("s", "Fixed", 1)


def test_constraint_solver():

    s1 = (
        Sketch()
        .segment((0.0, 0), (0.0, 2.0), "s1")
        .segment((0.5, 2.5), (1.0, 1), "s2")
        .close("s3")
    )
    s1.constrain("s1", "Fixed", None)
    s1.constrain("s1", "s2", "Coincident", None)
    s1.constrain("s2", "s3", "Coincident", None)
    s1.constrain("s3", "s1", "Coincident", None)
    s1.constrain("s3", "s1", "Angle", pi / 2)
    s1.constrain("s2", "s3", "Angle", pi - pi / 4)

    s1.solve()

    assert s1._solve_status["status"] == 4

    s1.assemble()

    assert s1._faces.isValid()

    s2 = (
        Sketch()
        .arc((0.0, 0.0), (-0.5, 0.5), (0.0, 1.0), "a1")
        .arc((0.0, 1.0), (0.5, 1.5), (1.0, 1.0), "a2")
        .segment((1.0, 0.0), "s1")
        .close("s2")
    )

    s2.constrain("s2", "Fixed", None)
    s2.constrain("s1", "s2", "Coincident", None)
    s2.constrain("a2", "s1", "Coincident", None)
    s2.constrain("s2", "a1", "Coincident", None)
    s2.constrain("a1", "a2", "Coincident", None)
    s2.constrain("s1", "s2", "Angle", pi / 2)
    s2.constrain("s2", "a1", "Angle", pi / 2)
    s2.constrain("a1", "a2", "Angle", -pi / 2)
    s2.constrain("a2", "s1", "Angle", pi / 2)
    s2.constrain("s1", "Length", 0.5)
    s2.constrain("a1", "Length", 1.0)

    s2.solve()

    assert s2._solve_status["status"] == 4

    s2.assemble()

    assert s2._faces.isValid()

    s2._tags["s1"][0].Length() == approx(0.5)
    s2._tags["a1"][0].Length() == approx(1.0)

    s3 = (
        Sketch()
        .arc((0.0, 0.0), (-0.5, 0.5), (0.0, 1.0), "a1")
        .segment((1.0, 0.0), "s1")
        .close("s2")
    )

    s3.constrain("s2", "Fixed", None)
    s3.constrain("a1", "ArcAngle", pi / 3)
    s3.constrain("a1", "Radius", 1.0)
    s3.constrain("s2", "a1", "Coincident", None)
    s3.constrain("a1", "s1", "Coincident", None)
    s3.constrain("s1", "s2", "Coincident", None)

    s3.solve()

    assert s3._solve_status["status"] == 4

    s3.assemble()

    assert s3._faces.isValid()

    s3._tags["a1"][0].radius() == approx(1)
    s3._tags["a1"][0].Length() == approx(pi / 3)

    s4 = (
        Sketch()
        .arc((0.0, 0.0), (-0.5, 0.5), (0.0, 1.0), "a1")
        .segment((1.0, 0.0), "s1")
        .close("s2")
    )

    s4.constrain("s2", "Fixed", None)
    s4.constrain("s1", "Orientation", (-1.0, -1.0))
    s4.constrain("s1", "s2", "Distance", (0.0, 0.5, 2.0))
    s4.constrain("s2", "a1", "Coincident", None)
    s4.constrain("a1", "s1", "Coincident", None)
    s4.constrain("s1", "s2", "Coincident", None)

    s4.solve()

    assert s4._solve_status["status"] == 4

    s4.assemble()

    assert s4._faces.isValid()

    seg1 = s4._tags["s1"][0]
    seg2 = s4._tags["s2"][0]

    assert (seg1.endPoint() - seg1.startPoint()).getAngle(Vector(-1, -1)) == approx(
        0, abs=1e-9
    )

    midpoint = (seg2.startPoint() + seg2.endPoint()) / 2

    (midpoint - seg1.startPoint()).Length == approx(2)

    s5 = (
        Sketch()
        .segment((0, 0), (0, 3.0), "s1")
        .arc((0.0, 0), (1.5, 1.5), (0.0, 3), "a1")
        .arc((0.0, 0), (-1.0, 1.5), (0.0, 3), "a2")
    )

    s5.constrain("s1", "Fixed", None)
    s5.constrain("s1", "a1", "Distance", (0.5, 0.5, 3.0))
    s5.constrain("s1", "a1", "Distance", (0.0, 1.0, 0.0))
    s5.constrain("a1", "s1", "Distance", (0.0, 1.0, 0.0))
    s5.constrain("s1", "a2", "Coincident", None)
    s5.constrain("a2", "s1", "Coincident", None)
    s5.constrain("a1", "a2", "Distance", (0.5, 0.5, 10.5))

    s5.solve()

    assert s5._solve_status["status"] == 4

    mid0 = s5._edges[0].positionAt(0.5)
    mid1 = s5._edges[1].positionAt(0.5)
    mid2 = s5._edges[2].positionAt(0.5)

    assert (mid1 - mid0).Length == approx(3)
    assert (mid1 - mid2).Length == approx(10.5)

    s6 = (
        Sketch()
        .segment((0, 0), (0, 3.0), "s1")
        .arc((0.0, 0), (5.5, 5.5), (0.0, 3), "a1")
    )

    s6.constrain("s1", "Fixed", None)
    s6.constrain("s1", "a1", "Coincident", None)
    s6.constrain("a1", "s1", "Coincident", None)
    s6.constrain("a1", "s1", "Distance", (None, 0.5, 0.0))

    s6.solve()

    assert s6._solve_status["status"] == 4

    mid0 = s6._edges[0].positionAt(0.5)
    mid1 = s6._edges[1].positionAt(0.5)

    assert (mid1 - mid0).Length == approx(1.5)
