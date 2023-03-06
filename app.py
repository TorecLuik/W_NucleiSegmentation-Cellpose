import gradio as gr
import subprocess
import json


def greet(run_kwargs):
    cmd = "/app/wrapper.py"
    msg = f"Greetings: {cmd} (from config: {config['command-line']}) w/ args \n{run_kwargs}"
    print(msg)
    # return msg
    # return msg
    try:
        status = subprocess.run(
                [
                    'python3.7',
                    cmd
                ],
                capture_output=True
            )
    except subprocess.CalledProcessError as e:
        results = f"Error {e.__dict__}"
        print(results)
    finally:
        if status.returncode != 0:
            msg = msg + f"\nRunning failed: {status.__dict__}"  
        else:
            msg = msg + f"\nRun succeeded: {status.__dict__}"
        print(msg)
        return msg


with open('descriptor.json') as f:
    config = json.load(f)
    

def main():
    with gr.Blocks() as demo:
        inputs = []
        for input in config["inputs"]:
            if input["type"] == "String":
                if "default-value" in input:
                    inputs.append(
                        gr.Textbox(label=input["name"],
                                   value=input["default-value"]))
                else:
                    inputs.append(
                        gr.Textbox(label=input["name"]))
            elif input["type"] == "Number":
                if "default-value" in input:
                    inputs.append(
                        gr.Number(label=input["name"],
                                  value=input["default-value"]))
                else:
                    inputs.append(
                        gr.Number(label=input["name"]))
        
        run_btn = gr.Button("Run")
        out = gr.Textbox(label="Output")
        
        run_btn.click(greet, inputs=set(inputs), outputs=out)
    
    demo.launch(server_name="0.0.0.0", debug=True)


if __name__ == '__main__':
    main()