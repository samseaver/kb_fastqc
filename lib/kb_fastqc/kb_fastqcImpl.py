# -*- coding: utf-8 -*-
#BEGIN_HEADER
import os
import requests,subprocess
from biokbase.workspace.client import Workspace as workspaceService
#END_HEADER


class kb_fastqc:
    '''
    Module Name:
    kb_fastqc

    Module Description:
    A KBase module: kb_fastqc
    '''

    ######## WARNING FOR GEVENT USERS #######
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    #########################################
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/kbaseapps/kb_fastqc"
    GIT_COMMIT_HASH = "ed40d3b420b895f5ac3797ec26470f8773c2c309"
    
    #BEGIN_CLASS_HEADER
    
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.workspaceURL = config['workspace-url']
        self.scratch = os.path.abspath(config['scratch'])
        #END_CONSTRUCTOR
        pass
    

    def runFastQC(self, ctx, input_params):
        """
        :param input_params: instance of type "FastQCParams" -> structure:
           parameter "input_ws" of String, parameter "input_file" of String
        :returns: instance of String
        """
        # ctx is the context object
        # return variables are: encoded_html_string
        #BEGIN runFastQC

        token = ctx['token']
        wsClient = workspaceService(self.workspaceURL, token=token)
        headers = {'Authorization': 'OAuth '+token}

        info=None
        readLibrary=None
        try:
            readLibrary = wsClient.get_objects([{'name': input_params['input_file'],
                                                 'workspace' : input_params['input_ws']}])[0]
            info = readLibrary['info']
            readLibrary = readLibrary['data']
        except Exception as e:
            raise ValueError('Unable to get read library object from workspace: (' + str(input_params['input_ws'])+ '/' + str(input_params['input_file']) +')' + str(e))

        #Check type of read
        reads_type = "SE"
        if("PairedEnd" in info[2]):
            reads_type="PE"

        reads = list()
        if(reads_type == "SE"):
            if 'handle' in readLibrary:
                reads.append(readLibrary['handle'])
            elif 'lib' in readLibrary:
                reads.append(readLibrary['lib']['file'])
        elif(reads_type == "PE"):
            for number in ("1","2"):
                if 'handle_'+number in readLibrary:
                    reads.append(readLibrary['handle_'+number])
                elif 'lib'+number in readLibrary:
                    reads.append(readLibrary['lib'+number]['file'])

        read_file_list=list()
        for read in reads:
            #compose file name
            read_file_name = str(read['id'])
            if 'file_name' in read:
                read_file_name = read['file_name']
            read_file_name=self.scratch+"/"+read_file_name
            read_file_list.append(read_file_name)

            read_file = open(read_file_name, 'w', 0)
            r = requests.get(read['url']+'/node/'+read['id']+'?download', stream=True, headers=headers)
            for chunk in r.iter_content(1024):
                read_file.write(chunk)

        encoded_html_string = subprocess.check_output(["fastqc"]+read_file_list)
        #END runFastQC

        # At some point might do deeper type checking...
        if not isinstance(encoded_html_string, basestring):
            raise ValueError('Method runFastQC return value ' +
                             'encoded_html_string is not type basestring as required.')
        # return the results
        return [encoded_html_string]

    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK", 'message': "", 'version': self.VERSION, 
                     'git_url': self.GIT_URL, 'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
