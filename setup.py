import os
from setuptools import setup, find_packages

PREFIX = "inferscope"


def get_version():
    setup_py_dir = os.path.dirname(__file__)
    version_module_path = os.path.join(setup_py_dir, "src", "inferscope", "__version__.py")

    about = {}

    with open(version_module_path) as f:
        exec(f.read(), about)  # noqa

    return about["__version__"]


def setup_package():
    setup(
        name="inferscope",
        version=get_version(),
        author="kizill",
        author_email="staskirillov@gmail.com",
        packages=find_packages("src"),
        package_dir={"": "src"},
        description="Python-package for inferscope mlops service",
        include_package_data=True,
        install_requires=[
            "attr",
            "attrs",
            "httpx[http2]",
            "pydantic>2.0",
        ],
        long_description=open("README.md").read(),
        long_description_content_type='text/markdown',
        python_requires=">=3.9.0",
        keywords=["ml", "mlops"],
    )


if __name__ == "__main__":
    setup_package()
