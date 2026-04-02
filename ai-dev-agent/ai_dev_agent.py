import os
from crewai import Agent, Task, Crew

# ---------------- FILE WRITE FUNCTION ----------------
def write_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return "Created " + path


# ---------------- FILE PARSER ----------------
def create_files_from_output(output):
    lines = output.split("\n")
    current_file = None
    code_lines = []

    for line in lines:
        if line.startswith("FILE:"):
            if current_file is not None:
                write_file(current_file, "\n".join(code_lines))
                code_lines = []

            current_file = line.replace("FILE:", "").strip()

        elif line.startswith("CODE:"):
            continue

        else:
            code_lines.append(line)

    if current_file is not None:
        write_file(current_file, "\n".join(code_lines))


# ---------------- AGENTS ----------------
architect = Agent(
    role="Architect",
    goal="Design full-stack applications",
    backstory="You are a senior software architect with deep knowledge of scalable systems.",
    llm="ollama/deepseek-coder"
)

developer = Agent(
    role="Developer",
    goal="Write complete applications",
    backstory="You are an expert full-stack developer skilled in all modern technologies.",
    llm="ollama/deepseek-coder"
)


# ---------------- MAIN FUNCTION ----------------
def run_project(user_input):
    task = Task(
        description=f"""
        You are an AI software engineer.

        CRITICAL RULES (STRICT):

        1. NEVER say "too long"
        2. NEVER skip code
        3. NEVER summarize
        4. ALWAYS generate FULL code

        5. Output ONLY in this format:

        FILE: backend/server.js
        CODE:
        <complete code>

        FILE: backend/package.json
        CODE:
        <complete code>

        FILE: frontend/src/App.js
        CODE:
        <complete code>

        6. Generate COMPLETE project (no missing parts)

        7. If output is large, CONTINUE writing until done

        PROJECT:
        {user_input}
        """,
        expected_output="Full project code with file structure and code blocks",
        agent=developer
    )

    crew = Crew(
        agents=[architect, developer],
        tasks=[task]
    )

    result = crew.kickoff()
    result_text = str(result)

    print(result_text)

    create_files_from_output(result_text)

    print("\n✅ Project created successfully!")


# ---------------- RUN ----------------
if __name__ == "__main__":
    user_input = input("Enter your project idea: ")
    run_project(user_input)