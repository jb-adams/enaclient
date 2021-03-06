import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="enaclient",
    version="1.0.0",
    author="Jeremy Adams",
    author_email="jeremybr.adams@gmail.com",
    description="Retrieve ENA sequence metadata through refget API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jb-adams/enaclient",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
