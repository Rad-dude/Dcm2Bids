# -*- coding: utf-8 -*-


import logging
import os
import shutil
from distutils.version import LooseVersion
from glob import glob
from .utils import DEFAULT, run_shell_command


class Dcm2niix(object):
    """ Object to handle dcm2niix execution

    Args:
        dicomDirs (list): A list of folder with dicoms to convert
        bidsDir (str): A path to the root BIDS directory
        participant: Optional Participant object
        options (str): Optional arguments for dcm2niix

    Properties:
        sidecars (list): A list of sidecar path created by dcm2niix
    """

    def __init__(self, dicomDirs, bidsDir, participant=None,
            options=DEFAULT.dcm2niixOptions):
        self.logger = logging.getLogger(__name__)

        self.sidecarsFiles = []

        self.dicomDirs = dicomDirs
        self.bidsDir = bidsDir
        self.participant = participant
        self.options = options


    @property
    def outputDir(self):
        """
        Returns:
            A directory to save all the output files of dcm2niix
        """
        if self.participant:
            tmpDir = self.participant.prefix
        else:
            tmpDir = DEFAULT.helperDir
        return os.path.join(self.bidsDir, DEFAULT.tmpDirName, tmpDir)


    def run(self, force=False):
        """ Run dcm2niix if necessary

        Args:
            force (boolean): Forces a cleaning of a previous execution of
                             dcm2niix

        Sets:
            sidecarsFiles (list): A list of sidecar path created by dcm2niix
        """
        try:
            oldOutput = os.listdir(self.outputDir) != []
        except:
            oldOutput = False

        if oldOutput and force:
            self.logger.warning("Previous dcm2niix directory output found:")
            self.logger.warning(self.outputDir)
            self.logger.warning("'force' argument is set to True")
            self.logger.warning(
                    "Cleaning the previous directory and running dcm2niix")

            shutil.rmtree(self.outputDir, ignore_errors=True)

            #os.makedirs(self.outputDir, exist_ok=True)
            #python2 compatibility
            if not os.path.exists(self.outputDir):
                os.makedirs(self.outputDir)

            self.execute()

        elif oldOutput:
            self.logger.warning("Previous dcm2niix directory output found:")
            self.logger.warning(self.outputDir)
            self.logger.warning("Use --forceDcm2niix to rerun dcm2niix")

        else:
            #os.makedirs(self.outputDir, exist_ok=True)
            #python2 compatibility
            if not os.path.exists(self.outputDir):
                os.makedirs(self.outputDir)

            self.execute()

        self.sidecarFiles = glob(os.path.join(self.outputDir, "*.json"))

        return os.EX_OK


    def execute(self):
        """ Execute dcm2niix for each directory in dicomDirs
        """
        self.version()
        for dicomDir in self.dicomDirs:
            commandTpl = "dcm2niix {} -o {} {}"
            cmd = commandTpl.format(self.options, self.outputDir, dicomDir)
            output = run_shell_command(cmd)
            self.logger.info("\n" + output.decode())


    @staticmethod
    def version():
        """
        Returns:
            A string of the version of dcm2niix install on the system
        """
        logger = logging.getLogger(__name__)

        try:
            output = run_shell_command("dcm2niix")

        except:
            logger.error("dcm2niix does not appear to be installed")
            logger.error("See: https://github.com/rordenlab/dcm2niix")
            raise

        output = output.decode().split("\n")[0].split()
        version = output[output.index('version')+1]

        #check version
        if LooseVersion(version) < LooseVersion(DEFAULT.dcm2niixVersion):
            logger.error(
                    "Your version of dcm2niix is older than {}".format(
                        DEFAULT.dcm2niixVersion))
            logger.error("See: https://github.com/rordenlab/dcm2niix")
            raise Exception("Old dcm2niix version")

        return version

