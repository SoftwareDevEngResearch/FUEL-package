import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="FUEL_millerh", # Replace with your own username
    version="0.0.1",
    author="Heather Miller",
    author_email="heathermiller1321@gmail.com",
    description="Visualizing and Analyzing FUEL sensor data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HeatherMM1321/FUEL-package",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
