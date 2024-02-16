import os
import uuid
from malevich.square import  APP_DIR, DF, Context, processor, scheme
import pandas as pd


empty_file = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   width="800.0"
   height="240.0"
>
    <g fill="none">
        <!-- No shapes are defined here -->
    </g>
    <g transform="translate(20,210.0)" stroke="rgb(0,0,255)">
        <text x="80" y="-30" style="stroke:#000000">X </text>
        <text x="25" y="-85" style="stroke:#000000">Y </text>
        <text x="65" y="-5" style="stroke:#000000">Z </text>
        <!-- Coordinate system labels are retained -->
    </g>
</svg>
"""

def code_execution_sample(code_to_execute, write_to: str):
    import cadquery as cq
    import cairosvg

    error_message = ''
    try:
        local_scope = {}
        exec("import cadquery as cq \n\n"+code_to_execute, local_scope)
        result = local_scope['Result']
        cq.exporters.export(result, 'generation.svg')
        cq.exporters.export(result, 'generation.stl')
        with open('generation.svg', 'rb') as svg_file:
            svg_content = svg_file.read()

    except Exception as e:
        error_message = str(e)
        print(error_message)
        svg_content = empty_file

    # Convert SVG to PNG
    cairosvg.svg2png(bytestring=svg_content, write_to=write_to)

    return error_message


def extract_python_code(text):
    # Define markers for the start and end of the Python code block
    start_marker = "@@@"
    end_marker = "@@@"

    # Find the start position of the Python code block
    start_pos = text.find(start_marker)

    # Find the end position of the Python code block, which is after the second occurrence of the start marker
    end_pos = text.find(end_marker, start_pos + len(start_marker))

    # Find the actual end marker, which is after the second occurrence of the end marker
    actual_end_pos = text.find(end_marker, end_pos + len(end_marker))

    # Extract and return the Python code block
    try:
        # Include the length of end_marker to get the text until the end of the marker
        return text[start_pos + len(start_marker):actual_end_pos-len(end_marker)].strip()
    except:
        return text

@scheme()
class CodeSample:
    code: str


@processor()
def execute_python_with_cq(code_samples: DF[CodeSample], context: Context):
    outputs = []
    
    for code_text in code_samples.code.to_list():
        code_part = extract_python_code(code_text)
        image_name = uuid.uuid4().hex + '.png'
        msg_ = code_execution_sample(
            code_part, os.path.join(APP_DIR, image_name)
        )
        outputs.append(
            {
                "code": code_part,
                "error_code": msg_,
                "image": image_name,
            }
        )
        
    out_df = pd.DataFrame(outputs)
    context.share_many(out_df.image.to_list())
    
    return out_df
    
        
