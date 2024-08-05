# from langchain import hub
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
# from langchain_core.tools import StructuredTool
from langchain_core.tools import tool
# from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.messages import HumanMessage
import os
key = os.getenv('LANGCHAIN_API_KEY')
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = key
os.environ["LANGCHAIN_PROJECT"] = "agent"

llm = ChatOpenAI(model="gpt-4o")
input_msg = f"""
                generate a map titled 武汉市行政区划图 using data from the directory 
                '../data /武汉市.shp, ../data/公路.shp, ../data/铁路.shp'.
                For the 公路.shp files, change the line color to red. 
                For the 铁路.shp files, change the line color to yellow. 
                For the 武汉市.shp file, adjust the color of the polygon features according to the 地名 attribute.
            """


@tool(parse_docstring=True)
def map_add_layer(filepath: str):
    """
        Add one vector layer to the map.

        Args:
            filepath: directory of vector layer data.
    """
    print(filepath)
    return


@tool
def map_initial():
    """
    Initialize the basic settings of the map.
    Get basic information about vector files and set the display range,
    background color and coordinate system of the map.
    """
    print("initialize compeleted")
    return


@tool(parse_docstring=True)
def modify_line_color(color: str):
    """
        Modify the style of line features in the vector layer.

        Args:
            color: the color of line
    """
    print(color)
    return


map_add_layer.args_schema.schema()

tools = [map_add_layer, map_initial, modify_line_color]

template = f"""
<role>: You are a map expert and you are proficient in generating maps using vector or raster data .
<task>: Yourtask is to answer the question or solve the problem step by step using the {tools} provided.
<instrcution>
You can only respond with a single complete "Thought , Action , ActionInput , Observation" format OR a single "Final Answer" format .
Complete format:
Thought: (reflect on your progress and decide what to do next (based on observation if exist), do not skip)
Action: (the action name, should be one of[{tools}]. decide the action based on previous Thought and Observation)
ActionInput: (theinputstringtotheaction , decidetheinputbasedonpreviousThoughtandObservation )
Observation: (the result of the action)
(this process can repeat and you can only process one subtask at a time)
OR
Thought: (Review original question and check my total process)
Final Answer: (Outputs the final answer to the original input question based on observations and lists all data paths used and generated)

Answer the question below using the following tools: {tools}
Your final answer should contain all information necessary to answer the question and subquestions.

Do not skip these steps.
Begin! 
Question: {input}
"""
prompt = ChatPromptTemplate.from_template(template)
agent_executor = create_react_agent(llm, tools)
chain = prompt | agent_executor
response = chain.invoke({"input": input, "tools": tools})
print(response)
