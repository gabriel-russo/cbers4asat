from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
        name='cbers4asat',
        version='0.5',
        description='Biblioteca Python para consultar o catálogo e realizar operações com dados do CBERS4A',
        url='https://github.com/gabriel-russo/cbers4asat',
        author='Gabriel Russo',
        author_email='gabrielrusso@protonmail.com',
        license='MIT',
        license_files='LICENSE',
        long_description=long_description,
        long_description_content_type="text/markdown",
        classifiers=[
                "Programming Language :: Python :: 3.7",
                "Programming Language :: Python :: 3.8",
                "Programming Language :: Python :: 3.9",
                "Programming Language :: Python :: 3.10",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent",
                "Topic :: Scientific/Engineering :: GIS",
                "Development Status :: 3 - Alpha"
        ],
        packages=find_packages(),
        install_requires=[
                "geopandas >= 0.9",
                "requests >= 2.25.1",
                "pandas >= 1.3.5"
        ]
)
