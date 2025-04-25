from importlib import import_module

for _mod in ("io", "detect", "ransac", "visualize"):
    import_module(f".{_mod}", __name__)
