import threading
import time
import random
from queue import Queue

class Agent:
    def __init__(self, name, message_queue):
        self.name = name
        self.message_queue = message_queue
        self.status = "Idle"

    def log(self, message):
        log_message = f"[{self.name}] {message}"
        print(log_message)
        self.message_queue.put((self.name, message))

class AssemblyAgent(Agent):
    def run(self):
        while True:
            self.status = "Assembling"
            self.log("Starting assembly of product")
            time.sleep(random.uniform(1, 3))  # simulate assembly time
            self.status = "Waiting"
            self.log("Assembly complete, sending product to Logistics")
            # Signal to Logistics Agent
            self.message_queue.put((self.name, "Product assembled"))
            time.sleep(1)

class LogisticsAgent(Agent):
    def run(self):
        while True:
            self.status = "Transporting"
            self.log("Transporting product to Quality Control")
            time.sleep(random.uniform(1, 2))  # simulate transport time
            self.status = "Waiting"
            self.log("Product delivered to Quality Control")
            # Signal to Quality Control Agent
            self.message_queue.put((self.name, "Product delivered"))
            time.sleep(1)

class QualityControlAgent(Agent):
    def run(self):
        while True:
            self.status = "Inspecting"
            self.log("Inspecting product")
            time.sleep(random.uniform(1, 2))  # simulate inspection time
            self.status = "Waiting"
            self.log("Inspection complete, product approved")
            # Signal completion of the product cycle
            self.message_queue.put((self.name, "Product approved"))
            time.sleep(1)
