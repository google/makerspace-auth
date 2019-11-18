from setuptools import setup

with open("authbox/__init__.py") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split()[-1].strip("\"'")
            break
    else:
        raise Exception("Could not determine version from reading authbox/__init__.py")

setup(
    version=version
    # TODO python_requires=
)
