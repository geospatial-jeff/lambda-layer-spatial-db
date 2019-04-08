from setuptools import setup, find_packages

with open('./requirements.txt') as reqs:
    requirements = [line.rstrip() for line in reqs]

setup(name="lambda_spatial_db",
      version='0.1',
      author='Jeff Albrecht',
      author_email='geospatialjeff@gmail.com',
      packages=find_packages(exclude=['bin', 'layer']),
      install_requires = requirements,
      entry_points= {
          "console_scripts": [
              "lambda-db=_cli:lambda_db"
          ]},
      include_package_data=True
      )