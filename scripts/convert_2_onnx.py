import os
import sys
import torch
import argparse

# Add the root project directory to sys.path so 'backbones' can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backbones import get_model

def convert_edgeface_to_onnx(model_name, output_folder = None, use_torch_hub=False):
    if output_folder:
        output_path = f"{output_folder}/{model_name}.onnx"
    else:
        output_path = f"{model_name}.onnx"

    if use_torch_hub:
        # Load model and pretrained weights from Pytorch Hub 
        model = torch.hub.load('otroshi/edgeface', model_name)
        model = torch.hub.load('otroshi/edgeface', model_name, source='github', pretrained=True)
    
    else:
        # Load model structure locally and attempt to load weigts from the checkpoints directory 
        model = get_model(model_name)
        checkpoint_path = os.path.join(os.path.dirname(__file__), "..", 'checkpoints', f"{model_name}.pt")
        if os.path.exists(checkpoint_path):
            print(f"Loading weights from {checkpoint_path}.")
            model.load_state_dict(torch.load(checkpoint_path))
        else:
            print(f"Waring: {checkpoint_path} not found!")
        
    model.eval()

    # Edgeface expects 112x112 RGB cropped images
    dummy_input = torch.randn(1, 3, 112, 112)

    print(f"Exporting to ONNX formate at {output_path}")
    torch.onnx.export(model, 
                      dummy_input, 
                      output_path,
                      export_params=True, 
                      opset_version=11,
                      do_constant_folding=True, 
                      input_names=['input'], 
                      output_names=['output'], 
                      dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
                      verbose=True)
    
    print(f"ONNX conversion completed and saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, help="Name of the model to convert", required=True)
    parser.add_argument("--output_foler", type=str, help="Directory to save onnx model.", default=None)
    args = parser.parse_args()
    convert_edgeface_to_onnx(args.model_name, args.output_foler)

