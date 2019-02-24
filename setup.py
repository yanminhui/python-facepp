from setuptools import setup, find_packages


exec(open('facepplib/version.py').read())

setup(name='python-facepp',
      version=globals()['__version__'],
      keywords='face++ faceplusplus facepp python-facepp facepplib',
      description='Library for communicating with a Face++ facial recognition service',
      long_description=open('README.rst').read() + '\n\n' + open('CHANGELOG.rst').read(),
      packages=find_packages(),

      url='https://github.com/yanminhui/python-facepp',
      license='MIT License',
      author='yanminhui',
      author_email='yanminhui163@163.com',

      python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
      install_requires=['requests>=2.20.0'],

      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
          'Topic :: Internet :: WWW/HTTP',
          'Intended Audience :: Developers',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: Implementation :: CPython'
      ],
      zip_safe=False)
