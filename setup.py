from setuptools import setup, find_packages

with open('./requirements.txt') as reqs:
    requirements = [line.rstrip() for line in reqs]

with open('./requirements-dev.txt') as devreqs:
    dev_requirements = [line.rstrip() for line in devreqs]

setup(name="lambda_spatial_db",
      version='0.1',
      author='Jeff Albrecht',
      author_email='geospatialjeff@gmail.com',
      packages=find_packages(exclude=['bin', 'layer']),
      install_requires = requirements,
      extras_require= {
          'dev': dev_requirements
      },
      entry_points= {
          "console_scripts": [
              "lambda-db=_cli:lambda_db"
          ]},
      include_package_data=True
      )