from pathlib import Path
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load API key & set up configuration for Azure
load_dotenv()


API_KEY = os.getenv("OCP_APIM_SUBSCRIPTION_KEY","").strip()
assert API_KEY, "ERROR: Azure OpenAI Key is missing"

RESOURCE_ENDPOINT = os.getenv("OPENAI_API_BASE_ENDPOINT","").strip()
assert RESOURCE_ENDPOINT, "ERROR: Azure OpenAI Endpoint is missing"
RESOURCE_ENDPOINT = f"https://az-apim-svc-westeurope.azure-api.net"
client = AzureOpenAI(api_key=API_KEY, azure_endpoint=RESOURCE_ENDPOINT, api_version="2023-05-15"
                       ,default_headers={"Ocp-Apim-Subscription-Key": API_KEY})

# Patterns of the sourcefiles to look after
f_pat = "*.java"
# Location of the root folder to scan recursively
root_path = ".//test_code_dir//"
# path of the result
result_path = ".//output//result.txt"

# Set a context for the chatbot, how is the chatbot supposed to behave
messages_origin = [
    {
        "role": "system",
        "content": "You are a professional software developer with a lot of experience who answers are short and very concise.",
    },
    {
        "role": "system",
        "content": "Please summarize the following sourcecode briefly in three to 8 sentences each. Also note what could be improved here or if anything can be improved",
    },
]


if __name__ == "__main__":
    print("Start scan")

    # create a new chat to limit token size
    messages = messages_origin.copy()

    results = []

    for p in Path(root_path).rglob(f_pat):
        with open(p, "r") as f:
            f_string = f.read()
            messages.append({"role": "user", "content": f_string})
            chat = client.chat.completions.create(
                model="gpt-35-turbo-4k-0613", messages=messages
            )
            reply = chat.choices[0].message.content
            # Split sentences at the end to provide better readability
            reply_split = reply.replace(". ", ".\n")
            results.append(
                {
                    "filepath": p,
                    "filename": p.name,
                    "summary": reply,
                    "summary_split": reply_split,
                }
            )
        print(p)

    print("Scan sucessful")

    print("Writing results")
    with open(result_path, "w") as f:
        for r in results:
            f.write(str(r["filename"]) + ":\n")
            f.write("Path: " + str(r["filepath"]) + ":\n")
            f.write(r["summary_split"] + "\n\n")
    print("results written to: " + result_path)
