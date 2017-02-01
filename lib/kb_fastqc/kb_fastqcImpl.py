# -*- coding: utf-8 -*-
#BEGIN_HEADER
import os,uuid,sys
import requests,subprocess,shutil
from pprint import pprint
from KBaseReport.KBaseReportClient import KBaseReport
from biokbase.workspace.client import Workspace as workspaceService
from ReadsUtils.ReadsUtilsClient import ReadsUtils
#END_HEADER


class kb_fastqc:
    '''
    Module Name:
    kb_fastqc

    Module Description:
    A KBase module: kb_fastqc
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.2"
    GIT_URL = "git@github.com:msneddon/kb_fastqc"
    GIT_COMMIT_HASH = "72a6925fa0ceccf2853b5d6743adcf31af97a7e7"

    #BEGIN_CLASS_HEADER
    
    def _get_input_file_ref_from_params(self, params):
        if 'input_file_ref' in params:
            return params['input_file_ref']
        else:
            if 'input_ws' not in params and 'input_file' not in params:
                raise ValueError('Either the "input_file_ref" field or the "input_ws" with' +
                                 '"input_file" fields must be set.')
            return str(params['input_ws']) + '/' + str(params['input_file'])

    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.workspaceURL = config['workspace-url']
        self.scratch = os.path.abspath(config['scratch'])
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        #END_CONSTRUCTOR
        pass

    def runFastQC(self, ctx, input_params):
        """
        :param input_params: instance of type "FastQCParams" -> structure:
           parameter "input_ws" of String, parameter "input_file" of String,
           parameter "input_file_ref" of String
        :returns: instance of type "FastQCOutput" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: reported_output
        #BEGIN runFastQC

        token = ctx['token']
        wsClient = workspaceService(self.workspaceURL, token=token)
        headers = {'Authorization': 'OAuth '+token}
        uuid_string = str(uuid.uuid4())
        read_file_path=self.scratch+"/"+uuid_string
        os.mkdir(read_file_path)

        input_file_ref = self._get_input_file_ref_from_params(input_params)

        library=None
        try:
            library = wsClient.get_objects2({'objects': [{'ref': input_file_ref}]})['data'][0]
        except Exception as e:
            raise ValueError('Unable to get read library object from workspace: (' + input_file_ref + ')' + str(e))

        download_read_params = {'read_libraries': [], 'interleaved':"false"}
        if("SingleEnd" in library['info'][2] or "PairedEnd" in library['info'][2]):
            download_read_params['read_libraries'].append(library['info'][7]+"/"+library['info'][1])
        elif("SampleSet" in library['info'][2]):
            for sample_id in library['data']['sample_ids']:
                download_read_params['read_libraries'].append(library['info'][7]+"/"+sample_id)

#        pprint(download_read_params)
        ru = ReadsUtils(os.environ['SDK_CALLBACK_URL'])
        ret = ru.download_reads(download_read_params)
#        pprint(ret)

        read_file_list=list()
        for file in ret['files']:
            files = ret['files'][file]['files']

            fwd_name=files['fwd'].split('/')[-1]
            fwd_name=fwd_name.replace('.gz','')
            shutil.move(files['fwd'],os.path.join(read_file_path, fwd_name))
            read_file_list.append(os.path.join(read_file_path, fwd_name))

            if(files['rev'] is not None):
                rev_name=files['rev'].split('/')[-1]
                rev_name=rev_name.replace('.gz','')
                shutil.move(files['rev'],os.path.join(read_file_path, rev_name))
                read_file_list.append(os.path.join(read_file_path, rev_name))

        subprocess.check_output(["fastqc"]+read_file_list)
        report = "Command run: "+" ".join(["fastqc"]+read_file_list)
        
        output_html_files = list()
        output_zip_files = list()
        html_string = ""
        html_count = 0
        with open('/kb/data/index_start.txt', 'r') as start_file:
            html_string=start_file.read()

        for file in os.listdir(read_file_path):
            label=".".join(file.split(".")[1:])
            if(file.endswith(".zip")):
                output_zip_files.append({'path' : read_file_path+"/"+file,
                                         'name' : file,
                                         'label' : label,
                                         'description' : 'Zip file generated by fastqc that contains original images seen in the report'})
            if(file.endswith(".html")):
                output_html_files.append({'path' : read_file_path+"/"+file,
                                          'name' : file,
                                          'label' : label,
                                          'description' : 'HTML file generated by fastqc that contains report on quality of reads'})
                html_string+="            <button data-button=\"page\""+str(html_count)+" data-page=\""+file+"\">Page "+str(html_count)+"</button>"
                html_count+=1

        with open('/kb/data/index_end.txt', 'r') as end_file:
            html_string+=end_file.read()

        report_params = { 'objects_created' : [],
#                          'message' : report, 
                          'direct_html' : html_string,
#                          'direct_html_link_index' : 0,
                          'file_links' : output_zip_files, 
                          'html_links' : output_html_files,
                          'workspace_name' : input_params['input_ws'],
                          'report_object_name' : 'kb_fastqc_report_' + uuid_string }
        kbase_report_client = KBaseReport(self.callback_url, token=token)
        output = kbase_report_client.create_extended_report(report_params)
        reported_output = { 'report_name': output['name'], 'report_ref': output['ref'] }

        #Remove temp reads directory
        shutil.rmtree(read_file_path, ignore_errors=True)

        #END runFastQC

        # At some point might do deeper type checking...
        if not isinstance(reported_output, dict):
            raise ValueError('Method runFastQC return value ' +
                             'reported_output is not type dict as required.')
        # return the results
        return [reported_output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK", 'message': "", 'version': self.VERSION, 
                     'git_url': self.GIT_URL, 'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
