def run_pytest(name, srcs, deps=None, data=None, size=None):
    code = """
import os
import pytest
import sys

if __name__ == "__main__":
    sys.exit(pytest.main([f for f in os.listdir(".") if f.endswith(".py")]))
"""

    native.genrule(
        name = "generate_%s_file" % name,
        srcs = [],
        outs = ["%s.py" % name],
        cmd = "echo '%s' > $@" % code,
    )

    native.py_test(
        name = name,
        srcs = ["%s.py" % name] + srcs,
        data = data,
        deps = deps,
        size = size
    )

