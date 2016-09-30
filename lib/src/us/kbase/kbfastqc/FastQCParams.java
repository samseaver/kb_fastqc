
package us.kbase.kbfastqc;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: FastQCParams</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "input_ws",
    "input_file"
})
public class FastQCParams {

    @JsonProperty("input_ws")
    private String inputWs;
    @JsonProperty("input_file")
    private String inputFile;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("input_ws")
    public String getInputWs() {
        return inputWs;
    }

    @JsonProperty("input_ws")
    public void setInputWs(String inputWs) {
        this.inputWs = inputWs;
    }

    public FastQCParams withInputWs(String inputWs) {
        this.inputWs = inputWs;
        return this;
    }

    @JsonProperty("input_file")
    public String getInputFile() {
        return inputFile;
    }

    @JsonProperty("input_file")
    public void setInputFile(String inputFile) {
        this.inputFile = inputFile;
    }

    public FastQCParams withInputFile(String inputFile) {
        this.inputFile = inputFile;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((((("FastQCParams"+" [inputWs=")+ inputWs)+", inputFile=")+ inputFile)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
