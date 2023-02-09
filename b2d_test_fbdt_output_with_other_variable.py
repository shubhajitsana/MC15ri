#!/usr/bin/env python3
import sys
import basf2 as b2
import modularAnalysis as ma
# import stdV0s
import flavorTagger as ft
from variables import variables as vm  # shorthand for VariableManager
import variables.collections as vc
import variables.utils as vu
import vertex as vx

# get input file number from the command line
file_name = sys.argv[1]
if "sub00/" in file_name :
    file_number = file_name.split("sub00/")
else :
    file_number = file_name.split("sub01/")
input_filename = file_number[1]

# get output folder name from the command line
output_foldername = sys.argv[2]
output_filename = input_filename

# weight file
weightfile = sys.argv[3]
#################################################################################

# set analysis global tag (needed for flavor tagging) [S10]
b2.conditions.prepend_globaltag(ma.getAnalysisGlobaltag())  # [E10]

# Perform analysis.
main = b2.create_path()

ma.inputMdstList(environmentType="default",filelist=f"{file_name}",path=main)


# fill final state particle lists
ma.fillParticleList("pi+", "abs(d0)<0.2 and abs(z0)<1 and cosTheta >= -0.6", path=main)
ma.fillParticleList("K+", "abs(d0)<0.2 and abs(z0)<1 and cosTheta >= -0.6", path=main)


ma.reconstructDecay("anti-D0 -> K+ pi-",cut="1.84 < M < 1.89",path=main)
ma.matchMCTruth("anti-D0", path=main)
vx.kFit("anti-D0", conf_level=0.0, fit_type='massvertex', path=main)

ma.reconstructDecay("B+ -> [anti-D0 -> K+ pi-] pi+ pi- pi+",cut="5.2 < Mbc < 5.3 and abs(deltaE) < 0.3",path=main)
ma.matchMCTruth("B+", path=main)


ma.buildRestOfEvent(target_list_name="B+", path=main)
cleanMask = ("cleanMask", "nCDCHits > 0 and useCMSFrame(p)<=3.2", "p >= 0.05 and useCMSFrame(p)<=3.2")
ma.appendROEMasks(list_name="B+", mask_tuples=[cleanMask], path=main)
ma.buildContinuumSuppression(list_name="B+", roe_mask="cleanMask", path=main) 
vx.kFit("B+", conf_level=0.0, fit_type='vertex', path=main)
vx.TagV("B+", 'breco', path=main)
ft.flavorTagger(["B+"], path=main)
ma.buildEventShape(inputListNames=["B+"], path=main)



main.add_module(
    "MVAExpert",
    listNames=["B+"],
    extraInfoName="ContinuumProbability",
    identifier=f"{weightfile}",  # name of the weightfile used
)
simpleCSVariables = [
    # "DeltaZ",
    "R2",
    "thrustBm",
    "thrustOm",
    "cosTBTO",
    "cosTBz",
    # "KSFWVariables(et)",
    # "KSFWVariables(mm2)",
    # "KSFWVariables(hso00)",
    # "KSFWVariables(hso01)",  # has some issue
    # "KSFWVariables(hso02)",
    # "KSFWVariables(hso03)",  # has some issue
    # "KSFWVariables(hso04)",
    "KSFWVariables(hso10)",
    "KSFWVariables(hso12)",
    # "KSFWVariables(hso14)",
    "KSFWVariables(hso20)",
    # "KSFWVariables(hso22)",
    # "KSFWVariables(hso24)",
    "KSFWVariables(hoo0)",
    # "KSFWVariables(hoo1)",
    # "KSFWVariables(hoo2)",
    # "KSFWVariables(hoo3)",
    # "KSFWVariables(hoo4)",
    # "CleoConeCS(1)",
    # "CleoConeCS(2)",
    # "CleoConeCS(3)",
    # "CleoConeCS(4)",
    # "CleoConeCS(5)",
    # "CleoConeCS(6)",
    # "CleoConeCS(7)",
    # "CleoConeCS(8)",
    # "CleoConeCS(9)",
]
vm.addAlias("ContProb", "extraInfo(ContinuumProbability)")
# Create list of variables to save into the output file
vm.addAlias('PID_bin_kaon', 'ifNANgiveX(pidPairProbabilityExpert(321, 211, ALL), 0.5)')
vm.addAlias('PID_bin_pion', 'ifNANgiveX(pidPairProbabilityExpert(211, 321, ALL), 0.5)')
vm.addAlias('TOP_bin_kaon', 'ifNANgiveX(pidPairProbabilityExpert(321, 211, TOP), 0.5)')
vm.addAlias('TOP_bin_pion', 'ifNANgiveX(pidPairProbabilityExpert(211, 321, TOP), 0.5)')
vm.addAlias('ARICH_bin_kaon', 'ifNANgiveX(pidPairProbabilityExpert(321, 211, ARICH), 0.5)')
vm.addAlias('ARICH_bin_pion', 'ifNANgiveX(pidPairProbabilityExpert(211, 321, ARICH), 0.5)')
# vm.addAlias('channelID', 'extraInfo(decayModeID)')
vm.addAlias('genGrandMotherPDG', 'genMotherPDG(1)')
vm.addAlias('genGrandMotherID', 'genMotherID(1)')
vm.addAlias('genGrandGrandMotherPDG', 'genMotherPDG(2)')
vm.addAlias('genGrandGrandMotherID', 'genMotherID(2)')
vm.addAlias('CMS_phi', 'useCMSFrame(phi)')
vm.addAlias('chiSqrd', 'extraInfo(chiSquared)')
vm.addAlias('fitNdf', 'extraInfo(ndf)')

# In efficient way
cms_var = vu.create_aliases(vc.kinematics+vc.inv_mass, "useCMSFrame({variable})", prefix = "CMS")


b_vars = []
standard_vars = vc.kinematics + vc.mc_kinematics + vc.mc_truth
b_vars += standard_vars
my_var = vc.inv_mass + vc.deltae_mbc
b_vars += my_var


b_vars += simpleCSVariables
b_vars += vc.tag_vertex
b_vars += vc.mc_tag_vertex
b_vars += vc.vertex
b_vars += vc.event_shape
b_vars += ft.flavor_tagging

########################extra####################################
# TRACK Variables for final states (electrons, positrons, pions)
#: Variables for tracks
track_variables = ['theta',
                   'cosTheta',
                   'phi',
                   'charge',
                   'PID_bin_kaon',
                   'PID_bin_pion',
                   'TOP_bin_kaon',
                   'TOP_bin_pion',
                   'electronID', 'muonID', 'pionID', 'kaonID', 'protonID',
                   'inTOPAcceptance',
                   'thetaInCDCAcceptance',
                   'genMotherID',
                   'genMotherPDG',
                   'genGrandMotherID',
                   'genGrandMotherPDG',
                   'genGrandGrandMotherID',
                   'genGrandGrandMotherPDG',
                   'genParticleID',
                   'isCloneTrack',
                   'mcPDG'] + vc.track + vc.track_hits + standard_vars + cms_var
b_vars += vu.create_aliases_for_selected(
    track_variables,
    "B+ -> [anti-D0 -> ^K+ ^pi-] ^pi+ ^pi- ^pi+",
    prefix=["Kp", "pim_D", "pip1", "pim", "pip2"],
)

D_var = vc.inv_mass + vc.deltae_mbc + vc.mc_truth + vc.vertex + vc.mc_vertex + ['chiSqrd', 'fitNdf']
b_vars += vu.create_aliases_for_selected(
    D_var,
    "B+ -> [^anti-D0 -> K+ pi-] pi+ pi- pi+",
    prefix=["D0_bar"],
)

b_vars += vc.roe_kinematics + vc.roe_multiplicities


########################################################
# b_vars += vmc.mc_gen_topo(200),     # this variabe contains Topological information
########################extra####################################


ma.variablesToNtuple(
    decayString="B+",
    variables=b_vars +["ContProb", "isContinuumEvent"],
    filename=f"{output_foldername}/{output_filename}",
    treename="tree",
    path=main,
)

b2.process(main)