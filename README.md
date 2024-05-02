# Gepetto fork

Gepetto fork is a Python script which uses Groq's llama3-70b-8096 model to provide meaning to functions decompiled
by IDA Pro. If Groq fails (rate limit reached or context too long), then together.ai is queried if an
API key for it is configured, using mixtral-8x22b with 64kb context. They give 25$ when
opening an account, so a lot of free LLM interference.

At the moment, it can ask to explain what a function does, and to automatically rename its 
variables. Here is a simple example of what results it can provide in mere seconds:

![](https://github.com/JusticeRage/Gepetto/blob/main/readme/comparison.png?raw=true)

## Setup

Simply drop this script (as well as the `gepetto/` folder) into your IDA plugins folder (`$IDAUSR/plugins`). 
By default, on Windows, this should be `%AppData%\Hex-Rays\IDA Pro\plugins` (you may need to create the folder).

You will need to add the required packages to IDA's Python installation for the script to work.
Find which interpreter IDA is using by checking the following registry key: 
`Computer\HKEY_CURRENT_USER\Software\Hex-Rays\IDA` (default on Windows: `%LOCALAPPDATA%\Programs\Python\Python39`).
Finally, with the corresponding interpreter, simply run: 

```
[/path/to/python] -m pip install -r requirements.txt
```

⚠️ You will also need to edit the configuration file (found as `gepetto/config.ini`) and add your own API key, which 
can be found on [this page](https://beta.openai.com/account/api-keys).
Please note that Groq API queries are currently free but rate limited!

## Usage

Once the plugin is installed properly, you should be able to invoke it from the context menu of IDA's pseudocode window,
as shown in the screenshot below:

![](https://github.com/JusticeRage/Gepetto/blob/main/readme/usage.png?raw=true)

Switch between models supported by Gepetto from the Edit > Gepetto menu:

![](https://github.com/JusticeRage/Gepetto/blob/main/readme/select_model.png?raw=true)

You can also use the following hotkeys:

- Ask the model to explain the function: `Ctrl` + `Alt` + `H`
- Request better names for the function's variables: `Ctrl` + `Alt` + `R`

Initial testing shows that asking for better names works better if you ask for an explanation of the function first – I
assume because the model then uses its own comment to make more accurate suggestions.
There is an element of randomness to the AI's replies. If for some reason the initial response you get doesn't suit you,
you can always run the command again.

## Limitations

- only 6000 tokens can be sent to the Groq API at once, easily reached with the "rename variables" feature.
- Groq API has rate limiting for free accounts, you will hit it fast :)
- Together.AI API is only free for 25$ (about 25 million in/out tokens)

## Translations

You can change Gepetto's language by editing the locale in the configuration. For instance, to use the plugin
in French, you would simply add:

```ini
[Gepetto]
LANGUAGE = "fr_FR"
```
The chosen locale must match the folder names in `gepetto/locales`. If the desired language isn't available,
you can contribute to the project by adding it yourself! The translation portal to get involved is on 
[Transifex](https://app.transifex.com/gepetto/).

## Acknowledgements

- [Groq](https://groq.com), for their service
- [Hex Rays](https://hex-rays.com/), the makers of IDA for their lightning fast support
- [Kaspersky](https://kaspersky.com), for initially funding this project
- [HarfangLab](https://harfanglab.io/), the current backer making this work possible
