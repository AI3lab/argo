
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import ChatPromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from typing import Union, List, Tuple, Dict, Any, Literal



async def get_chat_model(
        model_name,
        api_key,
        kwargs

) -> ChatOpenAI:
    print(**kwargs)
    return ChatOpenAI(
        api_key=api_key,
        model=model_name,
        **kwargs
    )


async def llm_chat(
        prompt: Union[str, ChatPromptTemplate],
        input: Dict[str, Any],
        model='anthropic/claude-3.5-sonnet',
        temperature=0,
):
    chat_model = await get_chat_model(model=model, temperature=temperature)

    if type(prompt) == str:
        prompt_tpl = PromptTemplate.from_template(prompt)
    else:
        prompt_tpl = prompt

    chain = prompt_tpl | chat_model | StrOutputParser()

    result = await chain.ainvoke(input)

    return result


async def llm_chat_stream(
        prompt: Union[str, ChatPromptTemplate],
        input: Dict[str, Any],
        model='anthropic/claude-3.5-sonnet',
        temperature=0,
):
    chat_model = await get_chat_model(model=model, temperature=temperature)

    if type(prompt) == str:
        prompt_tpl = PromptTemplate.from_template(prompt)
    else:
        prompt_tpl = prompt

    chain = prompt_tpl | chat_model | StrOutputParser()
    async for result in chain.astream(input):
        yield result


async def summarize(
        docs: List[Document],
        model='anthropic/claude-3.5-sonnet',
        temperature=0,
):
    chat_model = await get_chat_model(model=model, temperature=temperature)

    chain = load_summarize_chain(chat_model, chain_type="stuff")
    result = await chain.ainvoke(docs, return_only_outputs=True)

    return result["output_text"]


async def llm_analyze(
        prompt: Union[str, ChatPromptTemplate],
        input: Dict[str, Any],
        output_type: Literal['json', 'text'] = 'json',
        model='anthropic/claude-3.5-sonnet',
        temperature=0,
):
    chat_model = await get_chat_model(model=model, temperature=temperature)

    if type(prompt) == str:
        prompt_tpl = PromptTemplate.from_template(prompt)
    else:
        prompt_tpl = prompt

    if output_type == 'json':
        chain = prompt_tpl | chat_model | JsonOutputParser()
    else:
        chain = prompt_tpl | chat_model | StrOutputParser()

    return await chain.ainvoke(input)
