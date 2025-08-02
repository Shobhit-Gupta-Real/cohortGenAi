import tiktoken
enc = tiktoken.encoding_for_model("gpt-4o")

text = "Hello, I am shobhit"
token = enc.encode(text)
print(token)