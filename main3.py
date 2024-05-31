import chromadb
from dotenv import load_dotenv
import os
import ollama


# load_dotenv('.env.local')

# storage_path = os.getenv('STORAGE_PATH')
# if storage_path is None:
#     raise ValueError('STORAGE_PATH environment variable is not set')

client = chromadb.PersistentClient(path="./cdb")
client.delete_collection("test")
collection = client.get_or_create_collection(name="test")


collection.add(
    documents=[
"""
Machine learning (ML) is a field of study in artificial intelligence concerned with the development and study of statistical algorithms that can learn from data and generalize to unseen data, and thus perform tasks without explicit instructions.[1] Recently, artificial neural networks have been able to surpass many previous approaches in performance.[2][3]

ML finds application in many fields, including natural language processing, computer vision, speech recognition, email filtering, agriculture, and medicine.[4][5] When applied to business problems, it is known under the name predictive analytics. Although not all machine learning is statistically based, computational statistics is an important source of the field's methods.

The mathematical foundations of ML are provided by mathematical optimization (mathematical programming) methods. Data mining is a related (parallel) field of study, focusing on exploratory data analysis (EDA) through unsupervised learning.[7][8]

""",
"""
Data science is an interdisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge and insights from structured and unstructured data. In simpler terms, data science is about obtaining, processing, and analyzing data to gain insights for many purposes.

""",
"""
Policy gradient methods(opens in a new window) are fundamental to recent breakthroughs in using deep neural networks for control, from video games(opens in a new window), to 3D locomotion(opens in a new window), to Go(opens in a new window). But getting good results via policy gradient methods is challenging because they are sensitive to the choice of stepsize — too small, and progress is hopelessly slow; too large and the signal is overwhelmed by the noise, or one might see catastrophic drops in performance. They also often have very poor sample efficiency, taking millions (or billions) of timesteps to learn simple tasks.

Researchers have sought to eliminate these flaws with approaches like TRPO(opens in a new window) and ACER(opens in a new window), by constraining or otherwise optimizing the size of a policy update. These methods have their own trade-offs—ACER is far more complicated than PPO, requiring the addition of code for off-policy corrections and a replay buffer, while only doing marginally better than PPO on the Atari benchmark; TRPO—though useful for continuous control tasks—isn’t easily compatible with algorithms that share parameters between a policy and value function or auxiliary losses, like those used to solve problems in Atari and other domains where the visual input is significant."""
],
metadatas=[
{"source": "test1"},
{"source": "test2"},
{"source": "test3"}
],
ids=["id1", "id2", "id3"]
)
print(collection.query(query_texts=[
        "What is ai?"
    ], n_results=1))
# stream=ollama.generate('llama3', "Why is the sky blue?", stream=True)
# for i in stream:
#     pass
#     print(i["response"], end="")