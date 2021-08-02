import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pysct", # Replace with your own username
    version="0.0.25",
    author="SAS Institute",
    author_email="eduardo.hellas@sas.com",
    description="Translator for SAS Viya Score code to python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sassoftware/sas-scoring-translator-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[],
)

