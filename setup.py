import setuptools

from bandcamp_name_your_price_dl import __desc__, __version__


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="bandcamp_name_your_price_dl",
    version=__version__,
    py_modules=["bandcamp_name_your_price_dl"],
    author="Layerex",
    author_email="layerex@dismail.de",
    description=__desc__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Layerex/bandcamp_name_your_price_dl",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Web Environment",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
    entry_points = {
        "console_scripts": [
            "bandcamp_name_your_price_dl = bandcamp_name_your_price_dl:main",
        ],
    },
    install_requires=["selenium", "requests", "pystandardpaths"]
)
