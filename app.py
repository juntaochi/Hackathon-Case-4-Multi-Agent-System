from flask import Flask, render_template, jsonify
import threading
from queue import Queue
from agents import AssemblyAgent, LogisticsAgent, QualityControlAgent

app = Flask(__name__)
message_queue = Queue()

# Create agent instances
assembly_agent = AssemblyAgent("AssemblyAgent", message_queue)
logistics_agent = LogisticsAgent("LogisticsAgent", message_queue)
quality_agent = QualityControlAgent("QualityControlAgent", message_queue)

def run_agent(agent):
    agent.run()

# Start each agent in its own thread
threading.Thread(target=run_agent, args=(assembly_agent,), daemon=True).start()
threading.Thread(target=run_agent, args=(logistics_agent,), daemon=True).start()
threading.Thread(target=run_agent, args=(quality_agent,), daemon=True).start()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/api/logs')
def api_logs():
    logs = []
    # Retrieve all logs available in the message queue
    while not message_queue.empty():
        logs.append(message_queue.get())
    return jsonify(logs)

@app.route('/api/status')
def api_status():
    status = {
        "AssemblyAgent": assembly_agent.status,
        "LogisticsAgent": logistics_agent.status,
        "QualityControlAgent": quality_agent.status
    }
    return jsonify(status)

if __name__ == '__main__':
    app.run(debug=True)
