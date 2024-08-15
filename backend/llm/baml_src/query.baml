// Defining a data model.
class QueryResponse {
  response string @description(#"
    The response to the question / comment queried by the student.
  "#)
}
// Creating a function to extract the response from a string.
function ExtractResponse(excerpts: string, query: string) -> QueryResponse {
  client GPT4o_mini
  prompt #"
    You are a chatbot designed for university of michigan students. DO NOT reveal that you are reading from transcript excerpts. You need to act like you are professional software from the university of michigan.

    I am going to give you excerpts of a lecture transcript that I believe correspond to the following query asked by a student,

    and I want you to do your best to answer the question / comment / whatever.

    The excerpts are ordered by vector similarity to the query, so the ordering might not be chronological. When answering questions, do not focus on the fact that the professor is talking about explaining a topic, focus on the topic itself.
    
    If you can try to be specific about examples used in respect to the lecture.
    
    Excerpts:
    {{ excerpts }}

    Query:
    {{ query }}

    {{ ctx.output_format }}
  "#
}

// Testing the function with a sample resume.
test test_economics_question {
  functions [ExtractResponse]
  args {
    excerpts #"
      excerpt 1: conomics. So, uh, the first family ofEconomics you can call them.All right, let's start with adverse selection.What happens when sellers no more than buyers?This is going to be important for each of you in differentdimensions. One often you're going to be abuyerand sometimes you might think I'm worr\n\nexcerpt 2: at's by design.That's because I believe all of economics can be boiled down tothese four core principles.And so the only thing you remember in 10 years time, andyou better remember these four,it's the only thing you remember is these four core principles.The marginal principle. Always ask, should I\n\nexcerpt 3: re.But we started by building the fundamentals of economics.So we started by saying with a promise from me, there are fourcore principles that you're gonna use to better understandalmost any decision you ever face.We applied those four core principles to buying decisions.We applied them to selling d\n\nexcerpt 4: ecisionsthat gave us the demand and the supply curve.We brought those curves together to create something beautiful.We call equilibrium.That framework is a framework that you can use to predict theoutcome of any change in the economy or society.And then you might say I want\n\nexcerpt 5: ou've now got the tool kitto analyze the consequences of imports and exports and tariffsand so on on the economy.We turn to externalitieswhich not only are everywhere, but also the central issue inenvironmental debates. You've now got the tools toengage environmental debatesAnd in 2021 externalities
    "#
    query #"
      What is economics?
    "#
  }
}
