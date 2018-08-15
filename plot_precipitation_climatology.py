import pdb
import argparse
#import calendar

import numpy as np
import matplotlib.pyplot as plt
import iris
import iris.plot as iplt
import iris.coord_categorisation
import cmocean

# next block would be self-published

def read_data(fname, month):
    """Read an input data file"""
    
    cube = iris.load_cube(fname, 'precipitation_flux')
    
#    pdb.set_trace() 
    #add tracer; pause code here when loading for debugging
    # type 'next' for next pdb; 'c' to run to completion
    
    iris.coord_categorisation.add_month(cube, 'time')
    cube = cube.extract(iris.Constraint(month=month))
    
    return cube


def mask_data(cube, fname, realm):
    """mask data over land or ocean, specifying realm"""
    
    cube.data = np.ma.asarray(cube.data) #ensure maskable data
    sftlf_cube = iris.load_cube(fname, 'land_area_fraction')
    if realm == 'ocean':
        cube.data.mask = np.where(sftlf_cube.data < 50, True, False) #vectorised argument to create mask
    elif realm == 'land': 
        cube.data.mask = np.where(sftlf_cube.data > 50, True, False)
    return(cube)
    
    
def convert_pr_units(cube):
    """Convert kg m-2 s-1 to mm day-1"""
    
    assert cube.units=='kg m-2 s-1', 'units of initial data should be kg m-2 s-1'
    
    cube.data = cube.data * 86400
    cube.units = 'mm/day'
    
    return cube


def plot_data(cube, month, gridlines=False, levels=None):
    """Plot the data."""
        
    fig = plt.figure(figsize=[12,5])    
    iplt.contourf(cube, levels=levels, cmap=cmocean.cm.haline_r, extend='max')

    plt.gca().coastlines()
    if gridlines:
        plt.gca().gridlines()
    cbar = plt.colorbar()
    cbar.set_label(str(cube.units))
    
    title = '%s precipitation climatology (%s)' %(cube.attributes['model_id'], month)
    plt.title(title)


def main(inargs):
    """Run the program."""

    cube = read_data(inargs.infile, inargs.month)   
    cube = convert_pr_units(cube)
    if type(inargs.mask) is list:
        assert inargs.mask[1]=='land' or inargs.mask[1]=='ocean', 'mask should specify land or ocean'
        cube = mask_data(cube, inargs.mask[0], inargs.mask[1])
    clim = cube.collapsed('time', iris.analysis.MEAN)
    plot_data(clim, inargs.month, inargs.gridlines, inargs.cbar_levels)
    plt.savefig(inargs.outfile)


if __name__ == '__main__':
    description = 'Plot the precipitation climatology for a given month.'
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument("infile", type=str, help="Input file name")
    
#    parser.add_argument("month", type=str, choices=['Jan','Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], help="Month to plot")
    import calendar
    parser.add_argument("month", type=str, choices=calendar.month_abbr[1:], help="Month to plot")

    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("-g", "--gridlines", help="add gridlines", default=False, 
                        action="store_true")
    
    parser.add_argument("-m", "--mask", type=str, nargs=2, metavar=('SFTLF_FILE','REALM'), default=None,
                        help="apply land or ocean mask (specify realm to mask)")
   
    parser.add_argument("-l", "--cbar_levels", type=float, nargs='*', default=None, 
                        help='list of levels / tick marks to appear on the colorbar')#list of float numbers, as in: 0 1 2 3 4 5 6
#    parser.add_argument("-l", "--cbar_levels", type=float, nargs=3, default=None, 
#                      help='list of levels / tick marks to appear on the colorbar')#list of float numbers, as in: 0 1 2 3 
    
    
    args = parser.parse_args()
    
    main(args)
