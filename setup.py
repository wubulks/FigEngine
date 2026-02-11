from setuptools import setup, find_packages

setup(
    name="figengine",
    version="1.1.0",
    description="High-Performance Structured Figure Engine",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Omarjan Obulkasim @ SYSU",
    author_email="wubulks@mail2.sysu.edu.cn",
    license="MIT",  
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy",
        "pillow",
        "matplotlib",
        "PyYAML",
        "pdf2image",
    ],
    extras_require={
        "dev": [
            "pytest>=7",
            "ruff>=0.6",
            "mypy>=1.8",
            "build>=1.2",
            "twine>=5.0",
        ]
    },
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True, 
    package_data={
        "figengine": [
            "examples/*",
            "examples/gallery/*",
        ]
    },
)
