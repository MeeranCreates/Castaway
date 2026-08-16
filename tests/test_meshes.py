from src.engine import mesh as mesh_module


def test_make_capsule_builds_a_mesh(monkeypatch):
    monkeypatch.setattr(mesh_module, "glGenVertexArrays", lambda count: 1)
    monkeypatch.setattr(mesh_module, "glGenBuffers", lambda count: 1)
    monkeypatch.setattr(mesh_module, "glBindVertexArray", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(mesh_module, "glBindBuffer", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(mesh_module, "glBufferData", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(mesh_module, "glEnableVertexAttribArray", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(mesh_module, "glVertexAttribPointer", lambda *_args, **_kwargs: None)

    capsule = mesh_module.make_capsule(radius=0.4, height=1.8)

    assert capsule.count > 0
