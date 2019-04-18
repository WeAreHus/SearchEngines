#coding:utf-8

from setuptools import setup, find_packages
setup(
    name = "Search",
    version = "0.1",
    author = "Cris",
    packages = find_packages(),
    install_requires = ["BeautifulSoup4", "requests", "urwid"],
    python_requires=">=3",
    include_package_data=True,
    packages = ["search"]
)
