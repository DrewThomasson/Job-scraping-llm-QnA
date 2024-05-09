#!/bin/bash

print Make sure you have Ollama installed before running this or it won't work

print installing wget with brew...

brew install wget

print Complete!

# Download first file
wget https://huggingface.co/failspy/kappa-3-phi-3-4k-instruct-abliterated-GGUF/resolve/main/ggml-model-f16.gguf?download=true -O ggml-model-f16.gguf

touch Modelfile

# Create Modelfile and populate it
cat << EOF > Modelfile
FROM $(pwd)/ggml-model-f16.gguf
TEMPLATE "{{ if .System }}<|system|>
{{ .System }}<|end|>
{{ end }}{{ if .Prompt }}<|user|>
{{ .Prompt }}<|end|>
{{ end }}<|assistant|>
{{ .Response }}<|end|>
"
PARAMETER num_keep 4
PARAMETER stop <|user|>
PARAMETER stop <|assistant|>
PARAMETER stop <|system|>
PARAMETER stop <|end|>
PARAMETER stop <|endoftext|>
EOF

# Run command to create uncensored_phi3
ollama create uncensored_phi3 -f Modelfile

# Download second file
wget https://huggingface.co/failspy/Llama-3-8B-Instruct-abliterated-GGUF/resolve/main/Llama-3-8B-Instruct-abliterated-q4_k.gguf?download=true -O Llama-3-8B-Instruct-abliterated-q4_k.gguf

# Modify Modelfile with content from the second file
cat << EOF > Modelfile
FROM $(pwd)/Llama-3-8B-Instruct-abliterated-q4_k.gguf
TEMPLATE "{{ if .System }}<|start_header_id|>system<|end_header_id|>

{{ .System }}<|eot_id|>{{ end }}{{ if .Prompt }}<|start_header_id|>user<|end_header_id|>

{{ .Prompt }}<|eot_id|>{{ end }}<|start_header_id|>assistant<|end_header_id|>

{{ .Response }}<|eot_id|>"
PARAMETER num_keep 24
PARAMETER stop <|start_header_id|>
PARAMETER stop <|end_header_id|>
PARAMETER stop <|eot_id|>
EOF

# Run command to create uncensored_llama3
ollama create uncensored_llama3 -f Modelfile

# List all ollama models
ollama list

# Remove downloaded files and Modelfile
print removing Modelfile and Downloaded files...
rm ggml-model-f16.gguf Llama-3-8B-Instruct-abliterated-q4_k.gguf Modelfile
Print Complete!
