from __future__ import absolute_import, division, print_function

from spectral_cube import SpectralCube, StokesSpectralCube, VaryingResolutionSpectralCube

from qtpy.compat import getexistingdirectory
from glue.core import Data
from glue.config import data_factory, qglue_parser, importer
from glue.core.data_factories.fits import is_fits
from glue.core.coordinates import coordinates_from_wcs

__all__ = ['read_spectral_cube', 'parse_spectral_cube']


def is_spectral_cube(filename, **kwargs):
    """
    Check that the file is a 3D or 4D FITS spectral cube
    """

    if not is_fits(filename):
        return False

    try:
        StokesSpectralCube.read(filename)
    except Exception:
        return False
    else:
        return True


def spectral_cube_to_data(cube, label=None):

    if isinstance(cube, (SpectralCube, VaryingResolutionSpectralCube)):
        cube = StokesSpectralCube({'I': cube})

    result = Data(label=label)
    result.coords = coordinates_from_wcs(cube.wcs)
    #result.meta = dict(cube.header)

    for component in cube.components:
        data = getattr(cube, component).unmasked_data[...]
        result.add_component(data, label='STOKES {0}'.format(component))

    return result


@data_factory(label='FITS Spectral Cube', identifier=is_spectral_cube)
def read_spectral_cube(filename, **kwargs):
    """
    Read in a FITS spectral cube. If multiple Stokes components are present,
    these are split into separate glue components.
    """
    cube = StokesSpectralCube.read(filename)
    return spectral_cube_to_data(cube)


@qglue_parser((SpectralCube, StokesSpectralCube))
def parse_spectral_cube(cube, label):
    return [spectral_cube_to_data(cube, label=label)]


@importer("Import CASA .image spectral cube")
def import_casa_spectral_cube():

    caption = ('Select .image directory')

    directory = getexistingdirectory(caption=caption)
    if not directory:
        return []

    data = read_spectral_cube(directory)
    data.label = directory.replace('.image', '')

    return [data]
