#!/usr/bin/env python
import pyhf, os
from optparse import OptionParser
from pyhf.infer.calculators import EmpiricalDistribution
import numpy

# Options
parser = OptionParser()
parser.add_option("--process", help="process", default="hino")
parser.add_option("--selection", help="selection", default="2T")

(options, args) = parser.parse_args()

dirname = "/nfs/dust/atlas/user/fmeloni/MuonCollider/Data/hypotests"

s = 3.92
b = 0.16
u = 0.1

process_list = ["wino", "hino"]
if options.process not in process_list:
    log.error('Unsupported process!')
    exit()

selection_list = ["1T", "2T"]
if options.selection not in selection_list:
    log.error('Unsupported selection!')
    exit()

if options.process == "wino" and options.selection == "1T":
    s = 313
    b = 187.8
    u = 0.1
elif options.process == "wino" and options.selection == "2T":
    s = 168
    b = 0.16
    u = 1.
elif options.process == "hino" and options.selection == "1T":
    s = 53
    b = 187.8
    u = 0.1
elif options.process == "hino" and options.selection == "2T":
    s = 3.92
    b = 0.16
    u = 1.

tag = "hypo_"+str(options.process)+"_"+str(options.selection)

#generate equally spaced points in a log scale
#lumi_vec = numpy.logspace(0., 5., num=50, base=10.0)
lumi_vec = numpy.logspace(2., 5., num=10, base=10.0)

print(str(options.process)+"_"+str(options.selection))

for lumin in lumi_vec:

    lumi = round(lumin,2)
    # parse the inputs
    sig_plus_bkg_list = []
    bkg_list = []
    
    for filename in os.listdir(dirname):
        f = os.path.join(dirname, filename)
        # checking if it is a file
        if (os.path.isfile(f)) and (str(lumi) in filename) and (tag in filename):
            file = open(f)
            contents = file.read()

            # Get the signal yields first
            for item in contents.split('\n')[0].split(" ")[:-1]:
                sig_plus_bkg_list.append(float(item))
            for item in contents.split('\n')[1].split(" ")[:-1]:
                bkg_list.append(float(item))

    sig_plus_bkg_dist = EmpiricalDistribution(sig_plus_bkg_list)
    bkg_dist = EmpiricalDistribution(bkg_list)

    sig = s*lumi/10000.
    bac = b*lumi/10000.
    sigma = u

    model = pyhf.simplemodels.uncorrelated_background(
        signal=[sig], bkg=[bac], bkg_uncertainty=[bac*sigma]
    )
    observations = [sig + bac]
    data = pyhf.tensorlib.astensor(observations + model.config.auxdata)

    calculator = pyhf.infer.utils.create_calculator(
        "toybased", data, model, test_stat="q0", track_progress=False)
    test_stat = calculator.teststatistic(0.0)

    pvalues = calculator.pvalues(test_stat, sig_plus_bkg_dist, bkg_dist)
    print(str(lumi) + " " + str(pvalues[2]))