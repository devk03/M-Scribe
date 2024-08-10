###############################################################################
#
#  Welcome to Baml! To use this generated code, please run the following:
#
#  $ pip install baml
#
###############################################################################

# This file was generated by BAML: please do not edit it. Instead, edit the
# BAML files and re-generate this code.
#
# ruff: noqa: E501,F401
# flake8: noqa: E501,F401
# pylint: disable=unused-import,line-too-long
# fmt: off

file_map = {
    
    "clients.baml": "client<llm> GPT4o_mini {\n  provider openai\n  options {\n    model \"gpt-4o-mini\"\n    api_key env.OPENAI_API_KEY\n  }\n}",
    "generators.baml": "\n// This helps use auto generate libraries you can use in the language of\n// your choice. You can have multiple generators if you use multiple languages.\n// Just ensure that the output_dir is different for each generator.\ngenerator target {\n    // Valid values: \"python/pydantic\", \"typescript\", \"ruby/sorbet\"\n    output_type \"python/pydantic\"\n    // Where the generated code will be saved (relative to baml_src/)\n    output_dir \"../\"\n    // The version of the BAML package you have installed (e.g. same version as your baml-py or @boundaryml/baml).\n    // The BAML VSCode extension version should also match this version.\n    version \"0.53.1\"\n    // Valid values: \"sync\", \"async\"\n    // This controls what `b.FunctionName()` will be (sync or async).\n    // Regardless of this setting, you can always explicitly call either of the following:\n    // - b.sync.FunctionName()\n    // - b.async_.FunctionName() (note the underscore to avoid a keyword conflict)\n    default_client_mode sync\n}",
    "query.baml": "// Defining a data model.\nclass QueryResponse {\n  response string @description(#\"\n    The response to the question / comment queried by the student.\n  \"#)\n}\n// Creating a function to extract the response from a string.\nfunction ExtractResponse(excerpts: string, query: string) -> QueryResponse {\n  client GPT4o_mini\n  prompt #\"\n    You are a chatbot designed for university of michigan students. DO NOT reveal that you are reading from transcript excerpts. You need to act like you are professional software from the university of michigan.\n\n    I am going to give you excerpts of a lecture transcript that I believe correspond to the following query asked by a student,\n\n    and I want you to do your best to answer the question / comment / whatever.\n\n    The excerpts are ordered by vector similarity to the query, so the ordering might not be chronological.\n    \n    Excerpts:\n    {{ excerpts }}\n\n    Query:\n    {{ query }}\n\n    {{ ctx.output_format }}\n  \"#\n}\n\n// Testing the function with a sample resume.\ntest test_economics_question {\n  functions [ExtractResponse]\n  args {\n    excerpts #\"\n      excerpt 1: conomics. So, uh, the first family ofEconomics you can call them.All right, let's start with adverse selection.What happens when sellers no more than buyers?This is going to be important for each of you in differentdimensions. One often you're going to be abuyerand sometimes you might think I'm worr\\n\\nexcerpt 2: at's by design.That's because I believe all of economics can be boiled down tothese four core principles.And so the only thing you remember in 10 years time, andyou better remember these four,it's the only thing you remember is these four core principles.The marginal principle. Always ask, should I\\n\\nexcerpt 3: re.But we started by building the fundamentals of economics.So we started by saying with a promise from me, there are fourcore principles that you're gonna use to better understandalmost any decision you ever face.We applied those four core principles to buying decisions.We applied them to selling d\\n\\nexcerpt 4: ecisionsthat gave us the demand and the supply curve.We brought those curves together to create something beautiful.We call equilibrium.That framework is a framework that you can use to predict theoutcome of any change in the economy or society.And then you might say I want\\n\\nexcerpt 5: ou've now got the tool kitto analyze the consequences of imports and exports and tariffsand so on on the economy.We turn to externalitieswhich not only are everywhere, but also the central issue inenvironmental debates. You've now got the tools toengage environmental debatesAnd in 2021 externalities\n    \"#\n    query #\"\n      What is economics?\n    \"#\n  }\n}\n",
}

def get_baml_files():
    return file_map