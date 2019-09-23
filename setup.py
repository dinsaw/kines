import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kines",
    version="0.0.4",
    author="Dinesh Sawant",
    author_email="dineshsawant300@gmail.com",
    description="Friendly Amazon Kinesis Stream Command Line Interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dinsaw/kines",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=['kines_cli'],
    install_requires=[
        'Click',
        'timeago',
        'boto3',
        'terminaltables',
        'matplotlib',
        'termgraph',
    ],
    entry_points='''
        [console_scripts]
        kines=kines.kines_cli:kines
    ''',
)
