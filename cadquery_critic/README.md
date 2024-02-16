# CAD Query Loop with Critic


The example utilizes `cadquery` library to create sketch images. The code is written using Open AI API and then improved
using critic built on GPT-4 vision. 


## Execution

To execute the code, install [malevich](https://docs.malevich.ai/) package and run `malevich restore`

After that, ensure you have `OPENAI_API_KEY` environment variable set and then run

`python flow.py --query <YOUR_QUERY> --rounds 5 -d ./outputs/

