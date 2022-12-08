from setuptools.command.build_ext import build_ext
from setuptools import Extension, setup, find_packages
import glob

class custom_build_ext(build_ext):
    def build_extensions(self):
        # Override the compiler executables. Importantly, this
        # removes the "default" compiler flags that would
        # otherwise get passed on to to the compiler, i.e.,
        # distutils.sysconfig.get_var("CFLAGS").
        self.compiler.set_executable("compiler_so", "g++ -fpic")
        self.compiler.set_executable("compiler_cxx", "g++")
        self.compiler.set_executable("linker_so", "g++ -Wl,--gc-sections -shared -lstdc++")
        build_ext.build_extensions(self)


setup(
    name="depth",
    version="1.0.0",
    author="Pavlo mozharovskyi",
    author_email="pavlo.mozharovskyi@telecom-paris.fr",
    description="The package provides many procedures for calculating the depth of points in an empirical distribution for many notions of data depth",
    long_description="The package provides many procedures for calculating the depth of points in an empirical distribution for many notions of data depth",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['numpy','scipy','scikit-learn'],
    include_package_data=True,
    ext_modules=[
        Extension(
            "ddalpha", 
            sources=["depth/src/ddalpha.cpp"],
            extra_compile_args=["-I."],
            extra_link_args=["-rdynamic",'-std=c++14','-fPIC']
        ),Extension(
            "depth_wrapper", 
            sources=["depth/src/depth_wrapper.cpp"],
            extra_compile_args=["-I."],
            extra_link_args=["-rdynamic",'-std=c++14','-fPIC']
        )
     
   	
    ],
    data_files=[('depth/multivariate', glob.glob("depth/multivariate/*.rst"))],
    zip_safe=False,
    cmdclass={"build_ext": custom_build_ext}
)
