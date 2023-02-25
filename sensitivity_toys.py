#!/usr/bin/env python
import pyhf
from optparse import OptionParser
from numpy import random

def discovery_from_calculator(model, data, seed, calc_type="asymptotics", **kwargs):
    random.seed(seed)
    calculator = pyhf.infer.utils.create_calculator(
        calc_type, data, model, test_stat="q0", track_progress=False, **kwargs
    )
    sig_plus_bkg_dist, bkg_dist = calculator.distributions(0.0)

    return sig_plus_bkg_dist, bkg_dist


# Options
parser = OptionParser()
parser.add_option("-l", "--luminosity",   dest='luminosity',
                  default=10000, help="luminosity")
parser.add_option("-s", "--signal",   dest='signal',
                  default=3.92, help="signal yield")
parser.add_option("-b", "--background",   dest='background',
                  default=0.16, help="background yield")
parser.add_option("-u", "--uncertainty",   dest='uncertainty',
                  default=0.1, help="background uncertainty")
parser.add_option("-n", "--ntoys",   dest='ntoys',
                  default=100, help="number of toys")
parser.add_option("-i", "--iseed",   dest='seed',
                  default=1234, help="integer seed")
parser.add_option("--process", help="process", default="hino")
parser.add_option("--selection", help="selection", default="2T")
(options, args) = parser.parse_args()

# parse the inputs
s = float(options.signal)*float(options.luminosity)/10000.
b = float(options.background)*float(options.luminosity)/10000.
sigma = float(options.uncertainty)

model = pyhf.simplemodels.uncorrelated_background(
    signal=[s], bkg=[b], bkg_uncertainty=[b*sigma]
)
observations = [s + b]
data = pyhf.tensorlib.astensor(observations + model.config.auxdata)

sig_plus_bkg_dist, bkg_dist = discovery_from_calculator(
    model, data, int(options.seed), calc_type="toybased", ntoys=int(options.ntoys))

baseDir = "/nfs/dust/atlas/user/fmeloni/MuonCollider"
filename = "hypo_"+str(options.process)+"_"+str(options.selection)+"_"+str(options.seed)+"_"+str(round(float(options.luminosity),2))+".txt"
fout = open(baseDir+"/Data/hypotests/"+filename,"w+")

for element in sig_plus_bkg_dist.samples:
    fout.write(str(element) + " ")
fout.write("\n")
for element in bkg_dist.samples:
    fout.write(str(element) + " ")
