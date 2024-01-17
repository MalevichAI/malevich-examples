# Docs Generation

We are in Malevich write a lot of apps for new users to quickly start developing their ideas. The pace of development of such apps is rapid, and the documentation is often left behind. In order to avoid this, we have developed a tool that allows us to generate documentation from the code. As processor functions are often well-documented, we can generate a good documentation for no-code users.

## How it is done

To automatically generate documentation, we use Open AI GPT models and our Malevich backend to launch it! By utilizing a simple flow and Malevich Runners we simultaneosly generate documentation for all the detected functions in the code.

## How to use it

All the code is located in `flow.py` file. To run it, you need to have Malevich installed and configured. Then you can run it with `malevich run flow.py` command. It will generate a `docs` folder with all the documentation in it. You can then use it in your project.

### How to configure it

Before running the flow, you should [restore Malevich environment](https://docs.malevich.ai/docs/malevich-meta/environment#restoring-environment). It could be done using the following command:

```bash
malevich restore
```

Also, you have to ensure that the environment variable `OPENAI_API_KEY` is set.

### How we run in

We are using the following command to run the flow:

```bash

OPENAI_API_KEY=... python flow.py --path <PATH_TO_LIB>

```