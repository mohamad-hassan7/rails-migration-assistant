# Simple CLI to run pipeline steps
from src.model.local_llm import LocalLLM

def main():
    llm = LocalLLM()
    print(llm.generate("Hello from demo agent"))

if __name__ == '__main__':
    main()
