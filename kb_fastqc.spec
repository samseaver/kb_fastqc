/*
A KBase module: kb_fastqc
*/

module kb_fastqc {

   typedef structure {
       string input_ws;
       string input_file;
   } FastQCParams;

   funcdef runFastQC(FastQCParams input_params)
       returns (string encoded_html_string)
       authentication required;
};
