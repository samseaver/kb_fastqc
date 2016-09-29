# -*- coding: utf-8 -*-
import unittest
import os,sys
import json
import time
import requests
import subprocess

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint

from biokbase.workspace.client import Workspace as workspaceService
from kb_fastqc.kb_fastqcImpl import kb_fastqc
from kb_fastqc.kb_fastqcServer import MethodContext


class kb_fastqcTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        user_id = requests.post(
            'https://kbase.us/services/authorization/Sessions/Login',
            data='token={}&fields=user_id'.format(token)).json()['user_id']
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
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_fastqc'):
            cls.cfg[nameval[0]] = nameval[1]
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL, token=token)
        cls.serviceImpl = kb_fastqc(cls.cfg)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_kb_fastqc_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    # NOTE: According to Python unittest naming rules test method names should start from 'test'.
    def test_local_fastqc(self):
        #This assumes, and apparently rightly so, that we're still in the /kb/module/test directory
        output = subprocess.check_output(["fastqc", "test_1.fastq.gz"])
        self.assertTrue("Analysis complete" in output)
        pass
        
    def test_fastqc(self):
        #create ws, and load test reads
        #Check WS exists
        #FastQC_WS_Exists = 0
        #workspaces = self.getWsClient().list_workspace_info({})
        #for record in workspaces:
        #    if("FastQC_Example" in record[1]):
        #        FastQC_WS_Exists = 1
        #        break
        #if(FastQC_WS_Exists == 0):
        #    self.getWsClient().create_workspace({"workspace":"FastQC_Example"})
        #else:
        #    print("FastQC_Example workspace exists")

        input_params={'input_ws':'FastQC_Example','input_file':'FastQC_Sample_Reads'}
        output = self.getImpl().runFastQC(self.getContext(), input_params)
        self.assertTrue("Analysis complete" in output[0])
        pass
