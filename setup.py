from setuptools import setup

setup(name='sjm_tools',
      version='1.0',
      description='A simple wrapper for SJM system',
      url='https://github.com/sysuliujh/Bioinfo-toolkit/tree/master/sjm_tools',
      author='Jianheng Liu',
      author_email='sysuliujh@gmail.com',
      license='MIT',
      packages=['sjm_tools'],
      entry_points={'console_scripts': ['qsjm = sjm_tools.qsjm:main']},
      zip_safe=False)