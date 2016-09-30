/*
A KBase module: kb_fastqc
*/

module kb_fastqc {

   typedef string FastQCOutput;

   typedef structure {
       string input_ws;
       string input_file;
   } FastQCParams;

   funcdef runFastQC(FastQCParams input_params)
       returns (FastQCOutput encoded_html_string)
       authentication required;
};
