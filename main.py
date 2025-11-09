from dotenv import load_dotenv
import os
from google import genai
import sys
from google.genai.types import Content, Part
from coding_agent.config import gemini_config
from coding_agent.functions.call_function import call_function


def _extract_text(response) -> str:
    """Return best-effort plain text from a response."""
    if getattr(response, "text", None):
        return response.text
    pieces = []
    for cand in (response.candidates or []):
        if not cand or not cand.content:
            continue
        for part in (cand.content.parts or []):
            if getattr(part, "text", None):
                pieces.append(part.text)
    return "\n".join(pieces).strip()


def main(work_dir_path):
    load_dotenv()
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        print("Missing GEMINI_API_KEY")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Please provide a prompt as a command-line argument.")
        sys.exit(1)

    verbose = False
    if len(sys.argv) > 2 and sys.argv[2] == "--verbose":
        verbose = True

    client = genai.Client(api_key=API_KEY)
    prompt = sys.argv[1]

    # Conversation state
    messages = [Content(parts=[Part(text=prompt)], role="user")]

    max_iters = 20
    for step in range(max_iters):
        # Always call with the full history
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=gemini_config,
        )

        if response is None:
            print("Response is None")
            break

        if verbose and response.usage_metadata:
            print(f"[iter {step}] prompt_tokens={response.usage_metadata.prompt_token_count} "
                  f"resp_tokens={response.usage_metadata.candidates_token_count}")

        # Keep the model's latest message (incl. any function_call parts) in the history
        if response.candidates:
            for cand in response.candidates:
                if cand and cand.content:
                    messages.append(cand.content)

        # If the model asked for function(s), execute them, append tool response(s), and loop
        if response.function_calls:
            tool_parts = []
            for fc in response.function_calls:
                part = call_function(fc.name, fc.args, work_dir_path, verbose)
                tool_parts.append(part)

            # ✅ Only one tool message per turn
            messages.append(Content(role="tool", parts=tool_parts))

            # Debug print
            for p in tool_parts:
                fr = p.function_response.response
                if "Result" in fr:
                    print("Function Result:", fr["Result"])
                elif "error" in fr:
                    print("Function Error:", fr["error"])
            continue
        
        # No function calls => final assistant text; print and exit
        final_text = _extract_text(response)
        if final_text:
            print("Response Text:", final_text)
            messages.append(Content(parts=[Part(text=final_text)], role="assistant"))
        break


if __name__ == "__main__":
    work_dir_path = os.getcwd()
    main(work_dir_path)
