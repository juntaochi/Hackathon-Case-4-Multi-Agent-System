# app.py
import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify
import openai

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# In-memory storage for demo purposes
agents = {}      # Key: agent id, Value: dict with position, system_prompt (agent instructions), and inbox
tasks = {}       # Key: task id, Value: dict with description, assigned_to, and completed status
inmails = []     # List of all inmail messages

# Counters for unique ids
task_counter = 1
agent_counter = 1

# Set your OpenAI API key as an environment variable before running
openai.api_key = os.getenv("OPENAI_API_KEY")

def call_openai(instructions, user_message):
    """
    Call the updated OpenAI API using the new instructions parameter.
    The instructions parameter acts as a high-priority developer message.
    """
    response = openai.responses.create(
        model="gpt-4o",
        instructions=instructions,
        input=user_message
    )
    return response.output_text

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Landing page: Ask the user for their business idea.
    """
    if request.method == 'POST':
        business_idea = request.form.get('business_idea')
        # Developer instructions for the AI cofounder
        instructions = (
            "You are an AI cofounder. Your role is to help entrepreneurs start their business. "
            "When a user provides a business idea, suggest the necessary positions (like accountant, lawyer, marketing director) "
            "and, when recruiting, output your command using this format exactly:\n\n"
            "[recruit]{ \"position\": \"<role>\", \"system_prompt\": \"<detailed instructions for the agent>\" }\n\n"
            "If you need to send an internal message, use the following format:\n\n"
            "[inmail]{ \"sender\": \"<sender_name>\", \"recipient\": \"<recipient_name>\", \"subject\": \"<subject>\", \"body\": \"<body>\" }\n\n"
            "When assigning tasks, use:\n\n"
            "[task]{ \"id\": \"<task_id>\", \"description\": \"<task_description>\" }\n\n"
            "Always use these commands exactly as specified."
        )
        response = call_openai(instructions, f"Business Idea: {business_idea}")
        return render_template("choose_positions.html", business_idea=business_idea, cofounder_response=response)
    return render_template("index.html")

@app.route('/recruit', methods=['POST'])
def recruit():
    """
    Recruit agents based on the user’s desired positions.
    """
    desired_positions = request.form.get('positions')  # e.g., "lawyer,marketing director"
    business_idea = request.form.get('business_idea')
    
    instructions = (
        "You are an AI cofounder responsible for recruiting AI agents for a startup. "
        "When recruiting an agent, output your command using the following format exactly:\n\n"
        "[recruit]{ \"position\": \"<role>\", \"system_prompt\": \"<detailed instructions for the agent>\" }"
    )
    
    for pos in [p.strip() for p in desired_positions.split(',') if p.strip()]:
        user_message = f"Recruit an agent for the position: {pos} for a business idea: {business_idea}"
        response = call_openai(instructions, user_message)
        if "[recruit]" in response:
            try:
                json_str = response.split("[recruit]")[1].strip()
                recruit_data = json.loads(json_str)
                global agent_counter
                agent_id = f"agent_{agent_counter}"
                agent_counter += 1
                agents[agent_id] = {
                    "id": agent_id,
                    "position": recruit_data.get("position"),
                    "system_prompt": recruit_data.get("system_prompt"),
                    "inmails": []
                }
            except Exception as e:
                print("Error parsing recruit command:", e)
    return redirect(url_for('dashboard'))

@app.route('/chat_cofounder', methods=['POST'])
def chat_cofounder():
    """
    Endpoint to handle chat messages with the AI cofounder.
    This endpoint receives a chat message and returns the cofounder's response.
    """
    user_message = request.form.get('message')
    instructions = (
        "You are an AI cofounder. Your role is to assist entrepreneurs continuously with guidance on business strategy, recruitment, and task management. "
        "Respond in clear and concise language and when needed, use command formats like [recruit], [inmail], and [task] exactly as specified."
    )
    response_text = call_openai(instructions, user_message)
    return jsonify({"response": response_text})

@app.route('/dashboard')
def dashboard():
    """
    Dashboard view: shows all agents, their inmail inboxes, and current tasks.
    """
    return render_template("dashboard.html", agents=agents, tasks=tasks, inmails=inmails)

@app.route('/send_inmail', methods=['POST'])
def send_inmail():
    """
    Endpoint to handle sending an inmail message.
    """
    sender = request.form.get('sender')
    recipient = request.form.get('recipient')
    subject = request.form.get('subject')
    body = request.form.get('body')
    inmail = {"sender": sender, "recipient": recipient, "subject": subject, "body": body}
    inmails.append(inmail)
    for agent in agents.values():
        if agent["position"].lower() == recipient.lower():
            agent["inmails"].append(inmail)
    return jsonify({"status": "success", "inmail": inmail})

@app.route('/create_task', methods=['POST'])
def create_task():
    """
    Create a new task assigned to a specific agent.
    """
    description = request.form.get('description')
    assigned_to = request.form.get('assigned_to')
    global task_counter
    task_id = f"task_{task_counter}"
    task_counter += 1
    tasks[task_id] = {
        "id": task_id,
        "description": description,
        "assigned_to": assigned_to,
        "completed": False
    }
    return jsonify({"status": "success", "task": tasks[task_id]})

@app.route('/complete_task', methods=['POST'])
def complete_task():
    """
    Mark a task as complete.
    """
    task_id = request.form.get('task_id')
    if task_id in tasks:
        tasks[task_id]['completed'] = True
        return jsonify({"status": "success", "task_id": task_id})
    return jsonify({"status": "error", "message": "Task not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
