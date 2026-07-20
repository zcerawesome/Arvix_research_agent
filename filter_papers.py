from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import os
import yaml
import json
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    files: list
    is_satisfied: bool
    ROLES: dict
    Filter_Agent: ChatOllama

def user_input_node(state: AgentState) -> AgentState:
    print('\n\nidx | paper title')
    for idx, file in enumerate(state['files']):
        print(idx, file, sep='\t')
    print('\n\n')
    print('Above are the papers that have found to have full strategies that can be backtested')
    response = input('''Input yes if you want to backtest each, a list of comma separated idx for each paper you want to backtest,\nor describe the type of papers you want to backtest: ''')
    if response.lower() == 'yes':
        return {'messages': [""], 'is_satisfied': True}
    try:
        indices = [int(a) for a in response.split(',')]
        filtered_files = [state['files'][index] for index in indices]
        return {"messages": [response], 'files': filtered_files, 'is_satisfied': True}
    except:
        return {'messages': [response], 'is_satisfied': False}
    
def update_list(state: AgentState) -> AgentState:
    criteria = state['messages'][-1]
    role = state['ROLES']['Backtest Relevance Filter']
    filter_text = role['system'].format(research_goal=criteria)
    text_prompt = ''
    folder_path = 'saved_papers/'
    for idx, file in enumerate(state['files']):
        with open(folder_path + file, 'r') as f:
            tag = f'<p id={idx} name="{file}">\n'
            key_detail = yaml.safe_load(f)['Key Findings']
            end = '</p>\n\n'
            text_prompt += tag + key_detail + end
    filter_prompt = [
        SystemMessage(content=filter_text),
        HumanMessage(text_prompt)
    ]
    response = state['Filter_Agent'].invoke(filter_prompt)
    data = json.loads(response.content)
    keys = data['Relevant papers']
    target_files = [state['files'][key] for key in keys]
    return {"messages": [response], "files": target_files, 'is_satisfied': False}

def route_back(state: AgentState) -> str:
    return END if state['is_satisfied'] else "update_list"

