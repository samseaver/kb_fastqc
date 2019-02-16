# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
import time
import unittest
from configparser import ConfigParser  # py3
from os import environ

from installed_clients.ReadsUtilsClient import ReadsUtils
from installed_clients.WorkspaceClient import Workspace as workspaceService
from kb_fastqc.authclient import KBaseAuth as _KBaseAuth
from kb_fastqc.kb_fastqcImpl import kb_fastqc
from kb_fastqc.kb_fastqcServer import MethodContext


class kb_fastqcTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_fastqc'):
            cls.cfg[nameval[0]] = nameval[1]
        authServiceUrl = cls.cfg.get('auth-service-url',
                "https://kbase.us/services/authorization/Sessions/Login")
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'kb_fastqc',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL, token=token)
        cls.serviceImpl = kb_fastqc(cls.cfg)

        #retrieve and setup test files
        test_fq_filename = "test_1.fastq.gz"
        output = subprocess.check_output(["curl",
                                          "-o",
                                          test_fq_filename,
                                          "http://bioseed.mcs.anl.gov/~seaver/Files/Sample_Reads/WT1_S1_L001_R2_001.fastq.gz"])
        cls.large_fq_test_file1 = os.path.join(cls.cfg['scratch'], test_fq_filename)
        shutil.copy(test_fq_filename, cls.large_fq_test_file1)

        fq_filename = "interleaved.fq"
        cls.small_fq_test_file2 = os.path.join(cls.cfg['scratch'], fq_filename)
        shutil.copy(os.path.join("data", fq_filename), cls.small_fq_test_file2)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            print("Test run on workspace "+cls.wsName)
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_kb_fastqc_" + str(suffix)
        self.getWsClient().create_workspace({'workspace': wsName})
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    # NOTE: According to Python unittest naming rules test method names should start from 'test'.
    def test_local_fastqc(self):
        # This assumes, and apparently rightly so, that we're still in the /kb/module/test directory
        output = subprocess.check_output(["fastqc", self.large_fq_test_file1]).decode()
        self.assertTrue("Analysis complete" in output)
        pass
        
    def test_fastqc_app(self):
        # create ws, and load test reads
        wsName = self.getWsName()
        ru = ReadsUtils(os.environ['SDK_CALLBACK_URL'])
        input_file_ref = ru.upload_reads({'fwd_file': self.small_fq_test_file2,
                                          'sequencing_tech': 'tech1',
                                          'wsname': wsName,
                                          'name': 'reads1',
                                          'interleaved': 1
                                          })['obj_ref']

        input_params = {'input_ws': wsName, 'input_file_ref': input_file_ref}
        output = self.getImpl().runFastQC(self.getContext(), input_params)[0]
        self.assertIn('report_name', output)
        self.assertIn('report_ref', output)
#        pprint(output)

        report = self.getWsClient().get_objects2({'objects': [{'ref': output['report_ref']}]})['data'][0]['data']
#        pprint(report)

        self.assertIn('direct_html', report)
        self.assertIn('file_links', report)
        self.assertIn('html_links', report)
        self.assertIn('objects_created', report)
        self.assertIn('text_message', report)


