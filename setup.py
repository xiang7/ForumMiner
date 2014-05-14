from setuptools import setup
import tests

setup(
	name='ForumMiner',
	version='0.0dev',
	install_requires = ['esmre','nltk','mpi4py'],
	author='Luojie Xiang',
	test_suite="tests.tests"
	)
