import setuptools

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aries_python",
    python_requires=">=3.6",
    version="0.4.1",
    description='An unofficial telnet wrapper for "ARIES / LYNX" motor controller by Kohzu Precision Co.,Ltd.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=['aries'],
    entry_points={"console_scripts": ["aries= aries:main"]},
    author="2-propanol",
    author_email="nuclear.fusion.247@gmail.com",
    url="https://github.com/2-propanol/aries_python",
)
