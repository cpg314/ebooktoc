from setuptools import setup
import time

with open('requirements.txt', 'r') as f:
    requirements = [l.strip().strip('\n') for l in f.readlines() if l.strip() and not l.strip().startswith('#')]

setup(name="ebooktoc",
      version=int(time.time()),
      author="cpg314",
      license="MIT",
      packages=["commandline", "document", "processor", "segmenterocr", "tests", "utils"],
      entry_points={"console_scripts": "ebooktoc={0}.{0}:main".format("commandline")},
      install_requires=requirements,
      zip_safe=False)
