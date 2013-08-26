#!/usr/bin/python

############################
#
# Plot That Lut
# Version : 0.2
# Author : mfe
#
############################

## imports
from os import path
from os import sys
# OpenColorIO
from PyOpenColorIO import Config, ColorSpace, FileTransform
from PyOpenColorIO.Constants import INTERP_NEAREST, INTERP_LINEAR, INTERP_TETRAHEDRAL, COLORSPACE_DIR_TO_REFERENCE
# matplotlib
import matplotlib

cherryPyMode = True

def setMatplotlibBackend():
    if cherryPyMode:
        matplotlib.use('Agg')
    else:
        matplotlib.use('Qt4Agg')

OCIO_LUTS_FORMATS =     ['.3dl',
                        '.csp',
                        '.cub',
                        '.cube',
                        '.hdl',
                        '.look',
                        '.mga/m3d',
                        '.spi1d',
                        '.spi3d',
                        '.spimtx',
                        '.vf'
                        ]

DEFAULT_SAMPLE = 256
DEFAULT_CUBE_SIZE = 17

def showPlot(fig, filename):
    if cherryPyMode:
        splitFilename =  path.splitext(filename)
        filename = splitFilename[0] + splitFilename[1].replace(".", "_")
        exportPath = 'img/export_'+ filename +'.png'
        print "export figure : " +exportPath
        fig.savefig(exportPath)
        return '<img src="/' + exportPath +'" width="640" height="480" border="0" />'
    else:
        matplotlib.pyplot.show()
        return ""

"""
createOCIOProcessor
lutfile : path to a LUT
interpolation : can be INTERP_NEAREST, INTERP_LINEAR or INTERP_TETRAHEDRAL (only for 3D LUT)
"""
def createOCIOProcessor(lutfile, interpolation):
    config = Config()
    # In colorspace (LUT)
    colorspace = ColorSpace(name='RawInput')
    t = FileTransform(lutfile,interpolation=interpolation)
    colorspace.setTransform(t, COLORSPACE_DIR_TO_REFERENCE)
    config.addColorSpace(colorspace)
    # Out colorspace
    colorspace = ColorSpace(name='ProcessedOutput')
    config.addColorSpace(colorspace)
    # Create a processor corresponding to the LUT transformation
    return config.getProcessor('RawInput', 'ProcessedOutput')

"""
plotCurve
lutfile : path to a color transformation file (lut, matrix...)
samplesCount : number of points for the displayed curve
"""
def plotCurve(lutfile, samplesCount, processor):
    # matplotlib : general plot
    from matplotlib.pyplot import title, plot, xlabel, ylabel, grid, show, figure
    # init vars
    maxValue = samplesCount - 1.0
    redValues = []
    greenValues = []
    blueValues = []
    inputRange = []
    # process color values
    for n in range(0, samplesCount):
        x = n/maxValue
        res = processor.applyRGB([x,x,x])
        redValues.append(res[0])
        greenValues.append(res[1])
        blueValues.append(res[2])
        inputRange.append(x)
    # init plot
    fig = figure()
    fig.canvas.set_window_title('Plot That 1D LUT')
    filename = path.basename(lutfile)
    title(filename)
    xlabel("Input")
    ylabel("Output")
    grid(True)
    # plot curves
    plot(inputRange, redValues, 'r-', label='Red values', linewidth=1)
    plot(inputRange, greenValues, 'g-', label='Green values', linewidth=1)
    plot(inputRange, blueValues, 'b-', label='Blue values', linewidth=1)
    return showPlot(fig, filename)

"""
plotCube
lutfile : path to a color transformation file (lut, matrix...)
cubeSize : number of segments. Ex : If set to 17, 17*17*17 points will be displayed
"""
def plotCube(lutfile, cubeSize, processor):
    # matplotlib : general plot
    from matplotlib.pyplot import title, show, figure
    # matplotlib : for 3D plot
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib.colors import rgb2hex
    # init vars
    inputRange  = range(0, cubeSize)
    maxValue = cubeSize - 1.0
    redValues = []
    greenValues = []
    blueValues = []
    colors = []
    # process color values
    for r in inputRange:
        for g in inputRange:
            for b in inputRange:
                # get a value between [0..1]
                normR = r/maxValue
                normG = g/maxValue
                normB = b/maxValue
                # apply correction via OCIO
                res = processor.applyRGB([normR,normG,normB])
                # append values
                redValues.append(res[0])
                greenValues.append(res[1])
                blueValues.append(res[2])
                # append corresponding color
                colors.append(rgb2hex([normR,normG,normB]))
    # init plot
    fig = figure()
    fig.canvas.set_window_title('Plot That 3D LUT')
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('Red')
    ax.set_ylabel('Green')
    ax.set_zlabel('Blue')
    ax.set_xlim(min(redValues),max(redValues))
    ax.set_ylim(min(greenValues),max(greenValues))
    ax.set_zlim(min(blueValues),max(blueValues))
    filename = path.basename(lutfile)
    title(filename)
    # plot 3D values
    ax.scatter(redValues, greenValues, blueValues, c=colors, marker="o")
    return showPlot(fig, filename)

def testLUT1D():
    lutfile = "testFiles/identity.csp"
    plotCurve(lutfile, samplesCount=DEFAULT_SAMPLE)

def testLUT3D():
    lutfile = "testFiles/identity.3dl"
    plotCube(lutfile, cubeSize=DEFAULT_CUBE_SIZE)

def supportedFormats():
    return "Supported LUT formats : " + ', '.join(OCIO_LUTS_FORMATS)

def help():
    h = "----\n"
    h += "plotThatLut.py <path to a LUT>                               :   dispay a cube ("+ str(DEFAULT_CUBE_SIZE) +" segments) for 3D LUTs and matrixes\n"
    h += "                                                                 or a curve ("+ str(DEFAULT_SAMPLE) +" points) for 1D/2D LUTs.\n"
    h += "plotThatLut.py <path to a LUT> curve [points count]          :   display a curve with x points (default value : "+ str(DEFAULT_SAMPLE) +").\n"
    h += "plotThatLut.py <path to a LUT> cube [cube size]              :   display a cube with x segments (default value : "+ str(DEFAULT_CUBE_SIZE) +").\n"
    h += supportedFormats()
    return h

def plotThatLut(lutfile, plotType=None, count=None):
    setMatplotlibBackend()
    # check if LUT format is supported
    fileext = path.splitext(lutfile)[1]
    if not fileext:
        raise Exception("Error: Couldn't extract extension in this path : "+ lutfile)
    if fileext not in OCIO_LUTS_FORMATS:
        raise Exception( "Error: " + fileext + " file format aren't supported.\n" + supportedFormats())
    # create OCIO processor
    processor = createOCIOProcessor(lutfile, INTERP_LINEAR)
    # init args
    if not plotType or plotType == 'auto':
        if processor.hasChannelCrosstalk() or fileext == '.spimtx':
            plotType = 'cube'
        else:
            plotType = 'curve'
    if not count or count == 'auto' :
        # set plotType from the command line and init default count
        if plotType=='curve':
            count = DEFAULT_SAMPLE
        else:
            count = DEFAULT_CUBE_SIZE
    # plot
    print "Plotting a " + plotType + " with " + str(count) + " samples..."
    if plotType=='curve':
        return plotCurve(lutfile, count, processor)
    elif plotType=='cube':
        return plotCube(lutfile, count, processor)
    else:
        raise Exception( "Unknown plot type : " + plotType + "\n"
        + "Plot type should be curve or cube.\n" + help())

if __name__ == '__main__':
    cherryPyMode = False
    paramsCount = len(sys.argv)
    lutfile =""
    plotType = None
    count = None
    if paramsCount < 2:
        print "Syntax error !"
        print help()
        sys.exit(1)
    elif paramsCount == 2:
        lutfile = sys.argv[1]
    elif paramsCount == 3:
        lutfile = sys.argv[1]
        plotType = sys.argv[2]
    elif paramsCount == 4:
        lutfile = sys.argv[1]
        plotType = sys.argv[2]
        count = int(sys.argv[3])
    else:
        print "Syntax error !"
        print help()
        sys.exit(1)
    try:
        plotThatLut(lutfile, plotType, count)
    except Exception, e:
        print "Watch out !\n%s" % e