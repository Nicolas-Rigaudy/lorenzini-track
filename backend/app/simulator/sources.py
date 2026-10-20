"""Published sources behind the simulator's parameters.

Every parameter that comes from the literature names its source key in a comment next to the
constant. Parameters with no published value for scalloped hammerheads are marked
"assumption" instead, and listed in docs/simulator.md with the reason for the chosen value.
"""

SOURCES: dict[str, str] = {
    "anderson2025": (
        "Anderson BN, Hammerschlag N, Saul S, Dodd JF, Bowlby HD, Kang Y, Gallagher AJ, "
        "Sulikowski JA (2025) Life stage and seasonal habitat use of the porbeagle Lamna nasus "
        "in the Northwest Atlantic Ocean. Frontiers in Marine Science 12. "
        "doi:10.3389/fmars.2025.1553509"
    ),
    "costa2010": (
        "Costa DP, Robinson PW, Arnould JPY, et al. (2010) Accuracy of ARGOS locations of pinnipeds at-sea estimated using Fastloc GPS. PLoS ONE 5(1): e8677. "
        "doi:10.1371/journal.pone.0008677"
    ),
    "heithaus2007": (
        "Heithaus MR, Wirsing AJ, Dill LM, Heithaus LI (2007) Long-term movements of tiger "
        "sharks satellite-tagged in Shark Bay, Western Australia. Marine Biology. "
        "doi:10.1007/s00227-006-0583-y"
    ),
    "huveneers2016": (
        "Huveneers C, Simpfendorfer CA, Kim S, et al. (2016) The influence of environmental parameters on the performance and detection range of acoustic receivers. "
        "Methods in Ecology and Evolution 7(7): 825-835. doi:10.1111/2041-210X.12520"
    ),
    "jonsen2005": (
        "Jonsen ID, Mills Flemming J, Myers RA (2005) Robust state-space modeling of animal "
        "movement data. Ecology 86(11): 2874-2880. doi:10.1890/04-1852"
    ),
    "kessel2014": (
        "Kessel ST, Cooke SJ, Heupel MR, et al. (2014) A review of detection range testing in aquatic passive acoustic telemetry studies. "
        "Reviews in Fish Biology and Fisheries 24: 199-218. doi:10.1007/s11160-013-9328-4"
    ),
    "salinas2025": (
        "Salinas-de-Leon P, Vaudo J, Suarez-Moncada J, Shivji M (2025) Long-distance movements "
        "of a scalloped hammerhead shark connect the Galapagos Islands with coastal areas and "
        "international waters of the Tropical Eastern Pacific. Environmental Biology of Fishes "
        "108(8): 1287-1293. doi:10.1007/s10641-025-01717-4"
    ),
    "selby2016": (
        "Selby TH, Hart KM, Fujisaki I, et al. (2016) Can you hear me now? Range-testing a submerged passive acoustic receiver "
        "array in a Caribbean coral reef habitat. Ecology and Evolution 6(14): 4823-4835. "
        "doi:10.1002/ece3.2228"
    ),
    "wells2018": (
        "Wells RJD, TinHan TC, Dance MA, et al. (2018) Movement, behavior, and habitat "
        "use of a marine apex predator, the scalloped hammerhead. Frontiers in Marine Science "
        "5: 321. doi:10.3389/fmars.2018.00321"
    ),
}
