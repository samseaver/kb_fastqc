/*
A KBase module: kb_fastqc
*/

module kb_fastqc {

   typedef structure {
       string input_ws;
       string input_file;
       string input_file_ref;
   } FastQCParams;

    typedef structure {
        string report_name;
        string report_ref;
    } FastQCOutput;

   funcdef runFastQC(FastQCParams input_params)
       returns (FastQCOutput reported_output)
       authentication required;
};
