# Malevich Rival

Welcome to a Rival - a demand analysis system built with Malevich! 

# Setup

## Package

Before the magic happens, you should install Python 3.11 and malevich package. Run the following command to do it:

```bash
pip install malevich
```

## Secrets

After the package installed, you have to restore secrets - special variables stored only in your local environment. For this you should run the following command:

```bash
malevich manifest secrets restore
```

Ensure that everything is fine using

```bash
malevich manifest secrets scan
```

## Packages

After secrets are installed you may install Malevich apps to be able to update flow using metascript. To simply restore all the packages at once use:

```bash
malevich restore
```

# Update Flow

The flow is the function decorated with `@flow()` once you run and interpret the function, you obtain a new version of the pipeline that immediately appears in UI. Once you change anything decorated function, you may run the following command to update the flow in Space:

```bash
python flows/rival.py
```

It is your choice how to store GPT-4 key within the config. The version handed to you make use of environment variable `OPENAI_API_KEY`. You may wish to set it for the key to appear in UI config.