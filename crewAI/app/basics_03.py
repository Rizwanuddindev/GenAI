import os, requests
from duckduckgo_search import DDGS
from crewai import Agent, Task, Crew
from decouple import config
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from bs4 import BeautifulSoup

import gradio as gr

# change the python version to: >=3.10,<3.13
# poetry new crewAI_tutorial --name app
# poetry config virtualenvs.in-project true
# poetry add crewai python-decouple gradio beautifulsoup4
# cd crewAI_tutorial model = gpt-3.5-turbo
# poetry run python3 basics_03.py

os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4-turbo-preview") # gpt-3.5-turbo

class WebBrowserToo():

    @tool("internet_search", return_direct=False)
    def internet_search(query: str) -> str:
        """Useful for quering content on the internet using DuckDuckGo"""
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
            return results if results else "No results found"

    @tool("process_search_results", return_direct=False)
    def process_search_results(url: str) -> str:
        """Process Content From Webpage"""
        response = requests.get(url=url)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.get_text()


tools = [
    WebBrowserToo().internet_search,
    WebBrowserToo().process_search_results
]


# Define your agents with roles and goals
news_correspondent = Agent(
    role='News Correspondent',
    goal='Advanced News Publisher Correspondent',
    backstory="""Your primary role is to function as an intelligent news research assistant, adept at scouring 
    the internet for the latest and most relevant trending stories across various sectors like politics, technology, 
    health, culture, and global events. You possess the capability to access a wide range of online news sources, 
    blogs, and social media platforms to gather real-time information.""",
    verbose=False,
    # Agent not allowed to delegate tasks to any other agent
    allow_delegation=False,
    tools=tools,
    llm=llm
)


news_editor = Agent(
    role='News Editor',
    goal="News Editor for 'AI News'",
    backstory="""To craft compelling and informative news reports using insights provided by Aria, the AI News Correspondent, 
    focusing on delivering high-quality journalism for 'AI News', a leading digital newspaper publisher.""",
    verbose=False,
    allow_delegation=True,
    tools=tools,
    llm=llm
)


ads_writter = Agent(
    role='Ad Writer',
    goal="Ad Writer for 'AI News'",
    backstory="""To craft compelling and relevant advertisements for 'AI News' publication, complementing the content written by the news editor.
    
    Contextual Ad Placement: Analyze the final report content from the news editor in-depth to identify key themes, topics, and reader interests. Place ads that are contextually relevant to these findings, thereby increasing potential customer engagement.

    Advanced Image Sourcing and Curation: Employ sophisticated web search algorithms to source high-quality, relevant images for each ad. Ensure these images complement the ad content and are aligned with the publication's aesthetic standards.

    Ad-Content Synchronization: Seamlessly integrate advertisements with the report, ensuring they enhance rather than disrupt the reader's experience. Ads should feel like a natural extension of the report, offering value to the reader.

    Reference and Attribution Management: For each image sourced, automatically generate and include appropriate references and attributions, ensuring compliance with copyright laws and ethical standards.
""",
    verbose=False,
    allow_delegation=True,
    tools=tools,
    llm=llm
)

supervisor = Agent(
    role='Supervisor',
    goal="Supervisor for 'AI News'",
    backstory="""You are an excellent supervisor for 'AI News'. Your primary role is to supervise each publication from the 'news editor' 
    and the ads written by the 'ads writter' and approve the work for publication. Examine the work and regulate violent language, abusive content and racist content.
    
    Capabilities:

    Editorial Review: Analyze the final drafts from the news editor and the ads writer for style consistency, thematic alignment, and overall narrative flow.

    Visual and Textual Harmony: Assess the integration of text and visuals in both news articles and advertisements, ensuring that images complement the writing and maintain a consistent aesthetic throughout the publication.

    Quality Assurance: Conduct detailed checks for grammatical accuracy, factual correctness, and adherence to journalistic standards in the news content, as well as creativity and effectiveness in the advertisements.

    Audience Engagement Analysis: Evaluate the potential impact of the combined content on the target audience, using predictive algorithms to suggest improvements for maximizing reader engagement and satisfaction.

    Feedback Loop: Provide constructive feedback to both the news editor and ads writer, facilitating a collaborative environment for continuous improvement in content creation and presentation.""",
    verbose=False,
    allow_delegation=True,
    tools=tools,
    llm=llm
)


# task1 = Task(
#     description="""Conduct a comprehensive research on the current trends in Space technology, specifically focusing 
#     on SpaceX and the Mars mission. Your final response should provide a detailed explanation on the approximate cost 
#     and timeline of the mission summarized into 3 paragraphs. Also include any advancements made in the space industry. 
#     Make sure you include links to the sources (websites) from which you obtained the facts from.""",
#     agent=news_correspondent
# )


task2 = Task(
    description="""Using the research findings of the news correspondent, write an publication for the news letter 'AI News'. The publication should contain references links to sources stated by the correspontent. 
    Your final answer MUST be the full blog post of at least 3 paragraphs.""",
    agent=news_editor
)

task3 = Task(
    description="""Using the final report from the news editor, include Ads in the final publication that will help advertisers advertise their products to potential customers. I want you to include images that you can get from web search. Make sure to add references to each of this images.""",
    agent=ads_writter
)


task4 = Task(
    description="""To meticulously review and harmonize the final output from both the news editor and ads writer, ensuring cohesion and excellence in the final publication for 'AI News'.""",
    agent=supervisor
)


agents = [news_correspondent, news_editor, ads_writter, supervisor]


def run_graph(input_message):
    task1 = Task(
        description=input_message,
        agent=news_correspondent
    )

    crew = Crew(
        agents=agents,
        tasks=[task1, task2],
        verbose=2
    )
    result = crew.kickoff()
    return result


inputs = gr.components.Textbox(lines=2, placeholder="Enter your query here...")
outputs = gr.components.Markdown()

demo = gr.Interface(
    fn=run_graph,
    inputs=inputs,
    outputs=outputs
)

demo.launch()