# coding_agent/cli.py
from dotenv import load_dotenv
import os
import sys
from google import genai
from google.genai.types import Content, Part
from .config import gemini_config
from .functions.call_function import call_function

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


def run(prompt: str, verbose: bool = False, work_dir_path: str | None = None):
    """Run the agent given a prompt (core logic extracted for easier testing)."""
    load_dotenv()
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        print("Missing GEMINI_API_KEY")
        sys.exit(1)

    if work_dir_path is None:
        work_dir_path = os.getcwd()

    client = genai.Client(api_key=API_KEY)
    messages = [Content(parts=[Part(text=prompt)], role="user")]

    max_iters = 20
    for step in range(max_iters):
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=gemini_config,
        )

        if response is None:
            print("Response is None")
            break

        if verbose and getattr(response, "usage_metadata", None):
            print(f"[iter {step}] prompt_tokens={response.usage_metadata.prompt_token_count} "
                  f"resp_tokens={response.usage_metadata.candidates_token_count}")

        if response.candidates:
            for cand in response.candidates:
                if cand and cand.content:
                    messages.append(cand.content)

        if getattr(response, "function_calls", None):
            tool_parts = []
            for fc in response.function_calls:
                part = call_function(fc.name, fc.args, work_dir_path, verbose)
                tool_parts.append(part)

            messages.append(Content(role="tool", parts=tool_parts))

            # small debug
            for p in tool_parts:
                fr = getattr(p, "function_response", None)
                if fr:
                    resp = fr.response
                    if isinstance(resp, dict) and "Result" in resp:
                        print("Function Result:", resp["Result"])
                    elif isinstance(resp, dict) and "error" in resp:
                        print("Function Error:", resp["error"])
            continue

        final_text = _extract_text(response)
        if final_text:
            print("Response Text:", final_text)
            messages.append(Content(parts=[Part(text=final_text)], role="assistant"))
        break


def main(argv=None):
    """Console entry point."""
    import argparse
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(prog="coding-agent", description="Run the Coding Agent")
    parser.add_argument("prompt", help="Prompt to send to the model")
    parser.add_argument("--work-dir", "-w", default=None, help="Working directory for tools")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args(argv)
    run(args.prompt, verbose=args.verbose, work_dir_path=args.work_dir)
