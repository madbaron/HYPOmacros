#!/usr/bin/env python
import pyhf
from optparse import OptionParser


def discovery_from_calculator(model, data, calc_type="asymptotics", **kwargs):
    calculator = pyhf.infer.utils.create_calculator(
        calc_type, data, model, test_stat="q0", track_progress=False, **kwargs
    )
    test_stat = calculator.teststatistic(0.0)
    sig_plus_bkg_dist, bkg_dist = calculator.distributions(0.0)

    pvalues = calculator.pvalues(test_stat, sig_plus_bkg_dist, bkg_dist)

    return pvalues


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
                  default=1000000, help="number of toys")
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

p_toys = discovery_from_calculator(
    model, data, calc_type="toybased", ntoys=int(options.ntoys))

#p_toys = discovery_from_calculator(
#    model, data, calc_type="asymptotics")

print(str(options.luminosity) + " " + str(p_toys[2]))
