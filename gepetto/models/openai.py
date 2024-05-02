import functools
import os
import re
import threading

import httpx as _httpx
import ida_kernwin
import groq as openai 
from together import Together

from gepetto.models.base import LanguageModel
import gepetto.config

_ = gepetto.config.translate.gettext


class GPT(LanguageModel):
    def __init__(self, model):
        self.model = model
        # Get API key
        if not gepetto.config.parsed_ini.get('OpenAI', 'API_KEY'):
            api_key = os.getenv("GROQ_API_KEY")
        else:
            api_key = gepetto.config.parsed_ini.get('OpenAI', 'API_KEY')
        if not api_key:
            print(_("Please edit the configuration file to insert your Groq API key!"))
            raise ValueError("No valid Groq API key found")

        if not gepetto.config.parsed_ini.get('OpenAI', 'TOGETHER_API_KEY'):
            together_api_key = os.getenv("TOGETHER_API_KEY")
        else:
            together_api_key = gepetto.config.parsed_ini.get('OpenAI', 'TOGETHER_API_KEY')
        if not api_key:
            print(_("You do not have a Together.ai API key set!"))

        # Get OPENAPI proxy
        if not gepetto.config.parsed_ini.get('OpenAI', 'OPENAI_PROXY'):
            proxy = None
        else:
            proxy = gepetto.config.parsed_ini.get('OpenAI', 'OPENAI_PROXY')

        # Get BASE_URL
        if not gepetto.config.parsed_ini.get('OpenAI', 'BASE_URL'):
            base_url = None
        else:
            base_url = gepetto.config.parsed_ini.get('OpenAI', 'BASE_URL')

        self.client = openai.Groq(
            api_key=api_key,
            base_url=base_url,
            http_client=_httpx.Client(
                proxies=proxy,
            ) if proxy else None
        )

    def __str__(self):
        return self.model

    def query_model(self, query, cb, additional_model_options=None):
        """
        Function which sends a query to gpt-3.5-turbo or gpt-4 and calls a callback when the response is available.
        Blocks until the response is received
        :param query: The request to send to gpt-3.5-turbo or gpt-4
        :param cb: The function to which the response will be passed to.
        :param additional_model_options: Additional parameters used when creating the model object. Typically, for
        OpenAI, response_format={"type": "json_object"}.
        """
        if additional_model_options is None:
            additional_model_options = {}
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": query}
                ],
                max_tokens=8192, **additional_model_options
            )
            ida_kernwin.execute_sync(functools.partial(cb, response=response.choices[0].message.content),
                                     ida_kernwin.MFF_WRITE)
        except openai.BadRequestError as e:
            # Context length exceeded. Determine the max number of tokens we can ask for and retry.
            m = re.search(r'maximum context length is \d+ tokens, however you requested \d+ tokens', str(e))
            if m:
                print(_("Unfortunately, this function is too big to be analyzed with the model's current API limits."))
            else:
                print(_("General exception encountered while running the query: {error}").format(error=str(e)))
        except Exception as e:
            print(_("Error while running the query: {error}").format(error=str(e)))
            client = Together(api_key=together_api_key)
            try:
                response = client.chat.completions.create(
                    model="mistralai/Mixtral-8x22B-Instruct-v0.1",
                    messages=query,
                )
                ida_kernwin.execute_sync(functools.partial(cb, response=response.choices[0].message.content),
                                     ida_kernwin.MFF_WRITE)
            except Exception as e:
                print(_("Error while running the query: {error}").format(error=str(e)))

    # -----------------------------------------------------------------------------

    def query_model_async(self, query, cb, additional_model_options=None):
        """
        Function which sends a query to {model} and calls a callback when the response is available.
        :param query: The request to send to {model}
        :param cb: Tu function to which the response will be passed to.
        :param additional_model_options: Additional parameters used when creating the model object. Typically, for
        OpenAI, response_format={"type": "json_object"}.
        """
        if additional_model_options is None:
            additional_model_options = {}
        print(_("Request to {model} sent...").format(model=str(gepetto.config.model)))
        t = threading.Thread(target=self.query_model, args=[query, cb, additional_model_options])
        t.start()

