import sys

from _pytest.python import Module


class IsolatedModule(Module):
    def _getobj(self):
        modules = (
            "app",
            "api",
            "auth",
            "database",
            "models",
            "schemas",
            "services",
            "repositories"
        )

        for name in list(sys.modules):
            if any(
                name == module or name.startswith(module + ".")
                for module in modules
            ):
                sys.modules.pop(name, None)

        return super()._getobj()


def pytest_pycollect_makemodule(module_path, parent):
    return IsolatedModule.from_parent(
        parent,
        path=module_path
    )